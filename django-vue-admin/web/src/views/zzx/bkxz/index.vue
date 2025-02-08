<template>
  <d2-container :class="{ 'page-compact': crud.pageOptions.compact }">
    <el-row>
      <el-col :span="12">
        <el-table
          :data="left.bk"
          style="width: 100%">

          <el-table-column
            prop="name"
            label="名字"
            width="60">
          </el-table-column>

          <el-table-column
            prop="qd"
            label="当前强度"
            width="60">
          </el-table-column>

          <el-table-column
            prop="je"
            label="区间净额"
            width="60">
          </el-table-column>

          <el-table-column
            prop="zt"
            label="涨停数量"
            width="60">
          </el-table-column>

        </el-table>
      </el-col>
      <el-col :span="12" >
        <div class="grid-content bg-purple-light"></div>
      </el-col>
    </el-row>

<!--    <el-table-->
<!--      default-expand-all="true"-->
<!--      :data="right.data"-->
<!--      style="width: 100%">-->
<!--      -->

<!--    </el-table>-->

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
// 板块强度
export default {
  name: 'bkxz',
  mixins: [d2CrudPlus.crud],
  data () {
    return {
      ws: {
        url: 'wss://duanxianxia.com/wss1',
        sock: null
      },
      right: {

      },
      left: {
        bk: []
      }
    }
  },
  components: {
  },
  methods: {
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
    initWs () {
      if (this.ws.sock) {
        return
      }
      this.ws.sock = new WebSocket(this.ws.url)
      this.ws.sock.onmessage = (message) => {
        const data = JSON.parse(message.data)
        console.log('onmessage', data)
        // this.left.bk = data.list.map(item => {
        //   return {
        //     name: item[1],
        //     qd: item[2],
        //     code: item[3],
        //     je: this.formatNumber(item[4]),
        //     zt: item[5]
        //   }
        // })
      }
      this.ws.sock.onclose = () => {
        console.log('onclose')
      }
      this.ws.sock.onopen = () => {
        console.log('onopen')
      }
    },

    pageRequest (query) {
      this.initWs()


      console.log(query)
      return []
    },
    addRequest (row) {
      console.log('api', api)
      return {}
    },
    updateRequest (row) {
      console.log('----', row)
      return {}
    },
    delRequest (row) {
      return {}
    },
    formatNumber (num) {
      if (typeof num !== 'number') {
        throw new Error('Input must be a number')
      }

      const absNum = Math.abs(num)
      let result

      if (absNum >= 1e8) {
        result = (num / 1e8).toFixed(3) + '亿'
      } else if (absNum >= 1e4) {
        result = (num / 1e4).toFixed(3) + '万'
      } else {
        result = num.toFixed(3)
      }

      return result
    }
  }
}
</script>
