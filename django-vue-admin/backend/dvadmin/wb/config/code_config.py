import json
import os

concept = [
    "分拆上市意愿", "人民币贬值受益", "富时罗素概念", "富时罗素概念股", "标普道琼斯A股", "沪股通", "深股通",
    "融资融券", "转融券标的", "再融资", "送转填权", "股权转让", "并购重组", "超跌", "MSCI概念", "一季报增长",
    "一季报预增", "业绩增长", "年报增长", "超跌", "央企国企改革", "地方国企改革", "三季报增长", "半年报预增",
    "中报增长", "山东国企改革", "上海国企改革", "江苏国企改革", "深圳国企改革", "重庆国企改革", "广东国企改革",
    "北京国企改革", "天津国企改革", "甘肃国企改革", "河南国企改革", "山西国企改革", "浙江国企改革", "珠海国企改革",
    "四川国企改革", "上海", "深圳", "浙江", "湖南", "武汉", "海南", "科创板", "年报预增", "三季报预增", "证金持股",
    "行业龙头", "参股新三板", "国企改革", "同花顺漂亮100"
]


class CodeConfig:
    _instance = None
    _config = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(CodeConfig, cls).__new__(cls, *args, **kwargs)
        return cls._instance

    def getCodeConfig(self):
        if self._instance._config:
            return self._instance._config

        configfile = os.path.abspath(os.path.join(os.path.dirname(__file__), 'data.json'))
        with open(configfile, "r+") as outfile:
            try:
                self._instance._config = json.load(outfile)
            except json.JSONDecodeError:
                self._instance._config = {
                    "chuang_ye_set": 18.99,
                    "zhu_set": 9.5,
                    "10cm": 50,
                    "20cm": 70,
                    "fd": 1,
                    "yd": 0,
                    "gvgn": concept,  # 过滤概念
                    "lian_ban_code_black": [],  # 连扳天数黑名单 设置值 H3
                }
        return self._instance._config

    def setFd(self, fd):
        self._instance._config["fd"] = fd

    def setYd(self, yd):
        self._instance._config["yd"] = yd