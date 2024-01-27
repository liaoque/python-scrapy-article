<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">连涨股票</template>
    <d2-container type="card">
      <el-row>
        <el-date-picker v-model="today" type="date" value-format="yyyyMMdd" placeholder="选择日期">
        </el-date-picker>
        <el-button type="primary" @click="getCrudOptions" style="margin-left: 16px;">
          查询
        </el-button>
      </el-row>
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
      today: '',
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
          name: '炸板',
          table: 'ZhaBan',
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
    getToday () {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0') // 添加前导零
      const day = today.getDate().toString().padStart(2, '0') // 添加前导零
      const ymd = `${year}${month}${day}`
      this.today = ymd
      return ymd
    },
    getData (query) {
      const self = this
      if (!self.today.length) {
        self.getToday()
      }
      return api.GetLianZhangGuPiao(self.today)
    },
    getCrudOptions () {
      const self = this
      if (!self.today.length) {
        self.getToday()
      }
      api.GetLianZhangGuPiao(self.today).then(function (params) {
        // console.log(111222,  [...params.chuangbairixingao])
        self.nav[0].data = params.lianzhanggupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        // console.log(self.nav[0].data)
        self.nav[1].data = params.dietinggupiao
        self.nav[2].data = params.zhabangupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        self.nav[3].data = params.chuangbairixingao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
          item.ziyouliutongshizhiyesterday = (item.ziyouliutongshizhiyesterday / 10000 / 10000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })

        self.nav[4].data = params.yizibangupiao.map(item => {
          item.jingjiaweipipeijinetoday = (item.jingjiaweipipeijinetoday / 10000 / 10000).toFixed(2)
          item.ziyouliutongshizhiyesterday = (item.ziyouliutongshizhiyesterday / 10000 / 10000).toFixed(2)
          item.zhangfu120 = (item.zhangfu120).toFixed(2)

          return item
        })
        self.nav[5].data = params.shoubangupiao.map(item => {
          item.ziyouliutongshizhiyesterday = (item.ziyouliutongshizhiyesterday / 10000 / 10000).toFixed(2)
          item.zhangtingfengdanetoday = (item.zhangtingfengdanetoday / 10000 / 10000).toFixed(2)
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
