<template>
  <d2-container>
    <el-row>
      <el-col :span="2">
        情绪: <el-tag size="medium" v-if="qx == 1">好</el-tag> <el-tag size="medium" v-if="qx == -1">坏</el-tag>
      </el-col>
      <el-col :span="2">
        补涨:
      </el-col>
      <el-col :span="2">
        阈值:
      </el-col>
      <!-- <el-col :span="2">
        昨标高:
      </el-col>
      <el-col :span="2">
        风口:
      </el-col> -->
      <el-col :span="2">
        炸板率:
      </el-col>
      <el-col :span="2">
        竞涨停:
      </el-col>
      <el-col :span="2">
        竞跌停:
      </el-col>
      <el-col :span="2">
        收涨停:
      </el-col>
      <el-col :span="2">
        收跌停:
      </el-col>
      <el-col :span="2">
        竞上涨:
      </el-col>
      <el-col :span="2">
        竞下跌:
      </el-col>
      <el-col :span="2">
        收上涨:
      </el-col>
      <el-col :span="2">
        收下跌:
      </el-col>
    </el-row>

    <el-tabs v-model="activeName">

      <el-tab-pane label="创业板概念" name="first">
        <chuangGn :data=plan.chuang_ye_ban_gai_nian :titles=titles></chuangGn>
      </el-tab-pane>

      <el-tab-pane label="创业板" name="third">
        <zhu :data=plan.chuang_ye_ban :code-map=codeMap.chuang></zhu>
      </el-tab-pane>

      <el-tab-pane label="主板" name="second">
        <zhu :data=plan.zhu_ban :code-map=codeMap.zhu></zhu>
      </el-tab-pane>

    </el-tabs>

  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

import chuangGn from './chuang_gn.vue'
import zhu from './zhu.vue'

