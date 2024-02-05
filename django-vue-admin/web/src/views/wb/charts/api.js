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
    url: '/select/update',
    method: 'get',
  }).then((data) => {
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
