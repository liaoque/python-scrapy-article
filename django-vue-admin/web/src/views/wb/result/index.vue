<template>
  <d2-container>

    <el-row>
      <el-col :span="2">
        情绪: <span v-if="qx == 1">好</span> <span v-if="qx == -1">差</span>
      </el-col>
      <el-col :span="2">
        阈值:
      </el-col>
      <el-col :span="2">
        炸板率: {{ other.zha_ban_lv }}%
      </el-col>
      <el-col :span="2">
        竞涨停: {{ other.jing_zhang_ting }}
      </el-col>
      <el-col :span="2">
        竞跌停: {{ other.jing_die_ting }}
      </el-col>
      <el-col :span="2">
        收涨停: {{ other.shou_zhang_ting }}
      </el-col>
      <el-col :span="2">
        收跌停: {{ other.shou_die_ting }}
      </el-col>
      <el-col :span="2">
        竞上涨: {{ other.jing_shang_zhang }}
      </el-col>
      <el-col :span="2">
        竞下跌: {{ other.jing_xia_die }}
      </el-col>
      <el-col :span="2">
        收上涨: {{ other.shou_shang_zhang }}
      </el-col>
      <el-col :span="2">
        收下跌: {{ other.shou_xia_die }}
      </el-col>
      <el-col :span="8"></el-col>
      <el-col :span="6"
        :class="{ 'green': bu_zhang.lian_ban_code && bu_zhang.lian_ban_code.lianbantianshu_coloer === 35, 'red': bu_zhang.lian_ban_code && bu_zhang.lian_ban_code.lianbantianshu_coloer == 13551615, }">
        最高连板天数: {{ bu_zhang.lian_ban_code && bu_zhang.lian_ban_code.lianbantianshu }}
      </el-col>
      <el-col :span="6">
        最高连扳天数股票: {{ bu_zhang.lian_ban_code && bu_zhang.lian_ban_code.briefname }}
      </el-col>
      <el-col :span="6"
        :class="{ 'green': bu_zhang.lian_ban_code120 && bu_zhang.lian_ban_code120.zhangfu120_color == 35 }">
        120日涨幅最高: {{ bu_zhang.lian_ban_code120 && bu_zhang.lian_ban_code120.briefname }}
      </el-col>
      <el-col :span="6">
        中军股票: {{ bu_zhang.zhong_jun && bu_zhang.zhong_jun.briefname }}
      </el-col>
      <el-col :span="12">
      </el-col>
      <el-col :span="16">
        封单: <el-switch v-model="fd"></el-switch>
        异动: <el-switch v-model="yd"></el-switch>
        <el-date-picker v-model="today" type="date" value-format="yyyyMMdd" placeholder="选择日期">
        </el-date-picker>
        <el-button type="primary" @click="getCrudOptions" style="margin-left: 16px;">
          查询
        </el-button>
        <el-button type="primary" @click="restData" :disabled="dis" style="margin-left: 16px;">
          重新抓取
        </el-button>
      </el-col>

      <el-col :span="2">
        <el-button @click="drawer_zhuxian = true" type="primary" style="margin-left: 16px;">
          主线
        </el-button>
      </el-col>
      <el-col :span="2">
        <el-button @click="drawer = true" type="primary" style="margin-left: 16px;">
          补涨
        </el-button>
      </el-col>
      <el-col :span="2">
        <el-button @click="drawer_gvgn = true" type="primary" style="margin-left: 16px;">
          过滤概念
        </el-button>
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="1">
        创业板
      </el-col>
      <el-col :span="4" style="color:yellow;background-color: cornflowerblue;">
        黄色: {{ chuang.yellow }}
      </el-col>
      <el-col :span="4" style="color:orange;background-color: cornflowerblue;">
        橘色:  {{ chuang.orange }}
      </el-col>
      <el-col :span="4" style="color:purple;background-color: cornflowerblue;">
        紫色:  {{ chuang.purple }}
      </el-col>
    </el-row>
    <el-row>
      <el-col :span="1">
        主板
      </el-col>
      <el-col :span="4" style="color:yellow;background-color: cornflowerblue;">
        黄色:  {{ zhu.yellow }}
      </el-col>
      <el-col :span="4" style="color:orange;background-color: cornflowerblue;">
        橘色:  {{ zhu.orange }}
      </el-col>
      <el-col :span="4" style="color:purple;background-color: cornflowerblue;">
        紫色:  {{ zhu.purple }}
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

    <!-- 侧边栏 -->
    <el-drawer :visible.sync="drawer" :with-header="false">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>补涨概念</span>
        </div>
        <div v-for="(item, key) in bu_zhang.gn" :key="key" class="text item">
          {{ item }}
        </div>
      </el-card>
    </el-drawer>

    <el-drawer :visible.sync="drawer_gvgn" :with-header="false">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>过滤概念</span>
        </div>
        <div v-for="(item, key) in gvgn" :key="key" class="text item">
          {{ item }}
        </div>
      </el-card>
    </el-drawer>

    <el-drawer :visible.sync="drawer_zhuxian" :with-header="false">
      <el-card class="box-card">
        <div slot="header" class="clearfix">
          <span>主线</span>
        </div>
        <div v-for="(item, key) in other.zhu_xian" :key="key" class="text item">
          概念：{{ item.gn }} --- 数量：{{ item.c }}
        </div>
      </el-card>
    </el-drawer>

  </d2-container>
