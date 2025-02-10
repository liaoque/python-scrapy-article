<template>
  <el-card
    class="card-view"
  >
    <el-form :inline="true" :model="jj" class="demo-form-inline">
      <el-form-item label="股票代码">
        <el-input v-model="jj.code"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="initGetJJ">查询</el-button>
      </el-form-item>
    </el-form>
    <div id="jj" :options="jj.chartOptions" style="height:400px"></div>
  </el-card>
</template>

<script>
import * as api from './api'

export default {
  props: [
    'tableData'
  ],
  data () {
    return {
      jj: {
        count: 120,
        macd: {},
        code: '600839',
        chartOptions: {
          dataset: [
            {
              id: 'rank',
              source: []
            }
          ],
          title: { text: '历史趋势' },
          tooltip: {
            trigger: 'axis',
            position: function (pt) {
              return [pt[0], '10%'];
            }
          },
          dataZoom: [
            {
              type: 'inside',
              start: 80,
              end: 100
            },
            {
              start: 80,
              end: 100
            }
          ],
          xAxis: {
            type: 'category',
            nameLocation: 'middle'
          },
          yAxis: {
            minInterval: 10,
            maxInterval: 200,
            inverse: true
          },
          series: [{
            type: 'line',
            datasetId: 'rank',
            showSymbol: false,
            encode: {
              x: 'date',
              y: 'rank',
              itemName: 'date',
              tooltip: ['rank']
            }
          }]
          // legend: {
          //   data: ['rank']
          // },
          //
          // tooltip: {},
          // xAxis: { type: 'category', data: [] },
          // yAxis: [{
          //   inverse: true,
          //   // 第一个y轴（默认左侧）
          //   axisLine: {
          //     lineStyle: {
          //       color: '#aaa',
          //       width: 1
          //     }
          //   },
          //   axisLabel: {
          //     textStyle: {
          //       color: '#333',
          //       fontSize: 12
          //     }
          //   },
          //   splitLine: {
          //     lineStyle: {
          //       color: '#ddd',
          //       type: 'dotted',
          //       width: 1
          //     }
          //   }
          // }],
          // series: []
        }
      }
    }
  },
  methods: {
    initGetJJ () {
      api.GetList(this.jj.code).then((data) => {
        // console.log(data)
        this.jj.data = data.data
        this.jj.chartOptions.dataset[0].source = [['rank', 'date']].concat(this.jj.data.map(item => [item.rank, item.date]))
        // console.log(this.jj.chartOptions)
        // this.jj.macd = this.$util.macd.calculateMACD(amount)
        // this.jj.chartOptions.xAxis.data = this.jj.data.map(item => item.date)
        // // console.log(this.jj.chartOptions.xAxis.data )
        //
        // // if (this.jj.count != -1) {
        // //   this.jj.chartOptions.xAxis.data = this.jj.chartOptions.xAxis.data.slice(this.jj.data.length - this.jj.count)
        // // }
        // const lineSeries = this.getLineSeries('rank', rank)
        // lineSeries.yAxisIndex = 0
        // lineSeries.color = 'red'
        // // lineSeries.showSymbol = false
        // console.log(lineSeries)
        // this.jj.data.map(item => {})
        // this.jj.chartOptions.series = [lineSeries]
        // this.jj.chartOptions.series = this.getMacdSeries().concat(lineSeries).concat(this.getBarSeries())
        this.myChart.setOption(this.jj.chartOptions)
      })
    },

    getLineSeries (name, data) {
      const series = {
        name: name,
        type: 'line',
        symbol: 'circle',
        smooth: true,
        showSymbol: true,
        showAllSymbol: false,
        data: []
      }
      for (let i = 0; i < this.jj.data.length; i++) {
        series.data.push(data[i])
      }
      // if (this.jj.count != -1) {
      //   series.data = series.data.slice(this.jj.data.length - this.jj.count)
      // }

      return series
    }
  },
  mounted () {
    this.myChart = this.$echarts.init(document.getElementById('jj'))
  }
}
</script>
