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
        @change="onDateChange"
        style="margin-bottom: 16px;"
      ></el-date-picker>

      <!-- 添加表格按钮 -->
      <el-button type="primary" @click="addTable" style="margin-bottom: 16px;">
        + 添加表格
      </el-button>

      <!-- 两列布局展示表格 -->
      <el-row :gutter="20" class="table-row">
        <el-col :span="24" v-for="(table, tIdx) in tables" :key="table.id">
          <el-card class="table-wrapper">
            <div slot="header" class="table-header">
              <!-- 可编辑表格标题 -->
              <el-input
                v-model="table.title"
                size="small"
                placeholder="表格标题"
                style="width: 140px;"
              />
              <el-button type="danger" size="mini" @click="removeTable(tIdx)">
                删除
              </el-button>
            </div>

            <!-- 股票数据表格 -->
            <el-table :data="table.rows" stripe border size="small" style="width: 100%;">
              <!-- 股票代码 -->
              <el-table-column label="股票代码" width="140">
                <template slot-scope="scope">
                  <el-input
                    v-model="scope.row.code"
                    size="small"
                    @blur="onCodeBlur(table, scope.row)"
                    placeholder="输入代码后失焦"
                  />
                </template>
              </el-table-column>
              <!-- 股票名字 -->
              <el-table-column prop="name" label="股票名字" width="120"/>
              <!-- 预期（自动计算，保留2位小数） -->
              <el-table-column prop="expected" label="预期" width="100"/>
              <!-- 开盘 -->
              <el-table-column prop="open" label="开盘" width="100">
                <template #default="{ row }">
                  <span>
                    {{ row.open }}
                  </span>
                </template>
              </el-table-column>
              <!-- 正确/错误（程序自动检测） -->
              <el-table-column prop="programResult" label="正确/错误" width="120" class="text-red">
                <template #default="{ row }">
                <span class="text-red" :class="{'text-green': isLow(row.programResult) }">
                  {{ row.programResult }}
                </span>
                </template>
              </el-table-column>
              <!-- 判定（人工核对） -->
              <el-table-column label="判定" width="100">
                <template slot-scope="scope">
                  <el-select v-model="scope.row.judge" size="small" placeholder="请选择">
                    <el-option label="正确" value="正确"/>
                    <el-option label="错误" value="错误"/>
                  </el-select>
                </template>
              </el-table-column>

              <el-table-column prop="notice" label="备注" width="100">
                <template slot-scope="scope">
                  <el-input
                    v-model="scope.row.notice"
                    size="small"
                  />
                </template>
              </el-table-column>

              <!-- 操作 -->
              <el-table-column label="操作" width="100">
                <template slot-scope="scope">
                  <el-button type="danger" size="mini" @click="removeRow(table, scope.$index)">
                    删除
                  </el-button>
                </template>
              </el-table-column>

            </el-table>

            <!-- 添加股票按钮 -->
            <div style="text-align: right; margin-top: 10px;">
              <el-button type="success" size="mini" @click="addRow(table)">
                + 添加股票
              </el-button>
            </div>
          </el-card>
        </el-col>
      </el-row>

    </div>
  </d2-container>
</template>

<style scoped>
.text-red {
  color: red;
}

.text-green {
  color: green;
}

.panel {
  padding: 16px;
}

.table-row {
  margin-top: 16px;
}

.table-wrapper {
  padding: 12px;
}

.table-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>

<script>
import * as api from './api'
import { d2CrudPlus } from 'd2-crud-plus'
import { crudOptions } from '@/views/zzx/dfcf/rq/crud'
import {getStockPanel, saveStockPanel} from './api'

