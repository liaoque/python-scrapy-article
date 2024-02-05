import {request} from '@/api/service'

export function GetList(code) {
  return request({
    url: 'http://81.68.241.227:8082/polls/jj/' + code
  }).then((data) => {
    let data2 = []
    for (let key in data) {
      data2.push({
        day: key,
        count: parseFloat(data[key])
      })
    }
    return data2
  })
}

export function GetDaPanList() {
  return request({
    url: 'http://81.68.241.227:8082/polls/da_pan'
  }).then((data) => {

    return data
  })
}

export function GetDaAList() {
  return request({
    url: 'https://push2his.eastmoney.com/api/qt/stock/kline/get?cb=&secid=1.000001&ut=fa5fd1943c7b386f172d6893dbfba10b&fields1=f1%2Cf2%2Cf3%2Cf4%2Cf5%2Cf6&fields2=f51%2Cf53%2Cf59%2Cf60&klt=101&fqt=1&end=20500101&lmt=100000&_=1707144525089',
    method: 'get',
  }).then((data) => {
    data.data.klines.map(item=>{
      item = item.splice(",")
      return {
        "day":item[0].replace("-",""),
        "count":item[1],
        "rate":item[2],
        "points":item[3],
      }
    })
    return data
  })
}

export function DelObj(id) {
  return request({
    url: '/select/delete',
    method: 'post',
    data: {id}
  })
}

export function GetCascadeData() {
  return request({
    url: '/select/cascadeData',
    method: 'get'
  })
}
