<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">涨停原因</template>
    <d2-container type="card">
      <el-row>
        <el-tabs>
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
  name: 'lian_zhang_gu_piao',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
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
          name: '首板',
          table: 'ShouBan',
          data: []
        },
        {
          name: '炸板',
          table: 'ZhaBan',
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
    ZhaBan: () => import('./zha_ban.vue'), // 这里填写实际的组件路径
    ShouBan: () => import('./shou_ban.vue') // 这里填写实际的组件路径
  },
  methods: {
    getData (query) {
      return api.GetLianZhangGuPiao(query)
    },
    getCrudOptions () {
      const self = this
      api.GetLianZhangGuPiao().then(function (params) {
        // console.log(111222,  [...params.chuangbairixingao])
        self.nav[0].data = params.lianzhanggupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 1000 / 1000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 1000 / 1000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        // console.log(self.nav[0].data)
        self.nav[1].data = params.dietinggupiao
        self.nav[2].data = params.chuangbairixingao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 1000 / 1000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 1000 / 1000).toFixed(2)
          item.ziyouliutongshizhiyesterday = (item.ziyouliutongshizhiyesterday / 1000 / 1000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        self.nav[3].data = params.shoubangupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 1000 / 1000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 1000 / 1000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        self.nav[4].data = params.yizibangupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 1000 / 1000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 1000 / 1000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        self.nav[5].data = params.zhabangupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 1000 / 1000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 1000 / 1000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        // self.nav[6].data = params.zhabangupiao

        console.log(params)
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
