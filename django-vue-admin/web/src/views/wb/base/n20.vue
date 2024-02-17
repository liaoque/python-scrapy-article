<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="code" label="代码">
    </el-table-column>
    <el-table-column prop="name" label="名称" sortable sort-by="name">
    </el-table-column>
    <el-table-column prop="suoshuhangye" sortable sort-by="suoshuhangye" label="所属行业">
    </el-table-column>

    <el-table-column  label="概念">
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <el-tag disable-transitions :key="index" v-for="(gainian, index) in scope.row.suoshugainian">{{
              gainian
            }}
          </el-tag>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.suoshugainian.join(",").slice(0, 10) }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>

    <el-table-column prop="qujianzhangtingcishu" sortable sort-by="qujianzhangtingcishu" label="最大涨幅满足条件次数"></el-table-column>
    <el-table-column prop="zuidazhangfu" sortable sort-by="zuidazhangfu" label="昨日最大涨幅"></el-table-column>
    <el-table-column prop="beforeyesterdaytop" sortable sort-by="beforeyesterdaytop" label="前日涨停"></el-table-column>
    <el-table-column prop="maxzhangfu" sortable sort-by="maxzhangfu" label="前日最大涨幅"></el-table-column>
    <el-table-column prop="zhangfu120" sortable sort-by="zhangfu120" label="120日涨跌幅"></el-table-column>
    <el-table-column prop="lianbancishu" sortable sort-by="lianbancishu" label="连板次数"></el-table-column>


  </el-table>
</template>
<!--代码	    名称	所属行业	所属概念	最大涨幅满足条件次数	昨日最大涨幅	前日涨停	前日最大涨幅	120日涨跌幅	连板次数
type N20 struct {
	Code                 string  `json:"股票代码" column:"代码;type=daima"`
	Name                 string  `json:"股票简称" column:"名称"`
	SuoShuHangYe         string  `json:"所属同花顺行业" column:"所属行业;type=belongToHangYe"`
	SuoShuGaiNian        string  `json:"所属概念"`
	QuJianZhangTingCiShu int     `json:"最大涨幅满足条件的次数"  column:"最大涨幅满足条件次数"`
	ZuiDaZhangFu         float64 `json:"N字20_1"  column:"昨日最大涨幅"`
	BeforeYesterdayTop   string  `json:"前日涨停" column:"前日涨停"`
	MaxZhangFu           float64 `json:"N字20_0" column:"前日最大涨幅"`
	LianBanCiShu         int     `json:"连续涨停天数满足条件的次数" column:"连板次数"`
}

-->

<script>
export default {
  props: [
    'tableData'
  ],
  data() {
    return {}
  }
}
</script>
