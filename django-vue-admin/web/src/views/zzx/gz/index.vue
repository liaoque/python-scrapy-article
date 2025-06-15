<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <div class="panel">
      <!-- 日期选择器，选择后加载对应数据 -->
      <el-date-picker
        v-model="selectedDate"
        type="date"
        placeholder="选择日期"
        format="yyyy-MM-dd"
        value-format="yyyy-MM-dd"
        style="margin-bottom: 16px;"
      ></el-date-picker>

      <!-- 添加表格按钮 -->
      <el-button type="primary" @click="fetchData" style="margin-bottom: 16px;">
        搜索
      </el-button>

      <!-- 两列布局展示表格 -->
      <el-row :gutter="20" class="table-row">
        <div v-if="loading" class="loading">
          <i class="el-icon-loading"></i> 加载中...
        </div>
        <div v-if="error" class="error">{{ error }}</div>

        <el-table
          v-if="resonanceData && sortedDates.length"
          :data="tableData"
          stripe
          border
          style="width: 100%; margin-top: 20px;"
        >
          <!-- 第一列显示股票名称 -->
          <el-table-column
            prop="name"
            label="股票"
            fixed="left"
            width="180"
          />
          <!-- 动态列: 每个日期 -->
          <el-table-column
            v-for="date in sortedDates"
            :key="date"
            :prop="date"
            :label="formatDisplayDate(date)"
            align="center"
          >
            <template slot-scope="{ row }">
              <i
                v-if="row[date]"
                class="el-icon-circle-check"
                style="color: #67C23A"
              />
            </template>
          </el-table-column>
        </el-table>

        <div
          v-if="resonanceData && !sortedDates.length"
          class="no-data"
        >
          未查询到共振记录
        </div>
      </el-row>

    </div>
  </d2-container>
</template>

<script>
import * as api from './api'
import { d2CrudPlus } from 'd2-crud-plus'
import { crudOptions } from '@/views/zzx/dfcf/rq/crud'

export default {
  name: 'gz',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      selectedDate: '',
      resonanceData: null,
      loading: false,
      error: ''
    }
  },
  created () {
    // this.loadData()
  },
  computed: {
    // eslint-disable-next-line vue/no-unused-components
    sortedDates () {
      if (!this.resonanceData) return []
      // 按日期降序或你希望的顺序
      return Object.keys(this.resonanceData.resonance_pairs)
        .sort((a, b) => b.localeCompare(a))
    },
    // eslint-disable-next-line vue/no-unused-components
    tableData () {
      if (!this.resonanceData) return []
      const pairs = this.resonanceData.resonance_pairs
      const names = this.resonanceData.names
      // 收集所有在选定日期区间里出现的股票
      const codeSet = new Set()
      this.sortedDates.forEach(date => {
        (pairs[date] || []).forEach(code => codeSet.add(code))
      })
      const codes = Array.from(codeSet).sort()
      // 构造行数据
      return codes.map(code => {
        const row = { name: `${code} ${names[code] || ''}` }
        this.sortedDates.forEach(date => {
          row[date] = (pairs[date] || []).includes(code)
        })
        return row
      })
    }
    // ZhangTingDaRou: () => import('./zhang_ting_da_rou.vue'), // 这里填写实际的组件路径
    // DieTingDaMian: () => import('./die_ting_da_mian.vue'), // 这里填写实际的组件路径
    // ChuangBaiRiXinGao: () => import('./chuang_bai_ri_xin_gao.vue'), // 这里填写实际的组件路径
    // JinJingFeng: () => import('./jin_jing_feng.vue'), // 这里填写实际的组件路径
    // ShouBan: () => import('./shou_ban.vue') // 这里填写实际的组件路径
  },
  methods: {
    async fetchData () {
      this.error = ''
      if (this.selectedDate.length === 0) {
        this.error = '请先选择开始和结束日期范围'
        return
      }
      this.loading = true
      this.resonanceData = null
      try {
        const res = await api.getStockPanel({ current_time: this.selectedDate.replaceAll("-", "") })
        console.log(res)
        if (res.code === 2000) {
          this.resonanceData = res.data
        } else {
          this.error = res.msg || '接口返回错误'
        }
      } catch (e) {
        this.error = '请求失败，请检查网络或重试'
      } finally {
        this.loading = false
      }
    },
    formatDisplayDate (date) {
      return date.replace(/(\d{4})(\d{2})(\d{2})/, '$2$3')
    },
    getData (query) {

    },
    getCrudOptions () {
      return crudOptions(this)
    },
    pageRequest (query) {
      return Promise.resolve().then(() => {
        return {
          code: 0,
          msg: 'success',
          data: {}
        }
      })
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

<style scoped>
.resonance-page {
  padding: 20px;
}

.loading {
  margin: 20px 0;
  font-size: 16px;
  color: #409EFF;
}

.error {
  margin: 20px 0;
  color: #F56C6C;
}

.no-data {
  margin: 20px 0;
  color: #909399;
  text-align: center;
}
</style>
