import { request } from '@/api/service'
import {response} from "@/api/tools";

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
  return response({})
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


