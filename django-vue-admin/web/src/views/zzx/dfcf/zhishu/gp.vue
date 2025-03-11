<template>
  <el-card
    class="card-view"
  >
    <el-form :inline="true" :model="jj" class="demo-form-inline">
      <el-form-item label="指数代码">
        <el-input v-model="jj.code"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="initGetJJ">查询</el-button>
        <el-tag v-show="jj.name" >{{ jj.name }}</el-tag>
      </el-form-item>
    </el-form>
    <vix ref="vix"></vix>
<!--    <chanlun ref="chanlun"></chanlun>-->
  </el-card>
</template>

<script>
import * as api from './api'

export default {
  props: [
    'tableData'
  ],
  components: {
    vix: () => import('./vix.vue') // 这里填写实际的组件路径
  },
  data () {
    return {
      jj: {
        count: 120,
        macd: {},
        name: '',
        code: '600839'
      }
    }
  },
  methods: {
    async initGetJJ () {
      this.$refs.vix.render()
      // await api.GetList(this.jj.code).then(async (data) => {
      //   const d = data.data[0].date
      //   const popularityData = data.data //
      //   const result = await api.GetGjList(this.jj.code).then((data) => {
      //     this.jj.name = data.data.name
      //     const data2 = data.data.klines.map(item => {
      //       item = item.split(',')
      //       // [开盘价, 收盘价, 最低价, 最高价]
      //       return [item[0], item[1], item[2], item[4], item[3], item[8]]
      //     }).filter(item => item[0] >= d)
      //     this.$refs.rq.render(data2, d, popularityData)
      //     return data2
      //   })
      //
      //   await this.$refs.chanlun.render(this.jj.code, result)
      // })
    }

  },
  mounted () {

    // this.myChart = this.$echarts.init(document.getElementById('jj'))
  }
}
</script>
