<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">涨停原因</template>
    <d2-container type="card">
      <el-row>
        <el-tabs >
          <el-tab-pane :key="index" v-for="(item, index) in nav" :label="item.name" :name="item.key">

            <component :is="item.table" :table-data="item.data"></component>

          </el-tab-pane>
          <!-- <el-tab-pane label="配置管理" name="second">配置管理</el-tab-pane>
              <el-tab-pane label="角色管理" name="third">角色管理</el-tab-pane>
              <el-tab-pane label="定时任务补偿" name="fourth">定时任务补偿</el-tab-pane> -->
        </el-tabs>
      </el-row>
    </d2-container>
  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'yuan_yin',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      other: {
        jing_zhang_ting: null,
        jing_die_ting: null,
        zhu_ban: null,
        chuang_ye_ban: null,
        ke_chuang_ban: null
      },
      nav: [
        {
          name: '涨停大肉',
          table: 'ZhangTingDaRou',
          data: []
        },
        {
          name: '跌停大面',
          table: 'DieTingDaMian',
          data: []
        },
        {
          name: '创百日新高',
          table: 'ChuangBaiRiXinGao',
          data: []
        },
        {
          name: '今竟封',
          table: 'JinJingFeng',
          data: []
        },
        {
          name: '首版',
          table: 'ShouBan',
          data: []
        }
      ]
    }
  },
  components: {
    ZhangTingDaRou: () => import('./zhang_ting_da_rou.vue'), // 这里填写实际的组件路径
    DieTingDaMian: () => import('./die_ting_da_mian.vue'), // 这里填写实际的组件路径
    ChuangBaiRiXinGao: () => import('./chuang_bai_ri_xin_gao.vue'), // 这里填写实际的组件路径
    JinJingFeng: () => import('./jin_jing_feng.vue'), // 这里填写实际的组件路径
    ShouBan: () => import('./shou_ban.vue') // 这里填写实际的组件路径
  },
  methods: {
    getData (query) {
      return api.GetYuanYin(query)
    },
    getCrudOptions () {
      const self = this
      api.GetYuanYin().then(function (params) {
        self.nav[0].data = params.lian_zhang_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao =item.gai_nian_gu_piao.map(item=>{
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        // console.log(self.nav[0].data)
        self.nav[1].data = params.die_ting_sort

        self.nav[2].data = params.chuang_bai_ri_xin_gao_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao =item.gai_nian_gu_piao.map(item=>{
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })

        self.nav[3].data = params.yi_zi_ban_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao =item.gai_nian_gu_piao.map(item=>{
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })

        self.nav[4].data = params.shou_ban_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao =item.gai_nian_gu_piao.map(item=>{
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
      })
      return crudOptions(this)
    },
    pageRequest (query) {
      return api.GetList(query)
    },
    addRequest (row) {
      console.log('api', api)
      return api.AddObj(row)
    },
    updateRequest (row) {
      console.log('----', row)
      return api.UpdateObj(row)
    },
    delRequest (row) {
      return api.DelObj(row.id)
    }
  }
}
</script>
