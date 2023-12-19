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
            "fd": 1,
            "yd": 0,
            "lian_ban_code_black": [], # 连扳天数黑名单 设置值 H33
        }
