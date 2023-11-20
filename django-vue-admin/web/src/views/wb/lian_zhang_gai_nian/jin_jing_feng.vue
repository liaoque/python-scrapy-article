<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column prop="gianian" label="概念" >
    </el-table-column>
    <el-table-column prop="c" label="一字板数" >
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