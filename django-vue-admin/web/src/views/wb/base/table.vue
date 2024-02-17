<template>
  <el-table :data="tableData" style="width: 100%">

    <el-table-column prop="code" sortable sort-by="code" label="代码">
    </el-table-column>
    <el-table-column prop="name" label="名称" sortable sort-by="name">
    </el-table-column>
    <el-table-column prop="belongtohangye" sortable sort-by="belongtohangye" label="所属行业">
    </el-table-column>
    <el-table-column prop="province" sortable sort-by="province" label="省份">
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

    <el-table-column prop="jingjiazhangfutoday" label="竞价涨幅" sortable sort-by="jingjiazhangfutoday"></el-table-column>
    <el-table-column prop="jingjiaweipipeijinetoday" label="竞价未匹配金额" sortable sort-by="jingjiaweipipeijinetoday"></el-table-column>
    <el-table-column prop="jingjiaweipipeijineyesterday" label="昨日竞价未匹配金额" sortable sort-by="jingjiaweipipeijineyesterday"></el-table-column>
    <el-table-column prop="zhangtingleixingtoday" label="涨停类型" sortable sort-by="zhangtingleixingtoday"></el-table-column>
    <el-table-column prop="zhangdiefuqianfuquantoday" label="涨跌幅" sortable sort-by="zhangdiefuqianfuquantoday"></el-table-column>
    <el-table-column prop="shoupanjia" label="收盘价" sortable sort-by="shoupanjia"></el-table-column>
    <el-table-column prop="kaipanjia" label="开盘价" sortable sort-by="kaipanjia"></el-table-column>
    <el-table-column prop="zhangtingjia" label="涨停价" sortable sort-by="zhangtingjia"></el-table-column>


  </el-table>
</template>

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
