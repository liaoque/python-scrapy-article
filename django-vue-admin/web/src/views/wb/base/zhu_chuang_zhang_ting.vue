<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="color0" label="代码">
    </el-table-column>
    <el-table-column prop="briefname" label="名称" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="belongtohangye" sortable sort-by="color2" label="所属行业">
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

    <el-table-column prop="zhangtingcishu25days" label="25日涨停次数" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="lianxuzhangtingtianshu" sortable sort-by="color2" label="昨日连板天数">
    </el-table-column>
    <el-table-column prop="LianBanTianShuToday" label="连板天数" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="zhangdiefuqianfuquantoday" sortable sort-by="color2" label="涨跌幅"></el-table-column>
    <el-table-column prop="zhangtingfengdanetoday" sortable sort-by="color2" label="涨停封单额"></el-table-column>
    <el-table-column prop="shoucizhangtingshijian" sortable sort-by="color2" label="首次涨停时间"></el-table-column>
    <el-table-column prop="zhangtingfengbanshichangtoday" sortable sort-by="color2" label="涨停封板时长"></el-table-column>
    <el-table-column prop="zhangtingjiachengjiaojinetoday" sortable sort-by="color2" label="涨停价成交金额"></el-table-column>
    <el-table-column prop="zhangtingcishu120days" sortable sort-by="color2" label="120日涨跌幅"></el-table-column>
    <el-table-column prop="tingleixing" sortable sort-by="color2" label="涨停类型"></el-table-column>


  </el-table>
</template>
<!--
  代码	    名称	所属行业	所属概念	25日涨停次数	昨日连板天数	连板天数	涨跌幅	涨停封单额	首次涨停时间	涨停封板时长	涨停价成交金额	120日涨跌幅	涨停类型

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
