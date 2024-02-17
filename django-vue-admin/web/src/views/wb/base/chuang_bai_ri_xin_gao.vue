<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="code" label="代码">
    </el-table-column>
    <el-table-column prop="briefname" label="名称" >
    </el-table-column>
    <el-table-column prop="belongtohangye" label="所属行业">
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

    <el-table-column prop="jitianjibantoday" label="25日涨停次数" sortable sort-by="jitianjibantoday">
    </el-table-column>
    <el-table-column prop="lianxuzhangtingyesterday" sortable sort-by="lianxuzhangtingyesterday" label="昨日连板天数"></el-table-column>
    <el-table-column prop="lianbantianshutoday" label="连板天数" sortable sort-by="lianbantianshutoday"></el-table-column>
    <el-table-column prop="zhangdiefuqianfuquantoday" sortable sort-by="zhangdiefuqianfuquantoday" label="涨跌幅">
    </el-table-column>


  </el-table>
</template>
<!--
代码	    名称	所属行业	所属概念	25日涨停次数	昨日连板天数	连板天数	涨跌幅


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
