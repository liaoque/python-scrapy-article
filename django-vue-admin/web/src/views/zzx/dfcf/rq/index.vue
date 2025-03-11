<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">

    </template>
    <d2-container type="card">
      <el-row>
        <gp></gp>
      </el-row>
      <el-row>
<!--        <dapan></dapan>-->
      </el-row>
    </d2-container>
  </d2-container>
</template>

<script>
import * as api from './api'
import {d2CrudPlus} from 'd2-crud-plus'

export default {
  name: 'dfcf_rq',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
    }
  },
  components: {
    gp: () => import('./gp.vue'), // 这里填写实际的组件路径
    // dapan: () => import('./dapan.vue'), // 这里填写实际的组件路径
  },
  methods: {
    getCrudOptions () {
      return {}
    },
    pageRequest(query) {
      return {}
    },
    addRequest(row) {
      console.log('api', api)
      return {}
    },
    updateRequest(row) {
      console.log('----', row)
      return {}
    },
    delRequest(row) {
      return {}
    }
  }
}
</script>
