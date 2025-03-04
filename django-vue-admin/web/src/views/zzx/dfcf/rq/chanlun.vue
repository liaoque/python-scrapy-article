<template>
  <div id="cl" :options="jj.chartOptions" style="height:500px"></div>
</template>

<script>
import * as api from './api'
import jj from '@/views/wb/charts/jj.vue'

export default {
  name: 'chanlun',
  computed: {
    jj () {
      return jj
    }
  },
  props: [

  ],
  data () {
    return {
    }
  },
  methods: {
    async render (code, rawData) {
      const result = await api.GetChanLun(code).then((data) => {
        // 构造“笔”系列数据，绘制为线段。这里每一笔用一条单独的 line 系列展示，
        // 横坐标用笔起始和结束时的时间（或索引），纵坐标为对应的价格
        const strokeSeries = data.data.bi_list.map(stroke => {
          return {
            name: '笔',
            type: 'line',
            data: [
              [stroke.start_index, stroke.start_value],
              [stroke.end_index, stroke.end_value]
            ],
            // 采用不同颜色区分上升和下降笔
            lineStyle: {
              width: 2,
              color: stroke.direction === 'up' ? 'red' : 'green'
            },
            symbol: 'none'
          }
        })

        // 构造中枢区域（pivot）标记。利用 markArea 绘制矩形区域，
        // 每个中枢区域的横坐标范围为 [start_index, end_index]，
        // 纵坐标范围为 [L_pivot, H_pivot]
        const pivotMarkAreas = data.data.pivots.map(pivot => {
          return [
            {
              xAxis: pivot.start_index,
              yAxis: pivot.L_pivot
            },
            {
              xAxis: pivot.end_index,
              yAxis: pivot.H_pivot
            }
          ]
        })

        // 构造买卖点信号。利用 markPoint 展示买入/卖出信号。
        // 这里假设 signals 中每个信号包含 time、price 和 type 字段。
        const signalPoints = data.data.signals.map(signal => {
          return {
            coord: [signal.time, signal.price],
            value: signal.type === 'buy' ? '买' : '卖',
            itemStyle: {
              color: signal.type === 'buy' ? 'red' : 'green'
            }
          }
        })

        return { strokeSeries, pivotMarkAreas, signalPoints }
      })

      const option = {
        title: {
          text: '缠论K线图'
        },
        tooltip: {
          trigger: 'axis'
        },
        xAxis: {
          type: 'category',
          data: rawData.map((item, index) => item[0]),
          boundaryGap: true
        },
        yAxis: {
          type: 'value',
          scale: true
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
        series: [
          {
            name: 'K线',
            type: 'candlestick',
            data: rawData.map((item, index) => [item[1], item[2], item[3], item[4], item[5]]),
            // 利用 markArea 绘制中枢区域
            markArea: {
              data: result.pivotMarkAreas,
              // 可设置透明背景突出区域
              itemStyle: {
                color: 'rgba(0, 0, 255, 0.2)'
              }
            },
            // 利用 markPoint 绘制买卖信号
            markPoint: {
              data: result.signalPoints,
              label: {
                formatter: '{b}',
                color: '#fff'
              }
            }
          },
          // 添加所有“笔”系列
          ...result.strokeSeries
        ]
      }

      this.myChart.setOption(option)
    }

  },
  mounted () {
    this.myChart = this.$echarts.init(document.getElementById('cl'))
  }
}
</script>