export default {
  name: 'yq',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      tables: [],
      selectedDate: new Date().toISOString().split('T')[0]
    }
  },
  created () {
    this.loadData()
  },
  watch: {
    // 当表格数据变化时，自动保存
    tables: {
      handler () {
        this.saveData()
      },
      deep: true
    },
    // 切换日期时加载对应数据
    selectedDate (newDate, oldDate) {
      if (newDate !== oldDate) {
        this.loadData()
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
    isLow (result) {
      // 确保 result 是字符串
      if (typeof result !== 'string') return false
      return result.indexOf('低') > -1
    },
    uuid () {
      return Date.now().toString(36) + Math.random().toString(36).substr(2)
    },
    // 切换日期触发
    onDateChange () {
      // loadData 已在 watcher 处理
    },
    // 从 localStorage 读取对应日期的数据
    loadData () {
      api.getStockPanel({
        current_time: this.selectedDate
      }).then(res => {
        console.log(res)
        this.tables = res.data
      })
    },
    // 保存当前选中日期的数据到 localStorage
    saveData () {
      api.saveStockPanel({
        current_time: this.selectedDate,
        data: this.tables
      }).then(res => {
        console.log(res)
        //  this.tables = res.data
      })
    },
    addTable () {
      this.tables.push({
        id: this.uuid(),
        title: `表格 ${this.tables.length + 1}`,
        rows: []
      })
    },
    removeTable (idx) {
      this.tables.splice(idx, 1)
    },
    addRow (table) {
      table.rows.push({
        id: this.uuid(),
        code: '',
        name: '',
        expected: '',
        open: '',
        notice: '',
        programResult: ''
      })
    },
    removeRow (table, idx) {
      table.rows.splice(idx, 1)
    },
    async onCodeBlur (table, row) {
      if (!row.code) return
      try {
        const list = await this.fetchStockInfo(row.code)
        list.sort((a, b) => new Date(a.date) - new Date(b.date))
        // 找到当前日期项及前一日项
        const idx = list.findIndex(item => item.date === this.selectedDate)
        if (idx === -1 || idx === 0) {
          throw new Error('无有效历史数据')
        }

        const today = list[idx]
        const prev = list[idx - 1]
        const prevprev = list[idx - 2]
        // 填充名称与开盘
        row.name = today.name || ''
        row.open = today.open
        // 预期计算： (前日成交量 - 当日成交量)/当日成交量 * 当日涨幅

        let buckets = [
          { s: -10, e: -7, label: '远低于预期' },
          { s: -7, e: -3, label: '较低于预期' },
          { s: -3, e: 0, label: '低于预期' },
          { s: 0, e: 3, label: '符合预期' },
          { s: 3, e: 7, label: '高于预期' },
          { s: 7, e: 10, label: '远高于预期' }
        ]

        let changePercent = 10
        if (row.code.substr(0, 3) === '300' || row.code.substr(0, 3) === '688') {
          buckets = buckets.map(res => {
            res.s *= 2
            res.e *= 2
            return res
          })
          changePercent = 20
        } else if (row.code.substr(0, 1) === '8') {
          buckets = buckets.map(res => {
            res.s *= 2
            res.e *= 2
            return res
          })
          changePercent = 30
        }

        const expectedVal = ((prevprev.volume - prev.volume) / prevprev.volume) * changePercent
        row.expected = expectedVal.toFixed(2)
        // 程序检测：预期与开盘接近, 差值/预期 <=5%
        // const diffRatio = Math.abs(row.open - expectedVal) / Math.abs(expectedVal)
        // const diff = row.open - expectedVal
        console.log('<UNK>', expectedVal)

        let label = '超出范围'
        const idx2 = buckets.findIndex(item => item.s <= expectedVal && expectedVal < item.e)
        if (idx2 === 0) {
          if (row.open >= buckets[0].s) {
            label = '符合预期'
          }

          if (row.open >= buckets[1].s) {
            label = '高于预期'
          }

          if (row.open >= buckets[2].s) {
            label = '超预期'
          }
        } else if (idx2 === 5) {
          if (row.open >= buckets[5].s) {
            label = '符合预期'
          }

          if (row.open >= buckets[4].s) {
            label = '低于预期'
          }

          if (row.open >= buckets[3].s) {
            label = '远低于预期'
          }
        } else if (row.open >= buckets[idx2 + 1].s) {
          label = '符合预期'
        } else if (row.open >= buckets[idx2 + 2].s) {
          label = '超预期'
        } else if (row.open >= buckets[idx2 - 1].s) {
          label = '低于预期'
        } else if (row.open >= buckets[idx2 - 2].s) {
          label = '远低于预期'
        } else {
          label = '符合预期'
        }

        row.programResult = label
      } catch {
        row.name = '获取失败'
      }
    },
    fetchStockInfo (code) {
      // TODO: 替换为真实接口
      return api.GetGjList(code)
    },
    // 计算人工判定：如果程序检测结果与“开盘>=预期”一致，则对，否则错
    computeJudge (row) {
      debugger
      const expectedNum = parseFloat(row.expected)
      const openNum = parseFloat(row.open)
      if (isNaN(expectedNum) || isNaN(openNum) || !row.programResult) {
        return ''
      }
      const actualTrend = openNum >= expectedNum // true 表示开盘>=预期
      const programDetect = String(row.programResult) === 'true'
      return actualTrend === programDetect ? '对' : '错'
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
