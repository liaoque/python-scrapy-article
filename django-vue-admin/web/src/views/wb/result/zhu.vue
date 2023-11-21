<template>
  <div>
    <el-table :cell-class-name="cellClassName" :data="data.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      style="width: 100%">
      <el-table-column prop="code" sortable sort-by="code" label="代码">
      </el-table-column>
      <el-table-column prop="briefname" label="名称">
      </el-table-column>
      <el-table-column prop="jingjiajinetoday_s" sortable sort-by="jingjiajinetoday" label="竞价未匹配">
      </el-table-column>
      <el-table-column prop="suoshugainian" sortable sort-by="suoshugainian" label="所属概念">
      </el-table-column>

      <el-table-column prop="zhangdiefuqianfuquantoday_s" sortable sort-by="zhangdiefuqianfuquantoday" label="涨跌幅">
      </el-table-column>
      <el-table-column prop="zhangdie4thday_s" sortable sort-by="zhangdie4thday" label="4日涨跌幅">
      </el-table-column>
      <el-table-column prop="jingjiajinechengjiaoliangbi_s" sortable sort-by="jingjiajinechengjiaoliangbi" label="竞价量比">
      </el-table-column>
      <el-table-column prop="jingjiajinechengjiaoliangbi_s" sortable sort-by="jingjiajinechengjiaoliangbi" label="今昨量比">
      </el-table-column>
      <el-table-column prop="lianbantianshuyesterday" sortable sort-by="lianbantianshuyesterday" label="昨日连板天数">
      </el-table-column>
      <el-table-column prop="zhangfu120_s" sortable sort-by="zhangfu120" label="120日涨跌幅">
      </el-table-column>
      <el-table-column prop="yidongcishu" sortable sort-by="yidongcishu" label="异动次数">
      </el-table-column>
      <el-table-column prop="jianguanleixingyesterday" sortable sort-by="jianguanleixingyesterday" label="监管">
      </el-table-column>
      <el-table-column prop="chuangbairixingao" sortable sort-by="chuangbairixingao" label="创百日新高">
      </el-table-column>
      <el-table-column prop="ziyouliutongshizhiyesterday_s" sortable sort-by="ziyouliutongshizhiyesterday" label="自由流通市值">
      </el-table-column>
    </el-table>
    <div class="block">
      <el-pagination layout="prev, pager, next"  :total="data.length" :current-page="currentPage"
         :page-size="pageSize"
        @current-change="handleCurrentChange">
      </el-pagination>
    </div>
  </div>
</template>

<script>
export default {
  name: 'zhu_ban',
  props: {
    data: [],
    codeMap: {}
  },
  data () {
    return {
      currentPage: 1, // 当前页码
      pageSize: 50 // 每页的数据条数
    }
  },
  methods: {
    // 每页条数改变时触发 选择一页显示多少行
    handleSizeChange (val) {
      this.currentPage = 1
      this.pageSize = val
    },
    // 当前页改变时触发 跳转其他页
    handleCurrentChange (val) {
      this.currentPage = val
    },
    cellClassName (row) {
      const key = 'color' + row.columnIndex
      if (parseInt(row.row[key]) === 35) {
        return 'el-button--success'
      }
    }
  }
}
</script>