</template>

<script>
import * as api from './api'
// import { crudOptions } from './crud'
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
  data () {
    return {
      dis: false,
      zhu: {
        yellow: '',
        orange: '',
        purple: ''
      },
      chuang: {
        yellow: '',
        orange: '',
        purple: ''
      },
      drawer: false,
      drawer_zhuxian: false,
      today: '',
      drawer_gvgn: false,
      fd: 0,
      qx: 0,
      yd: 0,
      gvgn: [],
      other: {
        zha_ban_lv: 0,
        jing_zhang_ting: 0,
        jing_die_ting: 0,
        shou_zhang_ting: 0,
        shou_die_ting: 0,
        jing_shang_zhang: 0,
        jing_xia_die: 0,
        shou_shang_zhang: 0,
        zhu_xian: [],
        shou_xia_die: 0
      },
      bu_zhang: {},
      titles: {
        jinjinfengshu: '今竞封',
        dietingweipipei: '跌停未匹配'
      },
      activeName: 'first',
      pickerOptions: {
        value: '',
        shortcuts: [{
          text: '今天',
          onClick (picker) {
            picker.$emit('pick', new Date())
          }
        }, {
          text: '昨天',
          onClick (picker) {
            const date = new Date()
            date.setTime(date.getTime() - 3600 * 1000 * 24)
            picker.$emit('pick', date)
          }
        }, {
          text: '一周前',
          onClick (picker) {
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
    getToday () {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0') // 添加前导零
      const day = today.getDate().toString().padStart(2, '0') // 添加前导零
      const ymd = `${year}${month}${day}`
      this.today = ymd
      return ymd
    },
    restData () {
      const self = this
      if (!self.today.length) {
        self.getToday()
      }
      api.RestData(self.today).then(() => {
        self.dis = true
        setInterval(() => {
          api.RestStatus().then(res => {
            self.dis = !res.res
          })
        }, 10000)
      })
    },
    getCrudOptions () {
      const self = this
      if (!self.today.length) {
        self.getToday()
      }

      api.GetResult(self.today, self.fd, self.yd).then(function (params) {
        self.fd = params.config.fd === 1
        self.yd = params.config.yd === 1
        self.lian_ban_code_black = params.config.lian_ban_code_black
        self.gvgn = params.config.gvgn
        self.other = params.other
        if (self.fd === 1) {
          self.titles.jinjinfengshu = '涨停大肉数'
          self.titles.dietingweipipei = '跌停封单额'
        }
        self.qx = params.qing_xu
        self.bu_zhang = params.bu_zhang
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
          if (item.color0 === 46) {
            self.zhu.orange = item.briefname
          } else if (item.color3 === 29) {
            self.zhu.purple = item.briefname
          } else if (item.color1 === 36) {
            self.zhu.yellow = item.briefname
          }

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
          item.zhangdie4thday_s = ((item.zhangdie4thday * 100)).toFixed(2)
          item.zhangfu120_s = ((item.zhangfu120 * 100)).toFixed(2)
          item.jingjiajinechengjiaoliangbi_s = (item.jingjiajinechengjiaoliangbi * 100).toFixed(2)
          item.ziyouliutongshizhiyesterday_s = (Math.ceil(item.ziyouliutongshizhiyesterday / 1000000) / 100).toFixed(2)
          item.zhangdiefuqianfuquantoday_s = (Math.ceil(item.zhangdiefuqianfuquantoday * 100) / 100).toFixed(2)
          item.jingjiajinejingjialiangbi_s = (item.jingjiajinejingjialiangbi).toFixed(2)

          if (item.color0 === 46) {
            self.chuang.orange = item.briefname
          } else if (item.color3 === 29) {
            self.chuang.purple = item.briefname
          } else if (item.color1 === 36) {
            self.chuang.yellow = item.briefname
          }
          return item
        }).sort((a, b) => {
          if (a.zhangfu120 > b.zhangfu120) { return -1 }
          if (a.zhangfu120 < b.zhangfu120) { return 1 }
          return 0
        })
      })
      return []
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

<style>
.green {
  background-color: #67C23A;
}

.red {
  background-color: red;
}
</style>
