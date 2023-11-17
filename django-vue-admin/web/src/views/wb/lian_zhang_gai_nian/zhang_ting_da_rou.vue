<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column prop="code" label="代码" width="180">
    </el-table-column>
    <el-table-column prop="name" label="名称" width="180">
    </el-table-column>
    <el-table-column prop="name" label="概念" width="180">
    </el-table-column>
    <el-table-column prop="name" label="连涨天数" width="180">
    </el-table-column>
    <el-table-column prop="name" label="涨停封单金额" width="180">
    </el-table-column>
    <el-table-column prop="name" label="涨停大肉原因" width="180">
    </el-table-column>
    <el-table-column prop="name" label="涨停大肉数" width="180">
    </el-table-column>
    <el-table-column prop="name" label="价未匹配金额" width="180">
    </el-table-column>

  </el-table>
</template>

<script>
export default {
  data () {
    return {
      tableData: [{
        date: '2016-05-02',
        name: '王小虎4',
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
