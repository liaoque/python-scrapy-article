import requests
import random
import time


_headers = {
    "HOST": "push2his.eastmoney.com",
    'User-Agent': "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
}


class TongHuaShunId:

    def __init__(self, t, userAgent):
        self.n = [0] * 18
        self.n[0] = 4228805416 #self.random()
        self.n[1] = 1720486505 #int(t)
        self.n[3] =90299976# self.strHash(userAgent) # Jn.strhash(navigator.userAgent),
        self.n[4] = 1  # 假设平台为1 tt.getPlatform(),
        self.n[5] = 10  # 假设浏览器索引为10 tt.getBrowserIndex(),
        self.n[6] = 5  # 假设插件数量为0  tt.getPluginNum()
        self.n[15] = 0
        self.n[16] = 1
        self.n[17] = 3
        self.n[13] = 3748
        self.n[2] = 1720491475 #self.timeNow()

    def encode(self, n):
        r = self._hash(n)
        n = self._encode(n, [3, r])
        return self._base64(n)

    def _encode(self, n, o):
        a = 0
        i = 2
        u = o[1]
        while a < len(n):
            o.append(n[a] ^ (u & 255))
            u = ~(u * 131)
            a += 1
            i += 1
        return o

    def strHash(self, userAgent):
        c = 0
        for v in userAgent:
            c = (c << 5) - c + ord(v)
            c &= 0xFFFFFFFF  # 保持 c 为32位无符号整数
        return c

    def _hash(self, n):
        e = 0
        for i in n:
            e = (e << 5) - e + i
        return e & 255

    def _base64(self, n):
        m = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789-_"
        f = []
        for i in range(0, len(n), 3):
            l = (n[i] << 16) | (n[i + 1] << 8) | n[i + 2]
            f.append(m[(l >> 18) & 63])
            f.append(m[(l >> 12) & 63])
            f.append(m[(l >> 6) & 63])
            f.append(m[l & 63])
        return ''.join(f)

    def to_buff(self, n):
        u = [4, 4, 4, 4, 1, 1, 1, 3, 2, 2, 2, 2, 2, 2, 2, 4, 2, 1]
        c = [0] * 43
        s = -1
        for v in range(len(u)):
            l = n[v]
            p = u[v]
            s += p
            d = s
            while p != 0:
                c[d] = (l & 255)
                l >>= 8
                p -= 1
                d -= 1
        return c

    def random(self):
        return int(random.random() * 4294967295)

    def timeNow(self):
        try:
            time_now = int(time.time() * 1000)  # 获取当前时间的时间戳（毫秒）
            result = time_now // int("1111101000", 2)  # 使用整数除法
            return result
        except Exception:
            time_now = int(time.time() * 1000)  # 获取当前时间的时间戳（毫秒）
            result = time_now // int("1000", 10)  # 使用整数除法
            return result

    def __str__(self):
        n = self.to_buff(self.n)
        return self.encode(n)

def getTongHuaShun(url, cookies=None, headers=None):
    if headers == None:
        headers = {}
    headers["User-Agent"] = _headers["User-Agent"]
    headers["HOST"] = "q.10jqka.com.cn"
    # headers["Referer"] = url
    #
    # "https://s.thsi.cn/js/chameleon/chameleon.min.1720490.js"
    resp = getDF("http://s.thsi.cn/js/chameleon/chameleon.min." + str(time.time()+10000)[0:7] + ".js")
    # resp = getDF("https://s.thsi.cn/js/chameleon/chameleon.min.1720490.js")
    resp = resp[22:32]
    if cookies == None:
        cookies = {}
    cookies["v"] = TongHuaShunId(resp, headers["User-Agent"]).__str__()
    cookies["vvv"] = "1"
    response = requests.get(url, cookies=cookies, headers=headers)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("无法获取股票信息"+url)

def getDF(url, cookie=None, headers=None):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    else:
        raise Exception("无法获取股票信息")

def postDF(url, data, cookie=None, headers=None):
    pass


if __name__ == "__main__":

    print(str(time.time()+10000)[0:7])
    url = f"http://q.10jqka.com.cn/gn/detail/field/199112/order/desc/size/1000/page/1/ajax/1/code/" + "301558"
    html = getTongHuaShun(url, headers={
        "HOST": "q.10jqka.com.cn",
    })