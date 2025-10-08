import os
import base64
import hmac
import hashlib
from datetime import datetime, timezone
from urllib.parse import urlparse, urlencode

XFYUN_APP_ID = os.getenv("XFYUN_APP_ID")
XFYUN_API_KEY = os.getenv("XFYUN_API_KEY")
XFYUN_API_SECRET = os.getenv("XFYUN_API_SECRET")

def rfc1123_now_utc() -> str:
    return datetime.now(timezone.utc).strftime("%a, %d %b %Y %H:%M:%S GMT")

def build_auth_url(hosturl: str) -> str:
    """构建科大讯飞鉴权 URL（authorization/date/host 三参）"""
    if not (XFYUN_APP_ID and XFYUN_API_KEY and XFYUN_API_SECRET):
        raise RuntimeError("Missing XFYUN credentials in env")

    u = urlparse(hosturl)
    host = u.netloc
    path = u.path
    date = rfc1123_now_utc()

    sign_origin = f"host: {host}\n" \
                  f"date: {date}\n" \
                  f"GET {path} HTTP/1.1"
    sha = hmac.new(
        XFYUN_API_SECRET.encode("utf-8"),
        sign_origin.encode("utf-8"),
        digestmod=hashlib.sha256
    ).digest()
    signature = base64.b64encode(sha).decode("utf-8")

    auth_origin = (
        f"api_key=\"{XFYUN_API_KEY}\", algorithm=\"hmac-sha256\", "
        f"headers=\"host date request-line\", signature=\"{signature}\""
    )
    authorization = base64.b64encode(auth_origin.encode("utf-8")).decode("utf-8")

    qs = urlencode({
        "authorization": authorization,
        "date": date,
        "host": host
    })
    return f"{hosturl}?{qs}"

def infer_format(aue: str) -> str:
    aue = (aue or "").lower()
    if aue == "lame":
        return "mp3"
    if aue == "raw":
        return "pcm"
    if aue.startswith("opus"):
        return "opus"
    if aue.startswith("speex"):
        return "speex"
    return "bin"

def sample_rate_from_auf(auf: str) -> int:
    return 16000 if "16000" in (auf or "") else 8000
