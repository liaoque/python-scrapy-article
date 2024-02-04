<template>
  <el-card
    class="card-view"
  >
    <el-form :inline="true" :model="jj" class="demo-form-inline">

      <el-form-item label="大盘">
        <el-select v-model="jj.count" placeholder="请选择">
          <el-option
            v-for="item in jj.countOptions"
            :key="item.value"
            :label="item.label"
            :value="item.value">
          </el-option>
        </el-select>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="initGetJJ">查询</el-button>
      </el-form-item>
    </el-form>
    <div id="dapan" :options="jj.chartOptions" style="height:300px"></div>
  </el-card>
</template>

<script>
import {request} from "@/api/service";
import * as api from './api'

export default {
  props: [
    'tableData'
  ],
  data() {
    return {
      jj: {
        count: 120,
        countOptions: [
          {
            label: "120天",
            value: 120,
          },
          {
            label: "200天",
            value: 200,
          },
          {
            label: "500天",
            value: 500,
          },
          {
            label: "800天",
            value: 800,
          },
          {
            label: "全部",
            value: -1,
          }
        ],
        macd: {},
        chartOptions: {
          legend: {
            data: []
          },
          title: {text: '大盘'},
          tooltip: {},
          xAxis: {type: 'category', data: []},
          yAxis: [{
            // 第一个y轴（默认左侧）
            axisLine: {
              lineStyle: {
                color: '#aaa',
                width: 1
              }
            },
            axisLabel: {
              textStyle: {
                color: '#333',
                fontSize: 12
              }
            },
            splitLine: {
              lineStyle: {
                color: '#ddd',
                type: 'dotted',
                width: 1
              }
            }
          }, {
            // 第二个y轴（右侧）
            axisLine: {
              lineStyle: {
                color: '#aaa',
                width: 1
              }
            },
            axisLabel: {
              textStyle: {
                color: '#333',
                fontSize: 12
              }
            },
            splitLine: {
              show: false // 可以选择不显示分割线
            },
            position: 'right',
          }],
          series: []
        }
      },
      options:{
        "max_dieting": "跌停",
        "max_lianban": "连板",
        "max_zhangting": "涨停",
      }
    }
  },
  methods: {
    initGetJJ() {
      api.GetDaPanList().then((data) => {
        this.jj.data = data.data
        this.jj.data.reverse()
        this.jj.chartOptions.xAxis.data = this.jj.data.map(item => item.date_as.replaceAll("-", ""))
        if (this.jj.count != -1) {
          this.jj.chartOptions.xAxis.data = this.jj.chartOptions.xAxis.data.slice(this.jj.data.length - this.jj.count)
        }
        this.jj.chartOptions.series = this.getMacdSeries()
        this.jj.chartOptions.legend.data = [
        "涨停","跌停","连板",
        ]
        this.myChart.setOption(this.jj.chartOptions)
        // console.log(
        //   [...this.jj.data.map(item => item.max_dieting)],
        //   Math.max(...this.jj.data.map(item => item.max_dieting)),
        //   Math.max(...this.jj.data.map(item => item.max_lianban)),
        //   Math.max(...this.jj.data.map(item => item.max_zhangting)),
        // )
      

        // this.jj.macd = this.$util.macd.calculateMACD(amount)
        // this.jj.chartOptions.xAxis.data = this.jj.data.map(item => item.day)
        // if (this.jj.count != -1) {
        //   this.jj.chartOptions.xAxis.data = this.jj.chartOptions.xAxis.data.slice(this.jj.data.length - this.jj.count)
        // }
        // let lineSeries = this.getLineSeries("amount", amount);
        // lineSeries.yAxisIndex = 1
        // lineSeries.color = 'red'
        // this.jj.chartOptions.series = this.getMacdSeries().concat(lineSeries).concat(this.getBarSeries())
        // this.myChart.setOption(this.jj.chartOptions)
      })
    },
    getMacdSeries() {
      const macdSeries = [];
      const max_dieting = this.getLineSeriesMacd("max_dieting", 200);
      const max_zhangting = this.getLineSeriesMacd("max_zhangting", 200);
      const max_lianban = this.getLineSeriesMacd("max_lianban", 20);
      max_lianban.yAxisIndex = 1
      macdSeries.push(max_dieting);
      macdSeries.push(max_zhangting);
      macdSeries.push(max_lianban);
      return macdSeries;
    },
    getLineSeriesMacd(name, max){
      return this.getLineSeries(name, this.jj.data.map(item => item[name]), max);
    },
    getLineSeries(name, data, max) {
      const series = {
        name: this.options[name],
        type: 'line',
        symbol: 'circle',
        smooth: true,
        showSymbol: true,
        showAllSymbol: true,
        data: []
      };
      for (let i = 0; i < this.jj.data.length; i++) {
        series.data.push((data[i] > max ? max: data[i]) / max);
      }
      if (this.jj.count != -1) {
        series.data = series.data.slice(this.jj.data.length - this.jj.count)
      }

      return series;
    }
  },
  mounted() {
    this.myChart = this.$echarts.init(document.getElementById('dapan'))

  }
}
</script>
