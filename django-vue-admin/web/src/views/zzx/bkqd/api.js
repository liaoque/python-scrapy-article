import { request } from '@/api/service'

export function GetList (query) {
  return request({
    url: '/api/lh/bangdan',
    method: 'get',
    params: query
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
