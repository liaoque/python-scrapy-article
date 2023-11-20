<template>
      <el-table
          :cell-class-name="cellClassName"
          :data="data"
          style="width: 100%">
            <el-table-column
              prop="code"
              sortable
              sort-by="code"
              label="代码"
              >
            </el-table-column>
            <el-table-column
              prop="briefname"
              label="名称"
              >
            </el-table-column>
            <el-table-column
              prop="jingjiajinetoday_s"
              sortable
              sort-by="jingjiajinetoday"
              label="竞价未匹配">
            </el-table-column>
            <el-table-column
              prop="suoshugainian"
              sortable
              sort-by="suoshugainian"
              label="所属概念">
            </el-table-column>
           
            </el-table-column>
            <el-table-column
              prop="zhangdiefuqianfuquantoday_s"
              sortable
              sort-by="zhangdiefuqianfuquantoday"
              label="涨跌幅">
            </el-table-column>
            <el-table-column
              prop="zhangdie4thday_s"
              sortable
              sort-by="zhangdie4thday"
              label="4日涨跌幅">
            </el-table-column>
             <el-table-column
              prop="jingjiajinechengjiaoliangbi_s"
              sortable
              sort-by="jingjiajinechengjiaoliangbi"
              label="竞价量比">
            </el-table-column>
             <el-table-column
              prop="jingjiajinechengjiaoliangbi_s"
              sortable
              sort-by="jingjiajinechengjiaoliangbi"
              label="今昨量比">
            </el-table-column>
             <el-table-column
              prop="lianbantianshuyesterday"
              sortable
              sort-by="lianbantianshuyesterday"
              label="昨日连板天数">
            </el-table-column>
             <el-table-column
              prop="zhangfu120_s"
              sortable
              sort-by="zhangfu120"
              label="120日涨跌幅">
            </el-table-column>
             <el-table-column
              prop="yidongcishu"
              sortable
              sort-by="yidongcishu"
              label="异动次数">
            </el-table-column>
             <el-table-column
              prop="jianguanleixingyesterday"
              sortable
              sort-by="jianguanleixingyesterday"
              label="监管">
            </el-table-column>
             <el-table-column
              prop="chuangbairixingao"
              sortable
              sort-by="chuangbairixingao"
              label="创百日新高">
            </el-table-column>
             <el-table-column
              prop="ziyouliutongshizhiyesterday_s"
              sortable
              sort-by="ziyouliutongshizhiyesterday"
              label="自由流通市值">
            </el-table-column>
        </el-table>
    
    </template>


<script>
export default {
    name: 'zhu_ban',
    props: {
        "data":[],
        "codeMap":{}
    },
    methods:{
      
      cellClassName(row){
        switch(row.column.property){
          case 'code':
            if (row["power-1"] == 35){
              return 'el-button--success'
            }
            break;
          case  'briefname':
            break;
          case 'jingjiajinetoday_s':
            break;
          case 'suoshugainian':
            codeMap[row.code]
            break;
          case  'briefname':
            break;
          case 'zhangdiefuqianfuquantoday_s':
            break;
          case 'jingjiajinechengjiaoliangbi_s':
            break;
          case  'lianbantianshuyesterday':
            break;
          case 'zhangfu120_s':
            break;
          case 'yidongcishu':
            break;
          case 'jianguanleixingyesterday':
            break;
          case 'chuangbairixingao':
            break;
          case 'ziyouliutongshizhiyesterday_s':
            break;
        }
          console.log(row)
      }
    }
}
</script>