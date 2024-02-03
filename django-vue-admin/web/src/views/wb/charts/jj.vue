<template>
  <el-card
    class="card-view"
  >
    <el-form :inline="true" :model="jj" class="demo-form-inline">
      <el-form-item label="基金代码">
        <el-input v-model="jj.code"></el-input>
      </el-form-item>

      <el-form-item>
        <el-button type="primary" @click="initGetJJ">查询</el-button>
      </el-form-item>
    </el-form>
    <div :options="chartOptions" style="height:300px"></div>
  </el-card>
</template>

<script>
import {request} from "@/api/service";

export default {
  props: [
    'tableData'
  ],
  data() {
    return {
      jj: {
        macd: {},
        code: "003095",
        chartOptions: {
          title: {text: 'MACD'},
          tooltip: {},
          xAxis: {type: 'category', data: []},
          yAxis: {type: 'value'},
          series: []
        }
      },
    }
  },
  methods: {
    initGetJJ() {
      api.GetList(this.code).then((data) => {
        this.jj.data = data
        this.jj.data.reverse()
        this.jj.macd = this.$macd.calculateMACD(this.jj.data.map(item => item.count))
        this.jj.chartOptions.xAxis.data = this.jj.data.map(item => item.day)
        this.jj.chartOptions.series = this.getMacdSeries().concat(this.getBarSeries())
      })
    },
    getMacdSeries() {
      const macdSeries = [];
      const difSeries = this.getLineSeries("DIF");
      const deaSeries = this.getLineSeries("DEA");
      macdSeries.push(difSeries);
      macdSeries.push(deaSeries);
      return macdSeries;
    },
    getBarSeries() {
      const barSeries = this.getLineSeries("MACD");
      barSeries.type = 'bar';
      return barSeries;
    },
    getLineSeries(name) {
      const series = {
        name: name,
        type: 'line',
        symbol: 'none',
        smooth: true,
        showSymbol: false,
        showAllSymbol: false,
        data: []
      };
      for (let i = 0; i < this.jj.data.length; i++) {
        series.data.push([this.jj.data[i]['day'], this.jj.macd[i][name]]);
      }
      return series;
    }
  },
  mounted() {
    this.initGet()
  }
}
</script>
