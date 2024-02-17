<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="color0" label="代码">
    </el-table-column>
    <el-table-column prop="name" label="名称" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="suoshuhangye" sortable sort-by="color2" label="所属行业">
    </el-table-column>

    <el-table-column sortable sort-by="color3" label="概念">
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

    <el-table-column prop="zhangfu10" label="10日涨跌幅" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="zhangfu30" sortable sort-by="color2" label="30日涨跌幅">
    </el-table-column>


  </el-table>
</template>
<!--  代码	    名称	所属行业	所属概念	10日涨跌幅	30日涨跌幅
type ZhuXianYuan struct {
	Code          string  `json:"股票代码" column:"代码;type=daima"`
	Name          string  `json:"股票简称" column:"名称"`
	SuoShuHangYe  string  `json:"所属同花顺行业" column:"所属行业;type=belongToHangYe"`
	SuoShuGaiNian string  `json:"所属概念"`
	ZhangFu10     float64 `json:"区间涨跌幅:前复权2"  column:"10日涨跌幅;type=percent"`
	ZhangFu30     float64 `json:"区间涨跌幅:前复权1"  column:"30日涨跌幅;type=percent"`
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
