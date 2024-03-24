from django.shortcuts import render, get_object_or_404

# Create your views here.
from django.http import HttpResponse, Http404, HttpResponseRedirect, JsonResponse
from django.template import loader
from django.urls import reverse
from django.utils.html import format_html
from django.views import generic
from datetime import datetime, timedelta

# from ..model.shares import Shares
from ..model.shares_name import SharesName
from ..model.shares_date import SharesDate


class SharesView(generic.DetailView):
    template_name = 'shares/detail.html'
    model = SharesName


# def index(request):
#     latest_question_list = SharesName.objects.order_by('-id')[:5]
#     context = {'latest_question_list': latest_question_list}
#     return render(request, 'polls/index.html', context)

# def detail(request, question_id):
#     question = get_object_or_404(Question, pk=question_id)
#     return render(request, 'polls/detail.html', {'question': question})
#
# def results(request, question_id):
#     response = "You're looking at the results of question %s."
#     return HttpResponse(response % question_id)
#
# def vote(request, question_id):
#     return HttpResponse("You're voting on question %s." % question_id)


def shares_date(request, date_today):
    dates = SharesDate.objects.filter(date_as__lte=datetime.strptime(date_today, '%Y%m%d')).order_by('-date_as')[:3]
    tomorrow = SharesDate.objects.filter(date_as__gt=datetime.strptime(date_today, '%Y%m%d')).order_by('date_as')

    if len(tomorrow) == 1:
        tomorrow = tomorrow[0].date_as
        after_tomorrow = tomorrow + timedelta(days=1)
        tomorrow = [
            SharesDate(date_as=tomorrow),
            SharesDate(date_as=after_tomorrow)
        ]
    elif len(tomorrow) < 2:
        now = dates[0].date_as
        tomorrow = now + timedelta(days=1)
        after_tomorrow = now + timedelta(days=2)
        tomorrow = [
            SharesDate(date_as=tomorrow),
            SharesDate(date_as=after_tomorrow)
        ]

    response = JsonResponse({
        "today": dates[0].date_as,
        "yesterday": dates[1].date_as,
        "before_yesterday": dates[2].date_as,
        "tomorrow": tomorrow[0].date_as,
        "after_tomorrow": tomorrow[1].date_as,
    })
    response["Access-Control-Allow-Origin"] = "*"
    # 如果需要，可以添加更多CORS相关的头信息，例如：
    # response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    # response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response
    # return HttpResponse("You're voting on question %s." % question_id)


def shares_date_last(request, date_today):
    dates = SharesDate.objects.filter(date_as__lte=datetime.strptime(date_today, '%Y%m%d')).order_by('-date_as')[:10]

    response = JsonResponse({
        "dates": [ item.date_as for item in dates]
    })
    response["Access-Control-Allow-Origin"] = "*"
    # 如果需要，可以添加更多CORS相关的头信息，例如：
    # response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
    # response["Access-Control-Allow-Headers"] = "X-Requested-With, Content-Type"
    return response
