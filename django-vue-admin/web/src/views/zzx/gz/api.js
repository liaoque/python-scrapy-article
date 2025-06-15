import { request } from '@/api/service'

export function getStockPanel (data) {
  return request({
    url: '/api/lh/gz',
    method: 'get',
    params: data
  })
}

export function UpdateObj (code) {
  return Promise.resolve()
}

export function AddObj (code) {
  return Promise.resolve()
}

export function DelObj (code) {
  return Promise.resolve()
}
