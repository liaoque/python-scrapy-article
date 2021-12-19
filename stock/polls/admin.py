from django.contrib import admin

from .controller.question_admin import QuestionAdmin
from .model.question import Question


# Register your models here.



admin.site.register(Question, QuestionAdmin)
# admin.site.register(Choice)
