class CodeConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CodeConfig, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def getCodeConfig(self):
        return {
            "chuang_ye_set": 18.99 / 100,
            "zhu_set": 9.5 / 100,
            "10cm": 50,
            "20cm": 70,
            "fd": 1,
            "yd": 1,
            "lian_xu_duo_ri_yi_zi_ban": [],
        }
