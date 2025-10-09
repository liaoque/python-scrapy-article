from uuid import uuid4
from pathlib import Path
import websockets
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View

from dvadmin.lh.utils.xunfei.tts import build_auth_url, infer_format, sample_rate_from_auf
import os, json, base64, asyncio, re

SAVE_DIR = Path(os.getenv("SAVE_DIR", "media/public"))
SAVE_DIR.mkdir(parents=True, exist_ok=True)

WS_HOSTURL = "wss://tts-api.xfyun.cn/v2/tts"
TIMEOUT_SECONDS = int(os.getenv("UPSTREAM_TIMEOUT", "60"))


@method_decorator(csrf_exempt, name='dispatch')
class XunFeiView(View):

    def get(self, request, *args, **kwargs):
        return JsonResponse({
            "code": 2000,
            "msg": "success",
        })

    def post(self, request, *args, **kwargs):
        try:
            body = json.loads(request.body.decode("utf-8"))
        except Exception:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        text = body.get("text")
        XFYUN_API_KEY = body.get("XFYUN_API_KEY")
        XFYUN_API_SECRET = body.get("XFYUN_API_SECRET")
        XFYUN_APP_ID = body.get("XFYUN_APP_ID")
        vcn = body.get("vcn")
        if not text or not vcn:
            return JsonResponse({"error": "Missing required fields: text, vcn"}, status=400)

        aue = body.get("aue", "lame")
        sfl = int(body.get("sfl", 1))
        auf = body.get("auf", "audio/L16;rate=16000")
        speed = int(body.get("speed", 50))
        volume = int(body.get("volume", 50))
        pitch = int(body.get("pitch", 50))
        bgs = int(body.get("bgs", 0))
        tte = body.get("tte", "UTF8")
        reg = str(body.get("reg", "0"))
        rdn = str(body.get("rdn", "0"))
        return_type = body.get("return", "base64")

        ws_url = build_auth_url(WS_HOSTURL, XFYUN_API_KEY, XFYUN_API_SECRET)
        payload = {
            "common": {"app_id": XFYUN_APP_ID},
            "business": {
                "aue": aue, "sfl": sfl, "auf": auf, "vcn": vcn,
                "speed": speed, "volume": volume, "pitch": pitch, "bgs": bgs,
                "tte": tte, "reg": reg, "rdn": rdn
            },
            "data": {
                "status": 2,
                "text": base64.b64encode(text.encode("utf-8")).decode("utf-8")
            }
        }

        async def call_upstream():
            sid = ""
            done = False
            # 直接写 bytes（而不是攒 base64 字符串）
            chunks_bytes = []

            async with websockets.connect(ws_url, max_size=None) as ws:
                await ws.send(json.dumps(payload))
                async for raw in ws:
                    msg = json.loads(raw)
                    code = msg.get("code")
                    message = msg.get("message")
                    if not sid and "sid" in msg:
                        sid = msg["sid"]
                    if code != 0:
                        raise RuntimeError(json.dumps({"error": message or "XFYun error", "code": code, "sid": sid}))

                    data = msg.get("data") or {}
                    b64 = data.get("audio")
                    if b64:
                        # 和 demo 一样：每帧立刻解码成二进制
                        # 注意：如果含有 '-'/'_'，用 urlsafe_b64decode 更稳妥
                        decoder = base64.urlsafe_b64decode if ("-" in b64 or "_" in b64) else base64.b64decode
                        try:
                            # 去掉任何可能的空白后再解码
                            b64 = "".join(b64.split())
                            # 补齐 padding
                            padding = (-len(b64)) % 4
                            if padding:
                                b64 += "=" * padding
                            chunk = decoder(b64)
                        except Exception as e:
                            raise RuntimeError(json.dumps({"error": f"decode error: {e}", "sid": sid}))
                        chunks_bytes.append(chunk)

                    if data.get("status") == 2:
                        done = True
                        break

            if not done:
                raise RuntimeError(json.dumps({"error": "Upstream closed before final status=2", "sid": sid}))
            # 返回纯二进制拼接后的 bytes
            return b"".join(chunks_bytes), sid

        try:
            audio_bytes, sid = asyncio.run(asyncio.wait_for(call_upstream(), timeout=TIMEOUT_SECONDS))
        except asyncio.TimeoutError:
            return JsonResponse({"error": "Upstream timeout"}, status=504)
        except RuntimeError as rer:
            # 上游错误直接透传
            try:
                detail = json.loads(str(rer))
            except Exception:
                detail = {"error": str(rer)}
            return JsonResponse(detail, status=500)
        except Exception as e:
            return JsonResponse({"error": str(e)}, status=500)

        fmt = infer_format(aue)
        sr = sample_rate_from_auf(auf)

        if return_type == "url":
            file_id = str(uuid4())
            filename = f"{file_id}.{fmt}"  # 避免非 ASCII 文件名
            filepath = SAVE_DIR / filename


            with open(filepath, "wb") as f:
                f.write(audio_bytes)
                f.flush()
                os.fsync(f.fileno())

            url = f"/{filename}"
            return JsonResponse({"format": fmt, "sample_rate": sr, "audio_url": url, "sid": sid})

        audio_b64 = base64.b64encode(audio_bytes).decode("ascii")
        return JsonResponse({"format": fmt, "sample_rate": sr, "audio_base64": audio_b64, "sid": sid})
