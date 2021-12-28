from django.contrib import admin

from .controller.question_admin import QuestionAdmin
from .controller.shares import SharesNameAdmin
from .model.question import Question
from .model.shares_name import SharesName
from .model.shares_kdj_compute import SharesKdjCompute
from .model.shares_kdj_compute_detail import SharesKdjComputeDetail


# Register your models here.



admin.site.register(Question, QuestionAdmin)
admin.site.register(SharesName, SharesNameAdmin)
# admin.site.register(Choice)
