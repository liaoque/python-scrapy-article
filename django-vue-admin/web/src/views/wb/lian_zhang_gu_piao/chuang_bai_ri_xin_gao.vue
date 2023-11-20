<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column prop="code" label="代码" width="180" sortable>
    </el-table-column>
    <el-table-column prop="briefname" label="名字" width="180" >
    </el-table-column>
    <el-table-column label="所属概念" >
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <el-tag disable-transitions :key="index" v-for="(gainian, index) in scope.row.suoshugainian">{{gainian}}</el-tag>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.suoshugainian.join(",").slice(0, 10) }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>

    <el-table-column prop="jingjiaweipipeijinetoday" label="竞价未匹配金额" sortable>
    </el-table-column>
    <el-table-column prop="ziyouliutongshizhiyesterday" label="自由流通市值" sortable>
    </el-table-column>

    <el-table-column  label="创百日新高原因" sortable>
      <template slot-scope="scope">
        <el-popover trigger="hover" placement="top">
          <el-tag disable-transitions :key="index" v-for="(gainian, index) in scope.row.yuanyin">{{gainian}}</el-tag>
          <div slot="reference" class="name-wrapper">
            <el-tag size="medium">{{ scope.row.yuanyin.join(",").slice(0, 10) }}</el-tag>
          </div>
        </el-popover>
      </template>
    </el-table-column>
    <el-table-column prop="cishu" label="创白日新高数" sortable>
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  props: [
    'tableData'
  ],
  data () {
    return {
    }
  },
  created () {
    // props 会暴露到 `this` 上
    console.log(this.tableData)
  }
}
</script>
