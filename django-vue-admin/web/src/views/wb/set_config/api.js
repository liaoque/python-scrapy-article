import { request } from '@/api/service'


export function UpdateObj (obj) {
  return request({
    url:  '/api/wb/config',
    method: 'post',
    data: obj
  })
}

export function GetCascadeData () {
  return request({
    url: '/api/wb/config',
    method: 'get'
  })
}
