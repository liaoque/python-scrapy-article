import { request } from '@/api/service'

export function GetList (query) {
  return new Promise((resolve) => {
    setTimeout(() => {
      resolve({
        code: 2000,
        msg: 'success',
        data: {
          total: 99,
          current: query.current,
          size: 20,
          data: [
            { id: 1, select1: '1', select2: 'sz,wh' },
            { id: 2, select1: '1', select2: 'sz,sh' },
            { id: 3, select1: '0', select2: 'sz,gz' },
            { id: 4, select1: '1', select2: 'sz' },
            { id: 5, select1: '1', select2: 'sz,sh' },
            { id: 6, select1: '1', select2: 'sz' }
          ]
        }
      })
    })
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
    url: '/api/wb/yuan_yin?current_time='+today + '&fd=' + fd + '&yd=' + yd,
    method: 'get',
    data: { current_time: today }
  })
}
