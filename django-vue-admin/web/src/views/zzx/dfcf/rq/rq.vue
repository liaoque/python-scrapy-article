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
        <el-tag v-show="jj.name" >{{ jj.name }}</el-tag>
      </el-form-item>
    </el-form>
    <div id="jj" :options="jj.chartOptions" style="height:500px"></div>
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
        name: '',
        code: '600839'
      }
    }
  },
  methods: {
    async initGetJJ () {
      await api.GetList(this.jj.code).then((data) => {
        const d = data.data[0].date
        const popularityData = data.data.map(item => item.rank)
        api.GetGjList(this.jj.code).then((data) => {
          console.log(data.data.name)
          this.jj.name = data.data.name
          const data2 = data.data.klines.map(item => {
            item = item.split(',')
            // [开盘价, 收盘价, 最低价, 最高价]
            return [item[0], item[1], item[2], item[4], item[3], item[8]]
          }).filter(item => item[0] >= d)

          // this.jj.chartOptions2.dataset[0].source = [['price', 'date']].concat(data2)
          // console.log(data2)
          const option = this.getKOption(data2, popularityData)
          this.myChart.setOption(option)
        })
      })
    },

    getKOption (rawData, popularityData) {
      const macdData = this.$util.macd.calculateMACD(popularityData)
      console.log(macdData)
      return {
        tooltip: {
          trigger: 'axis',
          axisPointer: {
            type: 'cross'
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
        grid: [
          {
            left: '10%',
            right: '10%',
            top: '10%',
            height: '50%' // K 线图区域
          },
          {
            left: '10%',
            right: '10%',
            top: '65%',
            height: '20%' // MACD 图区域
          }
        ],

        xAxis: [
          {
            type: 'category',
            data: rawData.map((item, index) => item[0]),
            boundaryGap: false,
            gridIndex: 0 // 第一个 x 轴
          },
          {
            type: 'category',
            data: rawData.map((item, index) => item[0]),
            boundaryGap: false,
            gridIndex: 1 // 第2个 x 轴
          }
        ],
        yAxis: [
          {
            scale: true,
            name: '价格',
            gridIndex: 0, // 第一个 y 轴
            position: 'left'
          },
          {
            scale: true,
            name: '人气',
            inverse: true,
            gridIndex: 0, // 第2个 y 轴
            position: 'right'
          },
          {
            scale: true,
            gridIndex: 1 // 第三个 y 轴（MACD 图）
          }
        ],
        series: [
          {
            xAxisIndex: 0,
            yAxisIndex: 0,
            name: 'K 线图',
            type: 'candlestick',
            data: rawData.map((item, index) => [item[1], item[2], item[3], item[4], item[5]]),
            itemStyle: {
              color: '#ec0000',
              color0: '#00da3c',
              borderColor: '#8A0000',
              borderColor0: '#008F28'
            }
          },
          {
            xAxisIndex: 0,
            yAxisIndex: 1, // 使用第二个 y 轴
            name: '人气',
            type: 'line',
            data: popularityData,
            itemStyle: {
              color: '#5470C6' // 折线颜色
            },
            lineStyle: {
              width: 2
            },
            smooth: true // 是否平滑曲线
          },
          // MACD 折线图（DIFF）
          {
            name: 'DIFF',
            type: 'line',
            data: macdData.DIF,
            xAxisIndex: 1,
            yAxisIndex: 2,
            itemStyle: {
              color: '#FF7F50'
            }
          },
          // MACD 折线图（DEA）
          {
            name: 'DEA',
            type: 'line',
            data: macdData.DEA,
            xAxisIndex: 1,
            yAxisIndex: 2,
            itemStyle: {
              color: '#00BFFF'
            }
          },
          // MACD 柱状图
          {
            name: 'MACD',
            type: 'bar',
            data: macdData.MACD,
            xAxisIndex: 1,
            yAxisIndex: 2,
            itemStyle: {
              color: function (params) {
                return params.value >= 0 ? '#ec0000' : '#00da3c'
              }
            }
          }
        ]
      }
    }

  },
  mounted () {
    this.myChart = this.$echarts.init(document.getElementById('jj'))
  }
}
</script>
