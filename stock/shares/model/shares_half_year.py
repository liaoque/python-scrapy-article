from django.db import models
from .shares_name import SharesName
from datetime import datetime


# Create your models here.


class SharesHalfYear(models.Model):
    code = models.ForeignKey(SharesName, on_delete=models.CASCADE)
    name = models.CharField(max_length=30)
    p_start = models.IntegerField(default=0)
    p_end = models.IntegerField(default=0)
    p_year = models.IntegerField(default=0)
    p_year_half = models.IntegerField(default=0, help_text="1 前半年，2 后半年")

    class Meta:
        db_table = "mc_shares_half_year"
        # abstract = True

    def __str__(self):
        return self.name + ":" + self.p_year + ":" + self.p_year_half + ":最大-" + self.p_start + ":最小-" + self.p_end

    def getCodeIdList(self):
        return [
            [
                "000915", "002872", "002898", "002908", "002910", "002932", "002956", "300260", "300373", "300404",
                "300505", "300518", "300519", "300579", "300596", "300633", "300653", "300661", "300671", "300755",
                "300759", "300760", "300763", "300767", "300768", "300769", "430198", "600085", "600519", "600885",
                "601069", "601155", "601689", "601838", "603259", "603289", "603345", "603477", "603517", "603538",
                "603605", "603650", "603697", "603722", "603733", "603826", "603868", "603896", "603912", "603915",
                "603991"
            ],
            [
                "000333", "001965", "002025", "002043", "002098", "002105", "002182", "002236", "002262", "002311",
                "002531", "002556", "002637", "002724", "002726", "002730", "002732", "002733", "002738", "002756",
                "002758", "002766", "002785", "002810", "002812", "002878", "002884", "002889", "002906", "002911",
                "002913", "002916", "002920", "002926", "002931", "002935", "002939", "300072", "300087", "300179",
                "300203", "300214", "300224", "300231", "300240", "300251", "300265", "300395", "300401", "300406",
                "300438", "300470", "300483", "300487", "300566", "300590", "300596", "300602", "300613", "300618",
                "300619", "300620", "300679", "300680", "300690", "300693", "300697", "300699", "300707", "300717",
                "300718", "300721", "300724", "300726", "300748", "300752", "300760", "430489", "600276", "600449",
                "600903", "600917", "600933", "601166", "601766", "601877", "603008", "603011", "603018", "603033",
                "603085", "603105", "603110", "603129", "603136", "603192", "603222", "603228", "603297", "603301",
                "603305", "603308", "603321", "603338", "603348", "603488", "603505", "603583", "603599", "603605",
                "603606", "603612", "603659", "603693", "603703", "603712", "603806", "603816", "603833", "603899"
            ]
        ]
