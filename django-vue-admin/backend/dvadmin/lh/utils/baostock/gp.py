import baostock as bs

def GetGjList (code, start, end, frequency) :
    prefix = '0.'
    code3 = code[0:3]
    if code3 == '688':
        prefix = 'sh.'
    elif (code3 == '000'):
        prefix = 'sz.'
    elif (code3 == '002'):
        prefix = 'sz.'
    elif (code3 == '300'):
        prefix = 'sz.'
    elif (code3[0:2] == '60'):
        prefix = 'sh.'
    lg = bs.login()
    rs = bs.query_history_k_data_plus(prefix +code,
                                      "date,time,code,open,high,low,close,volume,amount,adjustflag",
                                      start_date=start, end_date=end,
                                      frequency=frequency, adjustflag="3")
    data_list = []
    while (rs.error_code == '0') & rs.next():
        # 获取一条记录，将记录合并在一起
        data_list.append(rs.get_row_data())

    return data_list