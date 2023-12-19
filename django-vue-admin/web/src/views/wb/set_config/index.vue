<template>
  <d2-container>
    <el-form ref="form" :model="form" label-width="80px">
      <el-form-item label="过滤概念">
        <el-input type="textarea"  v-model="form.gvgn"></el-input>
      </el-form-item>
      <el-form-item label="设置值1">
        <el-input v-model="form.chuang_ye_set"></el-input>
      </el-form-item>
      <el-form-item label="设置值2">
        <el-input v-model="form.zhu_set"></el-input>
      </el-form-item>
      <el-form-item label="10CM">
        <el-input v-model="form.cm10"></el-input>
      </el-form-item>
      <el-form-item label="20CM">
        <el-input v-model="form.cm20"></el-input>
      </el-form-item>
      <el-form-item label="连板股票">
        <el-input type="textarea"  v-model="form.lian_ban_code_black"></el-input>
      </el-form-item>
      <el-form-item>
        <el-button type="primary" @click="onSubmit">保存成功</el-button>
        <el-button>取消</el-button>
      </el-form-item>
    </el-form>

  </d2-container>
</template>

<script>
import * as api from './api'
// import { crudOptions } from './crud'
// import { d2CrudPlus } from 'd2-crud-plus'
export default {
  name: 'set_config',
  // mixins: [d2CrudPlus.crud],
  data () {
    return {
      form: {
        gvgn: "",
        chuang_ye_set: 0,
        zhu_set: 0,
        cm10: 0,
        cm20: 0,
        lian_ban_code_black: ""
      }
    }
  },
  methods: {
    onSubmit () {
      // this.form
      // console.log(this.form.gvgn)
      api.UpdateObj({
        gvgn: this.form.gvgn.split(','),
        chuang_ye_set: this.form.chuang_ye_set,
        zhu_set: this.form.zhu_set,
        cm10: this.form.cm10,
        cm20: this.form.cm20,
        lian_ban_code_black: this.form.lian_ban_code_black.split(',')
      }).then(res=>{
        alert("保存成功")
      })
    },

    pageRequest () {
      const self = this
      return api.GetCascadeData().then(res => {
        res.data.gvgn = res.data.gvgn.join(",")
        res.data.lian_ban_code_black = res.data.lian_ban_code_black.join(",")
        self.form = res.data
      })
    },

    updateRequest (row) {
      return api.UpdateObj(row)
    }
  },
  mounted () {
    this.pageRequest()
  }
}
</script>
