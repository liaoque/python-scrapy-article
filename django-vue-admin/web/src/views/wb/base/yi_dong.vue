<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="color0" label="代码">
    </el-table-column>
    <el-table-column prop="marketcode" label="名称" sortable sort-by="color1">
    </el-table-column>


    <el-table-column prop="zhangtingcishu" sortable sort-by="color2" label="25日涨停次数"></el-table-column>
    <el-table-column prop="lianxuzhangtingtianshuyesterday" sortable sort-by="color2" label="昨日连板天数"></el-table-column>
    <el-table-column prop="lianxuzhangtingtianshu" sortable sort-by="color2" label="连板天数"></el-table-column>
    <el-table-column prop="jianguanleixing" sortable sort-by="color2" label="监管类型"></el-table-column>
    <el-table-column prop="jianguanleixingyesterday" sortable sort-by="color2" label="昨日监管类型"></el-table-column>
    <el-table-column prop="jianguanriqi" sortable sort-by="color2" label="监管日期"></el-table-column>
    <el-table-column prop="jianguanriqiyesterday" sortable sort-by="color2" label="昨日监管日期"></el-table-column>

    <el-table-column prop="qujianyidongleixing" sortable sort-by="color2" label="区间异动类型"></el-table-column>
    <el-table-column prop="yidongshijian" sortable sort-by="color2" label="异动时间"></el-table-column>
    <el-table-column prop="yidongqujianhuanshoulv" sortable sort-by="color2" label="异动区间换手率"></el-table-column>
    <el-table-column prop="qujiantingpancishu" sortable sort-by="color2" label="区间停牌次数"></el-table-column>

  </el-table>
</template>

<!--
  代码	    名称	25日涨停次数	昨日连板天数	连板天数	监管类型	昨日监管类型	监管日期	昨日监管日期	区间异动类型	异动时间	异动区间换手率	区间停牌次数

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
