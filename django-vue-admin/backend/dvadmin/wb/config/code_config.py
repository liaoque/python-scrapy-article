class CodeConfig:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CodeConfig, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def getCodeConfig(self):
        return {
            "chuang_ye_set": 18.99 ,
            "zhu_set": 9.5 ,
            "10cm": 50,
            "20cm": 70,
            "fd": 0,
            "yd": 0,
            "lian_xu_duo_ri_yi_zi_ban": [],
        }