<template>
  <div id="vix" style="height:500px"></div>

</template>

<script>
import * as api from './api'

export default {
  name: 'vix',
  props: [],
  data () {
    return {}
  },
  methods: {
    async render () {
      await api.GetGzRate().then(res => res.json()).then(async res => {
        const d = new Date()
        const dateStr = d.getFullYear() + (d.getMonth() + 1).toString().padStart(2, '0')
        // eslint-disable-next-line no-unused-vars
        let dateStrNext = d.getFullYear() + (d.getMonth() + 2).toString().padStart(2, '0')
        if (d.getMonth() === 12) {
          dateStrNext = (d.getFullYear() + 1) + '01'
        }
        const r = res.result.data[0].EMM00588704
        const etf300 = await this.getQq('1.510300', dateStr, dateStrNext, r)
        const etf50 = await this.getQq('1.510050', dateStr, dateStrNext, r)
        const etf500 = await this.getQq('1.510500', dateStr, dateStrNext, r)
        const etfkc = await this.getQq('1.588000', dateStr, dateStrNext, r)
        console.log(etf300, etf50, etf500, etfkc)
      }).catch(err => console.log(err))
      // const popularityDataMap = popularityData.reduce((acc, item) => {
      //   acc[item.date] = item
      //   return acc
      // }, {})
      //
      // const startDate = new Date(d)
      // const endDate = new Date(popularityData[popularityData.length - 1].date)
      // console.log(endDate)
      // // 根据开始和结束日期填充一个日期数组
      // const dateList = this.$util.fillDateList(startDate, endDate)
      //
      // // 根据日期数组，补充 popularityDataMap 中缺的数据
      // popularityData = this.$util.fillDayData(dateList, popularityDataMap)
      //
      // const dates = data2.map(item => item[0])
      // popularityData = popularityData.filter(item => dates.includes(item.date)).map(item => item.rank)
      // const option = this.getKOption(data2, popularityData)
      // this.myChart.setOption(option)
    },

    getKOption (rawData, popularityData) {

    },
    async getQq (code, dateStr, dateStrNext, r) {
      const etf300Date = await api.GetEtfQqListDate(code)
      const etf300 = await api.GetEtfQqList(code, dateStr)
      const etf300Next = await api.GetEtfQqList(code, dateStrNext)
      // console.log(etf300, etf300Date, etf300Next, code, dateStr)
      return this.$util.calculateVix(
        etf300.data.diff.map(item => {
          return {
            K: item.f161,
            call: item.f2 / 1000,
            put: item.f341 / 1000
          }
        }),
        etf300Next.data.diff.map(item => {
          return {
            K: item.f161,
            call: item.f2 / 1000,
            put: item.f341 / 1000
          }
        }),
        r,
        etf300Date.data.optionExpireInfo[0].days,
        etf300Date.data.optionExpireInfo[1].days
      )
    }
  },
  mounted () {
    this.myChart = this.$echarts.init(document.getElementById('vix'))
  }
}
</script>
