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

    <el-table-column prop="jingjiaweipipeijine" label="竞价未匹配金额" sortable sort-by="color1">
    </el-table-column>
    <el-table-column prop="zhangdiefu" sortable sort-by="color2" label="涨跌幅">
    </el-table-column>


  </el-table>
</template>
<!--  代码	    名称	所属行业	所属概念	竞价未匹配金额	涨跌幅
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
