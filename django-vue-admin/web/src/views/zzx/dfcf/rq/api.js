import { request } from '@/api/service'

export  function GetList (code) {
  return request({
    url: '/api/lh/lsqs',
    method: 'get',
    params: { code: code }
  })
}

export  function GetGjList (code) {
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
