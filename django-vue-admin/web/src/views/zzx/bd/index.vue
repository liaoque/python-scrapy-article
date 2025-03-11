<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <el-row>
      <el-col :span="24">
        <el-row>
          <el-col :span="24/left.bd.length"    v-for="(bd,index) in left.bd" :key="index" >
            <el-table
              :data="bd.data"
              style="width: 100%">
              <el-table-column
                :label="bd.title"
                width="180">
                <template slot-scope="scope">
                  <i >{{ scope.$index + 1 }}</i>
                  <span style="margin-left: 10px" @click="selectBd(bd, index)" >{{ scope.row.name }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-col>
        </el-row>
      </el-col>
<!--      <el-col :span="12" >-->
<!--        <div class="grid-content bg-purple-light"></div>-->
<!--      </el-col>-->
    </el-row>

    <el-drawer
      :title="right.title"
      :visible.sync="right.drawer"
      :direction="right.direction"
      size="70%"
     >
      <el-table
        default-expand-all="true"
        :data="right.data"
        style="width: 100%">
        <el-table-column
          type="index"
          label="人气"
          width="50">
        </el-table-column>
        <el-table-column
          prop="code"
          label="代码"
          width="60">
        </el-table-column>
        <el-table-column
          prop="name"
          label="名称"
          width="100">
        </el-table-column>
        <el-table-column
          prop="fudu"
          label="涨幅"
          width="60">
        </el-table-column>
        <el-table-column
          prop="rank"
          label="总分"
          width="60">
        </el-table-column>
        <el-table-column
          prop="change_rank"
          label="升降"
          width="60">
          <template slot-scope="scope">
            <span >{{scope.row.change_rank}}</span>
            <i :class='{
              "el-icon-top": parseInt(scope.row.change_rank) > 0,
             "el-icon-bottom": parseInt(scope.row.change_rank) < 0,
            }'
            :style="{ color: parseInt(scope.row.change_rank) > 0 ? '#F56C6C' : (parseInt(scope.row.change_rank) === 0 ? '': '#67C23A')}"></i>
          </template>
        </el-table-column>
        <el-table-column
          prop="bk"
          label="板块"
          width="180">
        </el-table-column>
        <el-table-column
          prop="riseDay"
          label="版状态"
          width="60">
        </el-table-column>
        <el-table-column
          label="题材"
          type="expand">
          <template slot-scope="scope">
            <div>{{scope.row.reason}}</div>
          </template>
        </el-table-column>

      </el-table>
    </el-drawer>

  </d2-container>
</template>

<style scoped>
.green{
  color: #67C23A;
}
.red{
  color: #F56C6C;
}
</style>

<script>
import * as api from './api'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'bangdan',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      right: {
        index: -1,
        drawer: false,
        direction: 'rtl',
        title: '',
        data: []
      },
      left: {
        bd: [
          {
            name: 'tdx',
            title: '通达信',
            data: []
          },
          {
            name: 'dfcf',
            title: '东方财富',
            data: []
          },
          {
            name: 'ths',
            title: '同花顺',
            data: []
          }
        ]
      }
    }
  },
  components: {
    // ZhangTingDaRou: () => import('./zhang_ting_da_rou.vue'), // 这里填写实际的组件路径
    // DieTingDaMian: () => import('./die_ting_da_mian.vue'), // 这里填写实际的组件路径
    // ChuangBaiRiXinGao: () => import('./chuang_bai_ri_xin_gao.vue'), // 这里填写实际的组件路径
    // JinJingFeng: () => import('./jin_jing_feng.vue'), // 这里填写实际的组件路径
    // ShouBan: () => import('./shou_ban.vue') // 这里填写实际的组件路径
  },
  methods: {
    selectBd (bg, index) {
      this.right.drawer = true
      this.right.index = index
      this.right.title = bg.title
      this.right.data = bg.data
      console.log(bg, index)
    },
    getToday () {
      const today = new Date()
      const year = today.getFullYear()
      const month = (today.getMonth() + 1).toString().padStart(2, '0') // 添加前导零
      const day = today.getDate().toString().padStart(2, '0') // 添加前导零
      const ymd = `${year}${month}${day}`
      this.today = ymd
      return ymd
    },
    getData (query) {

    },
    getCrudOptions () {
      return {
        pageOptions: {
          compact: true
        },
        options: {
          height: '100%'
        },
        viewOptions: {
          componentType: 'row'
        },
        formOptions: {
          defaultSpan: 12 // 默认的表单 span
        },
        columns: [

        ]
      }
    },
    pageRequest (query) {
      for (const key in this.left.bd) {
        api.GetList({ name: this.left.bd[key].name }).then(res => {
          // console.log(res)
          this.left.bd[key].data = res.data
        })
      }
      console.log(query)
      return []
    },
    addRequest (row) {
      console.log('api', api)
      return api.AddObj(row)
    },
    updateRequest (row) {
      console.log('----', row)
      return api.UpdateObj(row)
    },
    delRequest (row) {
      return api.DelObj(row.id)
    }
  }
}
</script>
