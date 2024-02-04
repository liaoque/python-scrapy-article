<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <template slot="header">

    </template>
    <d2-container type="card">
      <el-row>
        <jj></jj>
      </el-row>
      <el-row>
        <dapan></dapan>
      </el-row>
    </d2-container>
  </d2-container>
</template>

<script>
import * as api from './api'
import {crudOptions} from './crud'
import {d2CrudPlus} from 'd2-crud-plus'

export default {
  name: 'charts',
  mixins: [d2CrudPlus.crud],
  data() {
    return {
    }
  },
  components: {
    jj: () => import('./jj.vue'), // 这里填写实际的组件路径
    dapan: () => import('./dapan.vue'), // 这里填写实际的组件路径
  },
  methods: {
    getCrudOptions () {
      return {}
    },
    pageRequest(query) {
      return api.GetList(query)
    },
    addRequest(row) {
      console.log('api', api)
      return api.AddObj(row)
    },
    updateRequest(row) {
      console.log('----', row)
      return api.UpdateObj(row)
    },
    delRequest(row) {
      return api.DelObj(row.id)
    }
  }
}
</script>
