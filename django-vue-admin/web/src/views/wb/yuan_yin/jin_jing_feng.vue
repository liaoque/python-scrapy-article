<template>
  <d2-container>
    <template slot="header">{{ header.gn }} - {{ header.je }}</template>
    <el-table :data="tableData" style="width: 100%">
      <el-table-column prop="date" label="名称" width="180">
      </el-table-column>
      <el-table-column prop="name" label="竞价未匹配" width="180">
      </el-table-column>
    </el-table>
  </d2-container>
</template>

<script>
export default {
  data () {
    return {
      header: {
        gn: '',
        je: ''
      },
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