export default {
  name: 'result',
  mixins: [d2CrudPlus.crud],
  components: {
    chuangGn,
    zhu
  },
  data() {
    return {
      fd: 0,
      qx: 0,
      titles: {
        jinjinfengshu: '今竞封',
        dietingweipipei: '跌停未匹配'
      },
      activeName: 'first',
      pickerOptions: {
        value: '',
        shortcuts: [{
          text: '今天',
          onClick(picker) {
            picker.$emit('pick', new Date())
          }
        }, {
          text: '昨天',
          onClick(picker) {
            const date = new Date()
            date.setTime(date.getTime() - 3600 * 1000 * 24)
            picker.$emit('pick', date)
          }
        }, {
          text: '一周前',
          onClick(picker) {
            const date = new Date()
            date.setTime(date.getTime() - 3600 * 1000 * 24 * 7)
            picker.$emit('pick', date)
          }
        }]
      },

      plan: {
        chuang_ye_ban_gai_nian: [],
        zhu_ban: [],
        chuang_ye_ban: []
      },
      codeMap: {
        zhu: {},
        chuang: {}
      }
    }
  },
  methods: {

    getCrudOptions() {
      const self = this
      if (self.fd === 1) {
        self.titles.jinjinfengshu = '涨停大肉数';
        self.titles.dietingweipipei = '跌停封单额'
      }
      api.GetResult().then(function (params) {
        self.qx = params.qing_xu
        self.plan.chuang_ye_ban_gai_nian = params.chuang_ye_ban_gn.map((item) => {
          // 今昨百日新高
          let today = (Math.ceil(item.chuang_bai_ri_xin_gao.today / 1000000) / 100).toFixed(2)
          let yeasterday = (Math.ceil(item.chuang_bai_ri_xin_gao.yesterday / 1000000) / 100).toFixed(2)
          item.jin_zuo_bai_ri_xin_gao = item.chuang_bai_ri_xin_gao.count + '|' + today + '|' + yeasterday

          // 实际流通市值
          item.liu_tong_shi_zhi = (Math.ceil(item.liu_tong_shi_zhi / 1000000) / 100).toFixed(2)
          item.die_ting.value = (Math.ceil(item.die_ting.value / 1000000) / 100).toFixed(2)
          // item.die_ting.jing_jia_wei_pi_pei = (Math.ceil(item.die_ting.jing_jia_wei_pi_pei / 1000000) / 100).toFixed(2)

          // 今竟封数 ，跌停未匹配
          if (self.fd === 1) {
            item.shu_liang.value = item.shu_liang.zhang_ting_da_rou
            // item.die_ting.value = item.shu_liang.feng_dan_jin_e || 0
            item.pan_zhong.feng_dan_jin_e = (Math.ceil(item.pan_zhong.feng_dan_jin_e / 1000000) / 100).toFixed(2)
          } else {
            item.shu_liang.value = item.shu_liang.jin_jing_feng_count
            // item.die_ting.value = item.shu_liang.jing_jia_wei_pi_pei || 0
            item.pan_zhong.feng_dan_jin_e = 0
          }

          // 今竟封，跌停未匹配
          today = (Math.ceil(item.jin_jing_feng.today / 1000000) / 100).toFixed(2)
          yeasterday = (Math.ceil(item.jin_jing_feng.yesterday / 1000000) / 100).toFixed(2)
          const yesterdayFengDan = (Math.ceil(item.jin_jing_feng.yesterday_fengdan / 1000000) / 100).toFixed(2)
          item.jin_zuo_jin_jing_feng = today + '|' + yeasterday + '|' + yesterdayFengDan

          return item
        }).sort((a, b) => {
          if (a.shu_liang.value > b.shu_liang.value) { return -1 }
          if (a.shu_liang.value < b.shu_liang.value) { return 1 }
          return 0
        })
        // console.log(self.plan.chuang_ye_ban_gai_nian)

        self.plan.zhu_ban = params.zhu_data.map((item) => {
          self.codeMap.zhu[item.code] = item
          item.jingjiajinetoday_s = (Math.ceil(item.jingjiaweipipeijinetoday / 1000000) / 100).toFixed(2)
          item.zhangtingfengdanetoday_s = (Math.ceil(item.zhangtingfengdanetoday / 1000000) / 100).toFixed(2)
          item.zhangfu5_s = (Math.ceil(item.zhangfu5 * 100) / 100).toFixed(2)
          item.zhangdie4thday_s = (item.zhangdie4thday * 100).toFixed(2)
          item.zhangfu120_s = (item.zhangfu120 * 100).toFixed(2)
          item.jingjiajinechengjiaoliangbi_s = (item.jingjiajinechengjiaoliangbi * 100).toFixed(2)
          item.ziyouliutongshizhiyesterday_s = (Math.ceil(item.ziyouliutongshizhiyesterday / 1000000) / 100).toFixed(2)
          item.zhangdiefuqianfuquantoday_s = (Math.ceil(item.zhangdiefuqianfuquantoday * 100) / 100).toFixed(2)
          item.jingjiajinejingjialiangbi_s = (item.jingjiajinejingjialiangbi).toFixed(2)

          return item
        }).sort((a, b) => {
          if (a.zhangfu120 > b.zhangfu120) { return -1 }
          if (a.zhangfu120 < b.zhangfu120) { return 1 }
          return 0
        })

        self.plan.chuang_ye_ban = params.chuang_data.map((item) => {
          self.codeMap.chuang[item.code] = item
          item.jingjiajinetoday_s = (Math.ceil(item.jingjiaweipipeijinetoday / 1000000) / 100).toFixed(2)
          item.zhangtingfengdanetoday_s = (Math.ceil(item.zhangtingfengdanetoday / 1000000) / 100).toFixed(2)
          item.zhangfu5_s = (Math.ceil(item.zhangfu5 * 100) / 100).toFixed(2)
          item.zhangdie4thday_s = ((item.zhangdie4thday * 100) ).toFixed(2)
          item.zhangfu120_s = ((item.zhangfu120 * 100) ).toFixed(2)
          item.jingjiajinechengjiaoliangbi_s = (item.jingjiajinechengjiaoliangbi * 100).toFixed(2)
          item.ziyouliutongshizhiyesterday_s = (Math.ceil(item.ziyouliutongshizhiyesterday / 1000000) / 100).toFixed(2)
          item.zhangdiefuqianfuquantoday_s = (Math.ceil(item.zhangdiefuqianfuquantoday * 100) / 100).toFixed(2)
          item.jingjiajinejingjialiangbi_s = (item.jingjiajinejingjialiangbi).toFixed(2)

          return item
        }).sort((a, b) => {
          if (a.zhangfu120 > b.zhangfu120) { return -1 }
          if (a.zhangfu120 < b.zhangfu120) { return 1 }
          return 0
        })
      })
      return []
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

<style>
.green {
  background-color: #67C23A;
}

.red {
  background-color: red;
}
</style>
