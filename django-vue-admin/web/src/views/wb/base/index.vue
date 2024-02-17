<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">涨停概念</template>
    <d2-container type="card">
      <el-row>
        封单:
        <el-switch v-model="fd"></el-switch>
        异动:
        <el-switch v-model="yd"></el-switch>
        <el-date-picker v-model="today" type="date" value-format="yyyyMMdd" placeholder="选择日期">
        </el-date-picker>
        <el-button type="primary" @click="getCrudOptions" style="margin-left: 16px;">
          查询
        </el-button>
      </el-row>
      <el-row>
        <el-tabs>
          <el-tab-pane :key="index" v-for="(item, index) in nav" :label="item.name" :name="item.table">
            <component :is="item.table" :table-data="item.data"></component>
          </el-tab-pane>
        </el-tabs>
      </el-row>

    </d2-container>
  </d2-container>
</template>

<script>
import * as api from './api'
import {crudOptions} from './crud'
import {d2CrudPlus} from 'd2-crud-plus'

export default {
  name: 'lian_zhang_gai_nian',
  mixins: [d2CrudPlus.crud],
  data() {
    return {
      fd: 0,
      qx: 0,
      yd: 0,
      today: '',
      nav: [
        // {
        //   name: '今曾涨停',
        //   table: 'JinCengZhangTing',
        //   data: []
        // },
        // {
        //   name: '今曾跌停',
        //   table: 'JinCengDieTing',
        //   data: []
        // },
        // {
        //   name: '昨曾涨停',
        //   table: 'ZuoCengZhangTing',
        //   data: []
        // },
        // {
        //   name: '昨曾跌停',
        //   table: 'ZuoCengDieTing',
        //   data: []
        // },
        // {
        //   name: '断板',
        //   table: 'DuanBan',
        //   data: []
        // },
        // {
        //   name: '反包',
        //   table: 'FanBao',
        //   data: []
        // },
        {
          name: '创百日新高',
          table: 'ChuangBaiRiXinGao',
          data: []
        },
        // {
        //   name: '创百日新低',
        //   table: 'ChuangBaiRiXinDi',
        //   data: []
        // },
        {
          name: '异动',
          table: 'YiDong',
          data: []
        },
        {
          name: '一字板',
          table: 'YiZiBan',
          data: []
        }, {
          name: '一字跌停',
          table: 'YiZiDieTing',
          data: []
        },
        {
          name: 'N10',
          table: 'N10',
          data: []
        },
        {
          name: 'N20',
          table: 'N20',
          data: []
        },
        {
          name: '主线源',
          table: 'ZhuXianYuan',
          data: []
        },
        {
          name: 'table',
          table: 'Table',
          data: []
        },
      ]
    }
  },
  components: {
    JinCengZhangTing: () => import('./jin_ceng_zhang_ting.vue'), // 这里填写实际的组件路径
    JinCengDieTing: () => import('./jin_ceng_die_ting.vue'), // 这里填写实际的组件路径
    ZuoCengZhangTing: () => import('./zuo_ceng_zhang_ting.vue'), // 这里填写实际的组件路径
    ZuoCengDieTing: () => import('./zuo_ceng_die_ting.vue'), // 这里填写实际的组件路径
    DuanBan: () => import('./duan_ban.vue'), // 这里填写实际的组件路径
    FanBao: () => import('./fan_bao.vue'), // 这里填写实际的组件路径
    ChuangBaiRiXinGao: () => import('./chuang_bai_ri_xin_gao.vue'), // 这里填写实际的组件路径
    ChuangBaiRiXinDi: () => import('./chuang_bai_ri_xin_di.vue'), // 这里填写实际的组件路径
    ZhuChuangZhangTing: () => import('./zhu_chuang_zhang_ting.vue'), // 这里填写实际的组件路径
    YiDong: () => import('./yi_dong.vue'), // 这里填写实际的组件路径
    YiZiBan: () => import('./yi_zi_ban.vue'), // 这里填写实际的组件路径
    YiZiDieTing: () => import('./yi_zi_die_ting.vue'), // 这里填写实际的组件路径
    N10: () => import('./n10.vue'), // 这里填写实际的组件路径
    N20: () => import('./n20.vue'), // 这里填写实际的组件路径
    ZhuXianYuan: () => import('./zhu_xian_yuan.vue'), // 这里填写实际的组件路径
    Table: () => import('./table.vue'), // 这里填写实际的组件路径
  },
  methods: {
    getToday() {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0') // 添加前导零
      const day = today.getDate().toString().padStart(2, '0') // 添加前导零
      const ymd = `${year}${month}${day}`
      this.today = ymd
      return ymd
    },
    getData(query) {
      const self = this
      if (!self.today.length) {
        self.getToday()
      }
      return api.GetBase(self.today, self.fd, self.yd)
    },
    getCrudOptions() {
      let self = this
      if (!self.today.length) {
        self.getToday()
      }
      api.GetBase(self.today, self.fd, self.yd).then(function (params) {
        self.nav[0].data = params.chuang_bai_ri_xin_gao.map(item=>{
          item.suoshugainian = item.belongtogainian.split(";")
          return item
        })
        self.nav[1].data = params.yi_dong.map(item=>{
          //   item.belongtogainian = item.belongtogainian.split(";")
          return item
        })
        self.nav[2].data = params.yi_zi_ban.map(item=>{
          item.suoshugainian = item.belongtogainian.split(";")
          return item
        })
        self.nav[3].data = params.yi_zi_die_ting.map(item=>{
          item.suoshugainian = item.suoshugainian.split(";")
          return item
        })
        self.nav[4].data = params.n10.map(item=>{
          item.suoshugainian = item.suoshugainian.split(";")
          return item
        })
        self.nav[5].data = params.n20.map(item=>{
          item.suoshugainian = item.suoshugainian.split(";")
          return item
        })
        self.nav[6].data = params.zhu_xian_yuan.map(item=>{
          item.suoshugainian = item.suoshugainian.split(";")
          return item
        })
        self.nav[7].data = params.table.map(item=>{
          // item.belongtogainian = item.belongtogainian.split(";")
          return item
        })
        // self.nav[6].data = params.chuang_bai_ri_xin_gao
        // self.nav[7].data = params.chuang_bai_ri_xin_di
        // self.nav[8].data = params.zhu_chuang_zhang_ting
        // self.nav[9].data = params.yi_dong
        // self.nav[10].data = params.yi_zi_ban
        // self.nav[11].data = params.yi_zi_die_ting
        // self.nav[12].data = params.n10
        // self.nav[13].data = params.n20
        // self.nav[14].data = params.zhu_xian_yuan
        // self.nav[15].data = params.table


        // self.nav[0].data = params.jin_ceng_zhang_ting
        // self.nav[1].data = params.jin_ceng_die_ting
        // self.nav[2].data = params.zuo_ceng_zhang_ting
        // self.nav[3].data = params.zuo_ceng_die_ting
        // self.nav[4].data = params.duan_ban
        // self.nav[5].data = params.fan_bao
        // self.nav[6].data = params.chuang_bai_ri_xin_gao
        // self.nav[7].data = params.chuang_bai_ri_xin_di
        // self.nav[8].data = params.zhu_chuang_zhang_ting
        // self.nav[9].data = params.yi_dong
        // self.nav[10].data = params.yi_zi_ban
        // self.nav[11].data = params.yi_zi_die_ting
        // self.nav[12].data = params.n10
        // self.nav[13].data = params.n20
        // self.nav[14].data = params.zhu_xian_yuan
        // self.nav[15].data = params.table
      })
      return crudOptions(this)
    },
    pageRequest(query) {
      return api.GetList(query)
    },
    addRequest(row) {
      console.log('api', api)
      return api.AddObj(row)
    },
    updateRequest(row) {
      console.log('----', row)
      return api.UpdateObj(row)
    },
    delRequest(row) {
      return api.DelObj(row.id)
    }
  }
}
</script>
