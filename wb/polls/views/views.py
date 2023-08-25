from django.shortcuts import render

# Create your views here.
from django.http import HttpResponse

from wb.settings import DATABASES
import time
from pymongo import MongoClient
import polls.core.init_data 
import polls.core.streak_rise 
import polls.core.suo_shu_gai_nian 
import polls.core.bu_zhang 

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
    
    
    #取连涨股票
    lianzhanggupiao = streak_rise.step1(table1, data)
    
    #取跌停股票
    table1 = list(table.find({}, {"YiZiDieTing":1}))
    dietinggupiao = streak_rise.step2(table1, data)
    
    # 取炸板股票
    zhabangupiao = streak_rise.step3(data)
    
    # 取创百日新高股票
    chuangbairixingao = streak_rise.step4(data)
    
    # 取一字板股票
    yizibangupiao = streak_rise.step5(data)
    
    # 取首板股票
    shoubangupiao = streak_rise.step5_1(data)
    
    # 生成连涨概念
    lianzhanggainian = streak_rise.step6(lianzhanggupiao)
    
    # 生成跌停概念
    dietinggainian = streak_rise.step7(dietinggupiao)
    
    # 生成炸板概念
    zhabangainian = streak_rise.step8(zhabangupiao)
    
    #生成创百日新高概念
    chuangbairixingaogainnian = streak_rise.step9(chuangbairixingao)
    
    #生成一字板概念
    yizibangainian = streak_rise.step10(yizibangupiao)
    
    #生成首板概念
    shoubangainian = streak_rise.step11(shoubangupiao)
    
    #取涨停原因
    lianzhanggupiao = streak_rise.step12(lianzhanggupiao, lianzhanggainian)
    
    #取跌停原因
    dietinggupiao = streak_rise.step13(dietinggupiao, dietinggainian)

    #取炸板原因
    zhabangupiao = streak_rise.step14(zhabangupiao, zhabangainian)

    #取创百日新高原因
    chuangbairixingao = streak_rise.step15(chuangbairixingao, chuangbairixingaogainnian)
    
    #取一字板原因
    yizibangupiao = streak_rise.step16(yizibangupiao, yizibangainian)

    #取首板原因
    shoubangupiao = streak_rise.step17(shoubangupiao, shoubangainian)

    #排列涨停原因
    lian_zhang_sort = streak_rise.step18(lianzhanggupiao, lianzhanggainian)
    
    #排列跌停原因
    die_ting_sort = streak_rise.step19(dietinggupiao, dietinggainian)
    
    #排列炸板原因
    zha_ban_sort = streak_rise.step20(zhabangupiao, zhabangainian)
    
    #排列创百日新高原因
    chuang_bai_ri_xin_gao_sort = streak_rise.step21(chuangbairixingao, chuangbairixingaogainnian)
    
    #排列一字板原因
    yi_zi_ban_sort = streak_rise.step22(yizibangupiao, yizibangainian)
    
    #排列首板原因
    shou_ban_sort = streak_rise.step23(shoubangupiao, shoubangainian)
    
    #排列竞涨停竞跌停
    jing_jia_sort = streak_rise.step24(yizibangupiao, dietinggupiao, jin_jia_yeastday)
    
    #排列5日涨跌幅
    day_5_sort = streak_rise.step25(data)
    
    """
    table1 = list(table.find({}, {"Table":1}))
    data2 = suo_shu_gai_nian.suo_shu_gai_nian(table1, {
        chuang_ye_set:0,
        zhu_ban_set:0,
    })
    """
    
    bu_zhang = bu_zhang.bu_zhang(data, yesterday, yester_yesterday)
    
    
    
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