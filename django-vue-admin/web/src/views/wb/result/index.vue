<template>
  <d2-container >
    <el-row>
      <el-col :span="2" >
        情绪:
      </el-col>
      <el-col :span="2" >
        补涨:
      </el-col>
      <el-col :span="2" >
        阈值:
      </el-col>
      <el-col :span="2" >
        昨标高: 
      </el-col>
       <el-col :span="2" >
        风口: 
      </el-col>
      <el-col :span="2" >
        炸板率: 
      </el-col>
       <el-col :span="2" >
        竞涨停: 
      </el-col>
      <el-col :span="2" >
        竞跌停: 
      </el-col>
      <el-col :span="2" >
        收涨停: 
      </el-col>
      <el-col :span="2" >
        收跌停: 
      </el-col>
       <el-col :span="2" >
        竞上涨: 
      </el-col>
      <el-col :span="2" >
        竞下跌: 
      </el-col>
      <el-col :span="2" >
        收上涨: 
      </el-col>
      <el-col :span="2" >
        收下跌: 
      </el-col>
    </el-row>
   
    <el-tabs v-model="activeName" >
      <el-tab-pane label="创业板概念" name="first">
        <chuangGn :data=plan.chuang_ye_ban_gai_nian ></chuangGn>
        

      </el-tab-pane>

      <el-tab-pane label="主板" name="second">
        <zhu :data=plan.zhu_ban :codeMap=codeMap></zhu>
      </el-tab-pane>

      <el-tab-pane label="创业板" name="third">
         <zhu :data=plan.chuang_ye_ban :codeMap=codeMap ></zhu>
      </el-tab-pane>

    </el-tabs>

  </d2-container>
</template>

<script>
import * as api from './api'
import { crudOptions } from './crud'
import { d2CrudPlus } from 'd2-crud-plus'

import chuangGn from './chuang_gn.vue';
import zhu from './zhu.vue';

export default {
  name: 'result',
  mixins: [d2CrudPlus.crud],
  components:{
    chuangGn,
    zhu
  },
  data () {
    return {
        activeName:"first",
        pickerOptions: {
          value:"",
          shortcuts: [{
            text: '今天',
            onClick(picker) {
              picker.$emit('pick', new Date());
            }
          }, {
            text: '昨天',
            onClick(picker) {
              const date = new Date();
              date.setTime(date.getTime() - 3600 * 1000 * 24);
              picker.$emit('pick', date);
            }
          }, {
            text: '一周前',
            onClick(picker) {
              const date = new Date();
              date.setTime(date.getTime() - 3600 * 1000 * 24 * 7);
              picker.$emit('pick', date);
            }
          }]
        },
      
        "plan":{
          "chuang_ye_ban_gai_nian":[],
          "zhu_ban":[],
          "chuang_ye_ban":[]
        },
        codeMap:{
          "zhu":{},
          "chuang":{}
        }
    }
  },
  methods: {
    
    getCrudOptions () {
      let self = this
      api.GetResult().then(function (params) {

        self.plan.chuang_ye_ban_gai_nian = params.data.chuang_ye_ban_gn.map((item)=>{

            let today = (Math.ceil(item.chuang_bai_ri_xin_gao.today/1000000)/100).toFixed(2)
            let yeasterday = (Math.ceil(item.chuang_bai_ri_xin_gao.yesterday/1000000)/100).toFixed(2)
            item.jin_zuo_bai_ri_xin_gao = item.chuang_bai_ri_xin_gao.count + "|" + today + "|"+ yeasterday


            today = (Math.ceil(item.jin_jing_feng.today/1000000)/100).toFixed(2)
            yeasterday = (Math.ceil(item.jin_jing_feng.yesterday/1000000)/100).toFixed(2)
            item.jin_zuo_jin_jing_feng = today + "|"+ yeasterday

            item.liu_tong_shi_zhi_s = (Math.ceil(item.liu_tong_shi_zhi/1000000) / 100).toFixed(2)
            item.die_ting_da_mian.today = (Math.ceil(item.die_ting_da_mian.today/1000000) / 100).toFixed(2)
            return item
        }).sort((a, b)=>{
                if(a.jin_jing_feng_count.count > b.jin_jing_feng_count.count) { return -1; }
                if(a.jin_jing_feng_count.count < b.jin_jing_feng_count.count) { return 1; }
                return 0;
        })

        self.plan.zhu_ban = params.data.zhu_data.map((item)=>{
            self.codeMap.zhu[item["code"]] = item
            item.jingjiajinetoday_s = (Math.ceil(item.jingjiajinetoday/1000000) / 100).toFixed(2)
            item.zhangtingfengdanetoday_s = (Math.ceil(item.zhangtingfengdanetoday/1000000) / 100).toFixed(2)
            item.zhangfu5_s = (Math.ceil(item.zhangfu5*100) / 100).toFixed(2)
            item.zhangdie4thday_s = (Math.ceil(item.zhangdie4thday*100) / 100).toFixed(2)
            item.zhangfu120_s = (Math.ceil(item.zhangfu120*100) / 100).toFixed(2)
            item.jingjiajinechengjiaoliangbi_s = (Math.ceil(item.jingjiajinechengjiaoliangbi*100) ).toFixed(2)
            item.ziyouliutongshizhiyesterday_s = (Math.ceil(item.ziyouliutongshizhiyesterday/1000000) / 100).toFixed(2)
            item.zhangdiefuqianfuquantoday_s = (Math.ceil(item.zhangdiefuqianfuquantoday*100) / 100).toFixed(2)
            item.jingjiajinejingjialiangbi_s = (Math.ceil(item.jingjiajinejingjialiangbi*100) / 100).toFixed(2)

            return item
        }).sort((a, b)=>{
            if(a.zhangfu120 > b.zhangfu120) { return -1; }
            if(a.zhangfu120 < b.zhangfu120) { return 1; }
            return 0;
        })

        self.plan.chuang_ye_ban = params.data.chuang_data.map((item)=>{
            self.codeMap.chuang[item["code"]] = item
            item.jingjiajinetoday_s = (Math.ceil(item.jingjiajinetoday/1000000) / 100).toFixed(2)
            item.zhangtingfengdanetoday_s = (Math.ceil(item.zhangtingfengdanetoday/1000000) / 100).toFixed(2)
            item.zhangfu5_s = (Math.ceil(item.zhangfu5*100) / 100).toFixed(2)
            item.zhangdie4thday_s = (Math.ceil(item.zhangdie4thday*100) / 100).toFixed(2)
            item.zhangfu120_s = (Math.ceil(item.zhangfu120*100) / 100).toFixed(2)
            item.jingjiajinechengjiaoliangbi_s = (Math.ceil(item.jingjiajinechengjiaoliangbi*100) ).toFixed(2)+ "%"
            item.ziyouliutongshizhiyesterday_s = (Math.ceil(item.ziyouliutongshizhiyesterday/1000000) / 100).toFixed(2)
            item.zhangdiefuqianfuquantoday_s = (Math.ceil(item.zhangdiefuqianfuquantoday*100) / 100).toFixed(2) + "%"
            item.jingjiajinejingjialiangbi_s = (Math.ceil(item.jingjiajinejingjialiangbi*100) / 100).toFixed(2) + "%"
          
            return item
        }).sort((a, b)=>{
            if(a.zhangfu120 > b.zhangfu120) { return -1; }
            if(a.zhangfu120 < b.zhangfu120) { return 1; }
            return 0;
        })
        
      })
      return []
    },
    pageRequest (query) {
      return api.GetList(query)
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

<style>
.green{
  background-color:#67C23A;
}
.red{
  background-color:red;
}
</style>
