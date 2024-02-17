<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="code" label="代码">
    </el-table-column>
    <el-table-column prop="marketcode" label="名称" sortable sort-by="marketcode">
    </el-table-column>


    <el-table-column prop="zhangtingcishu" sortable sort-by="zhangtingcishu" label="25日涨停次数"></el-table-column>
    <el-table-column prop="lianxuzhangtingtianshuyesterday" sortable sort-by="lianxuzhangtingtianshuyesterday" label="昨日连板天数"></el-table-column>
    <el-table-column prop="lianxuzhangtingtianshu" sortable sort-by="lianxuzhangtingtianshu" label="连板天数"></el-table-column>
    <el-table-column prop="jianguanleixing" sortable sort-by="jianguanleixing" label="监管类型"></el-table-column>
    <el-table-column prop="jianguanleixingyesterday" sortable sort-by="jianguanleixingyesterday" label="昨日监管类型"></el-table-column>
    <el-table-column prop="jianguanriqi" sortable sort-by="jianguanriqi" label="监管日期"></el-table-column>
    <el-table-column prop="jianguanriqiyesterday" sortable sort-by="jianguanriqiyesterday" label="昨日监管日期"></el-table-column>

    <el-table-column prop="qujianyidongleixing" sortable sort-by="qujianyidongleixing" label="区间异动类型"></el-table-column>
    <el-table-column prop="yidongshijian" sortable sort-by="yidongshijian" label="异动时间"></el-table-column>
    <el-table-column prop="yidongqujianhuanshoulv" sortable sort-by="yidongqujianhuanshoulv" label="异动区间换手率"></el-table-column>
    <el-table-column prop="qujiantingpancishu" sortable sort-by="qujiantingpancishu" label="区间停牌次数"></el-table-column>

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
