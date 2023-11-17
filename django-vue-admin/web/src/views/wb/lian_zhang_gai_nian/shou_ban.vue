<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column prop="code" label="代码" width="180">
    </el-table-column>
    <el-table-column prop="name" label="名称" width="180">
    </el-table-column>
    <el-table-column prop="name" label="概念" width="180">
    </el-table-column>
    <el-table-column prop="name" label="涨停封单额" width="180">
    </el-table-column>
    <el-table-column prop="name" label="实际流通" width="180">
    </el-table-column>
    <el-table-column prop="name" label="首板原因" width="180">
    </el-table-column>
    <el-table-column prop="name" label="首板数" width="180">
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  data () {
    return {
      tableData: [{
        date: '2016-05-02',
        name: '王小虎5',
        address: '上海市普陀区金沙江路 1518 弄'
      }, {
        date: '2016-05-04',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1517 弄'
      }, {
        date: '2016-05-01',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1519 弄'
      }, {
        date: '2016-05-03',
        name: '王小虎',
        address: '上海市普陀区金沙江路 1516 弄'
      }]
    }
  }
}
</script>
