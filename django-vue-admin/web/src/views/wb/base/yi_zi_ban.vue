<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="code" label="代码">
    </el-table-column>
    <el-table-column prop="briefname" label="名称" sortable sort-by="briefname">
    </el-table-column>
    <el-table-column prop="belongtohangye" sortable sort-by="belongtohangye" label="所属行业">
    </el-table-column>

    <el-table-column label="概念">
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

    <el-table-column prop="jingjiaweipipeijinetoday" label="竞价未匹配金额" sortable sort-by="jingjiaweipipeijinetoday">
    </el-table-column>
    <el-table-column prop="zhangdiefuqianfuquantoday" sortable sort-by="zhangdiefuqianfuquantoday" label="涨跌幅">
    </el-table-column>
    <el-table-column prop="ziyouliutongshizhi" label="自由流通市值" sortable sort-by="ziyouliutongshizhi">
    </el-table-column>
    <el-table-column prop="zhangdiefuqianfuquantoday" sortable sort-by="zhangdiefuqianfuquantoday" label="120日涨跌幅">
    </el-table-column>


  </el-table>
</template>
<!--  代码	    名称	所属行业	所属概念	竞价未匹配金额	涨跌幅	自由流通市值	120日涨跌幅
type YiZiBan struct {
	Code                      string  `json:"code"`
	MarketCode                string  `json:"market_code"`
	BelongToHangYe            string  `json:"所属同花顺行业" column:"所属行业;type=belongToHangYe"`
	BelongToGaiNian           string  `json:"所属概念"`
	ZhangDieFuQianFuQuanToday string  `json:"涨跌幅:前复权"  column:"涨跌幅;type=percent"`
	JingJiaWeiPiPeiJinEToday  float64 `json:"竞价未匹配金额"`
	DaiMa                     string  `json:"股票代码" column:"代码;type=daima"`
	BriefName                 string  `json:"股票简称" column:"名称"`
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
