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


    <el-table-column prop="zhangtingcishu" sortable sort-by="color2" label="涨停次数"></el-table-column>
    <el-table-column prop="qujianzhangtingcishu" sortable sort-by="color2" label="曾涨停次数"></el-table-column>
    <el-table-column prop="zuocengzhangting" sortable sort-by="color2" label="昨曾涨停"></el-table-column>
    <el-table-column prop="beforeyesterdaytop" sortable sort-by="color2" label="前日涨停"></el-table-column>
    <el-table-column prop="beforeyesterdaycengzhangting" sortable sort-by="color2" label="前日曾涨停"></el-table-column>
    <el-table-column prop="zhangfu120" sortable sort-by="color2" label="120日涨跌幅"></el-table-column>
    <el-table-column prop="lianbancishu" sortable sort-by="color2" label="连板次数"></el-table-column>


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
