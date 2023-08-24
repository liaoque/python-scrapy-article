from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from wb.settings import DATABASES
import time
from pymongo import MongoClient
import polls.core.init_data 
import polls.core.streak_rise 

def index(request):

    client = MongoClient(DATABASES['wb']['CLIENT']['host'], DATABASES['wb']['CLIENT']['port'])  # 默认连接到 localhost 和端口 27017
    db = client['wb']         # 选择你的数据库
    current_timestamp = time.time()
    current_time = time.strftime("%Y%m%d", time.localtime())
    print('d'+current_time)
    table = db['d'+current_time]         # 选择你的数据库
    table1 = list(table.find({}, {"Table1FromJSON":1}))
    
    data = init_data.step1(table1)
    
    table1 = list(table.find({}, {"JinCengZhangTing":1}))
    data = init_data.step2(table1, data)

    table1 = list(table.find({}, {"ChuangBaiRiXinGao":1}))
    data = init_data.step3(table1, data)
    
    table1 = list(table.find({}, {"YiZiBan":1}))
    data = init_data.step4(table1, data)
    
    table1 = list(table.find({}, {"ZhuChuangZhangTing":1}))
    data = init_data.step5(table1, data)
    
    
    lianzhanggupiao = streak_rise.step1(table1, data)
    
    table1 = list(table.find({}, {"YiZiDieTing":1}))
    dietinggupiao = streak_rise.step2(table1, data)
    
    zhabangupiao = streak_rise.step3(data)
    
    client.close()

    context = {
        'latest_question_list': [],
    }
    return render(request, 'polls/index.html', context)
    
    
def detail(request, question_id):
    return HttpResponse("You're looking at question %s." % question_id)

def results(request, question_id):
    response = "You're looking at the results of question %s."
    return HttpResponse(response % question_id)

def vote(request, question_id):
    return HttpResponse("You're voting on question %s." % question_id)