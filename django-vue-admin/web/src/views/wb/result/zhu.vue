<template>
  <div>
    <el-table :cell-class-name="cellClassName" :data="data.slice((currentPage - 1) * pageSize, currentPage * pageSize)"
      style="width: 100%">
      <el-table-column prop="code" sortable sort-by="color0" label="代码">
      </el-table-column>
      <el-table-column prop="briefname" label="名称" sortable sort-by="color1">
      </el-table-column>
      <el-table-column prop="jingjiajinetoday_s" sortable sort-by="color2" label="竞价未匹配">
      </el-table-column>
      <el-table-column sortable sort-by="color3" label="概念">
        <template slot-scope="scope">
          <el-popover trigger="hover" placement="top">
            <el-tag disable-transitions :key="index" v-for="(gainian, index) in scope.row.suoshugainian">{{ gainian
            }}</el-tag>
            <div slot="reference" class="name-wrapper">
              <el-tag size="medium">{{ scope.row.suoshugainian.join(",").slice(0, 10) }}</el-tag>
            </div>
          </el-popover>
        </template>
      </el-table-column>

      <el-table-column prop="zhangdiefuqianfuquantoday_s" sortable sort-by="color4" label="涨跌幅">
      </el-table-column>
      <el-table-column prop="zhangdie4thday_s" sortable sort-by="color5" label="4日">
      </el-table-column>
      <el-table-column prop="jingjiajinechengjiaoliangbi_s" sortable sort-by="color6" label="竞价量比">
      </el-table-column>
      <el-table-column prop="jingjiajinejingjialiangbi_s" sortable sort-by="color7" label="今昨量比">
      </el-table-column>
      <el-table-column prop="lianbantianshuyesterday" sortable sort-by="color8" label="昨日连板">
      </el-table-column>
      <el-table-column prop="zhangfu120_s" sortable sort-by="color9" label="120日">
      </el-table-column>
      <el-table-column prop="yidongcishu" sortable sort-by="color10" label="异动">
      </el-table-column>
      <el-table-column prop="jianguanleixingyesterday" sortable sort-by="color11" label="监管">
      </el-table-column>
      <el-table-column prop="chuang_bai_ri_xin_gao" sortable sort-by="color12" label="创百日新高">
      </el-table-column>
      <el-table-column prop="ziyouliutongshizhiyesterday_s" sortable sort-by="color13" label="流通市值">
      </el-table-column>
    </el-table>
    <div class="block">
      <el-pagination layout="prev, pager, next" :total="data.length" :current-page="currentPage" :page-size="pageSize"
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
  data() {
    return {
      currentPage: 1, // 当前页码
      pageSize: 500 // 每页的数据条数
    }
  },
  methods: {
    // 每页条数改变时触发 选择一页显示多少行
    handleSizeChange(val) {
      this.currentPage = 1
      this.pageSize = val
    },
    // 当前页改变时触发 跳转其他页
    handleCurrentChange(val) {
      this.currentPage = val
    },
    cellClassName(row) {
      const key = 'color' + row.columnIndex
      // console.log(row)
      // '    紫色 29 橘色 46 黄色 36 绿色 35 红色 3  粉色 13551615
      let d = {
        "35": 'el-button--success',
        "46": 'el-button--46',
        "36": 'el-button--36',
        "13551615": 'el-button--13551615',
        "29": 'el-button--29',
        "37": 'el-button--37',
        "38": 'el-button--38',
        "3": 'el-button--3',
      }

      return d[row.row[key]]
    }
  }
}
</script>

<style>
.el-table {
  font-size: 10px;
}

.el-button--29 {
  color: #FFF;
  background-color: purple;
}

.el-button--36 {
  color: blue;
  background-color: yellow;
}

.el-button--46 {
  color: #FFF;
  background-color: orange;
}

.el-button--3 {
  color: #FFF;
  background-color: red;
}

.el-button--13551615 {
  color: #FFF;
  background-color: pink;
}

.el-button--37 {
  color: #FFF;
  background-color: blue;
}

.el-button--38 {
  color: #FFF;
  background-color: pink;
}
</style>
