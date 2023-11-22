<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">涨停原因
      <p>
        <el-tag>竞涨停{{ other.jing_zhang_ting }}</el-tag>
        <el-tag type="info">竞跌停{{ other.jing_die_ting }}</el-tag>
      </p>
      <p>
        <el-tag>【主板】({{ other.zhu_ban.code }}){{ other.zhu_ban.briefname }}【5日涨跌幅】{{ other.zhu_ban.zhangfu5.toFixed(2) }}</el-tag>

      </p>
      <p>
        <el-tag>【创业板】({{ other.chuang_ye_ban.code }}){{ other.chuang_ye_ban.briefname }}【5日涨跌幅】{{ other.chuang_ye_ban.zhangfu5.toFixed(2) }}</el-tag>

      </p>
      <p>
        <el-tag>【科创板】({{ other.ke_chuang_ban.code }}){{ other.ke_chuang_ban.briefname }}【5日涨跌幅】{{ other.ke_chuang_ban.zhangfu5.toFixed(2) }}</el-tag>
      </p>
    </template>
    <d2-container type="card">
      <el-row>
        <el-tabs>
          <el-tab-pane :key="index" v-for="(item, index) in nav" :label="item.name" :name="item.key">
            <component :is="item.table" :table-data="item.data"></component>
          </el-tab-pane>
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
        self.other.jing_zhang_ting = params.jing_jia_sort.zhang_ting.toFixed(2)
        self.other.jing_die_ting = params.jing_jia_sort.die_ting.toFixed(2)
        self.other.zhu_ban = params.day_5_sort.zhu_ban
        self.other.chuang_ye_ban = params.day_5_sort.chuang_ye_ban
        self.other.ke_chuang_ban = params.day_5_sort.ke_chuang_ban

        self.nav[0].data = params.lian_zhang_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao = item.gai_nian_gu_piao.map(item => {
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
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
          item.gai_nian_gu_piao = item.gai_nian_gu_piao.map(item => {
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })

        self.nav[3].data = params.yi_zi_ban_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao = item.gai_nian_gu_piao.map(item => {
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            return item
          })
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })

        self.nav[4].data = params.shou_ban_sort.map(item => {
          item.gai_nian_jing_jia_wei_pi_pei = (item.gai_nian_jing_jia_wei_pi_pei / 10000 / 10000).toFixed(2)
          item.gai_nian_feng_dan_jin_e = (item.gai_nian_feng_dan_jin_e / 10000 / 10000).toFixed(2)
          item.gai_nian_gu_piao = item.gai_nian_gu_piao.map(item => {
            item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
            item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
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
