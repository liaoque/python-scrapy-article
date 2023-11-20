<template>
    <el-table
          :data="data"
          style="width: 100%">
            <el-table-column
              prop="suoshugainian"
              label="所属概念"
              width="180">
              <template slot-scope="scope">
                  
                  <span :class="{'el-button--danger': scope.row.chuang_bai_ri_xin_gao.power==13421823}">{{ scope.row.suoshugainian }}</span>
                </template>
            </el-table-column>
            <el-table-column
              label="今昨百日新高"
              sortable
              sort-by="chuang_bai_ri_xin_gao.count"
              width="180">
                <template slot-scope="scope">
                  
                  <span :class="{'el-button--success': scope.row.chuang_bai_ri_xin_gao.power==35}">{{ scope.row.jin_zuo_bai_ri_xin_gao }}</span>
                </template>
            </el-table-column>
            <el-table-column
            sortable
            sort-by="liu_tong_shi_zhi"
              label="实际流通">
                <template slot-scope="scope">
                  
                  <span >{{ scope.row.liu_tong_shi_zhi_s }}</span>
                </template>
            </el-table-column>
            <el-table-column
            sortable
            sort-by="jin_jing_feng_count.count"
              label="今竞封数">
                <template slot-scope="scope">
                  
                  <span :class="{'el-button--danger': scope.row.jin_jing_feng_count.power==13421823}">{{ scope.row.jin_jing_feng_count.count }}</span>
                </template>
            </el-table-column>
            <el-table-column
            sortable
            sort-by="jin_jing_feng.today"
              label="今竞封">
                <template slot-scope="scope">
                  
                  <span :class="{'el-button--success': scope.row.jin_jing_feng.power==35}">{{ scope.row.jin_zuo_jin_jing_feng }}</span>
                </template>
            </el-table-column>
            <el-table-column
              sortable
              sort-by="pan_zhong.feng_dan"
              label="盘中封单总和">
              <template slot-scope="scope">
                  
                  <span :class="{'el-button--success': scope.row.pan_zhong.power==35}">{{ scope.row.pan_zhong.feng_dan }}</span>
                </template>
            </el-table-column>
            <el-table-column
            sortable
              sort-by="die_ting_da_mian.today"
              label="跌停未匹配">
              <template slot-scope="scope">
                  
                  <span :class="{'el-button--success': scope.row.die_ting_da_mian.power==35}">{{ scope.row.die_ting_da_mian.today }}</span>
              </template>
            </el-table-column>
        </el-table>
    </template>


<script>
export default {
    name: 'chuang_gn',
    props: {
        "data":{}
    }
}
</script>
