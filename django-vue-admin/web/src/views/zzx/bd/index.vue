<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <el-row>
      <el-col :span="12">
        <el-row>
          <el-col :span="24/left.bd.length"    v-for="(bd,index) in left.bd" :key="index" >
              <p >{{bd.title}}</p>
              <p v-for="(item,index2) in bd.data" :key="index2">{{item.name}}</p>
          </el-col>
        </el-row>
      </el-col>
      <el-col :span="12" >
        <div class="grid-content bg-purple-light"></div>
      </el-col>
    </el-row>

  </d2-container>
</template>

<script>
import * as api from './api'
import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'bangdan',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
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
