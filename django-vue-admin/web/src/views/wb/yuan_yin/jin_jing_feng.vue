<template>
  <el-table :data="tableData" style="width: 100%">
    <el-table-column type="expand">
      <template slot-scope="props">
        <el-form label-position="left" inline class="demo-table-expand">
          <el-form-item ::key="index" v-for="(item, index) in props.row.gai_nian_gu_piao" :label="item.briefname"
            :name="item.code">
            <span>{{ item.jingjiaweipipeijinetoday }}</span>
          </el-form-item>
        </el-form>
      </template>
    </el-table-column>
    <el-table-column prop="suoshugainian" label="名称" width="180">
    </el-table-column>
    <el-table-column prop="gai_nian_jing_jia_wei_pi_pei" label="竞价未匹配" width="180">
    </el-table-column>
  </el-table>
</template>

<script>
export default {
  props: [
    'tableData'
  ],
  data() {
    return {

    }
  }
}
</script>
