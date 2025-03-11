import { request } from '@/api/service'

/**
 * 国债利率
 * @returns {*}
 * @constructor
 */
export function GetGzRate () {
  return fetch('https://datacenter-web.eastmoney.com/api/data/v1/get?callback=&reportName=RPTA_WEB_TREASURYYIELD&columns=ALL&sortColumns=SOLAR_DATE&sortTypes=-1&token=&pageNumber=1&pageSize=1&_=' )
}

export function GetEtfQqListDate (code) {
  const url = 'https://push2.eastmoney.com/api/qt/stock/get?cb=&ut=&mspt=1&_='
  // =&secid=1.510300&exti=202504
  return request({
    url: url,
    method: 'get',
    params: { secid: code }
  })
}


export function GetEtfQqList (code, date) {
  const url = 'https://push2.eastmoney.com/api/qt/slist/get?np=1&fltt=1&invt=2&spt=9&cb&fields=f12%2Cf13%2Cf14%2Cf1%2Cf2%2Cf4%2Cf334%2Cf330%2Cf3%2Cf152%2Cf108%2Cf5%2Cf249%2Cf250%2Cf161%2Cf340%2Cf339%2Cf341%2Cf342%2Cf343%2Cf345%2Cf344%2Cf346%2Cf347&fid=f161&pn=1&pz=100&dect=1&po=0'
  // =&secid=1.510300&exti=202504
  return request({
    url: url,
    method: 'get',
    params: { secid: code, exti: date }
  })
}

export function GetEtf1000QqList (date) {
  const url = 'https://futsseapi.eastmoney.com/list/variety/option/221/2?orderBy=xqj&sort=asc&cp=c&pageSize=100&pageIndex=0'
  // =&secid=1.510300&exti=202504
  return request({
    url: url,
    method: 'get',
    params: { date: date }
  })
}



export function GetList (code) {
  let prefix = '0.'
  const code3 = code.substr(0,3)
  if (code3 === '688'){
    prefix = '1.'
  } else if (code3 === '000') {
    prefix = '0.'
  } else if (code3 === '002') {
    prefix = '0.'
  } else if (code3 === '300') {
    prefix = '0.'
  } else if (code3.substr(0, 2) === '60'){
    prefix = '1.'
  }

  return request({
    url: 'https://push2his.eastmoney.com/api/qt/stock/kline/get',
    method: 'get',
    params: {
      code: code,
      cb: '',
      secid: prefix + code,
      ut: '',
      fields1: 'f1,f2,f3,f4,f5,f6',
      fields2: 'f51,f52,f53,f54,f55,f56,f57,f58,f59,f60,f61',
      klt: 101,
      fqt: 1,
      end: '20500101',
      lmt: '250',
      _: 1739621395911
    // code: "600839",
    }
  })
}

export function AddObj (obj) {
  return request({
    url: '/select/add',
    method: 'post',
    data: obj
  })
}

export function UpdateObj (obj) {
  return request({
    url: '/select/update',
    method: 'post',
    data: obj
  })
}
export function DelObj (id) {
  return request({
    url: '/select/delete',
    method: 'post',
    data: { id }
  })
}
export function GetCascadeData () {
  return request({
    url: '/select/cascadeData',
    method: 'get'
  })
}

export function GetYuanYin (today, fd, yd) {
  return request({
    url: '/api/wb/yuan_yin?current_time=' + today + '&fd=' + fd + '&yd=' + yd,
    method: 'get',
    data: { current_time: today }
  })
}

export function GetChanLun (code) {
  return request({
    url: 'http://192.168.112.57:30080/api/lh/chanlun',
    method: 'get',
    params: { code: code }
  })
}
