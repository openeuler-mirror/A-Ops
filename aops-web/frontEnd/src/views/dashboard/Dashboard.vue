<template>
  <my-page-header-wrapper>
    <div style="width: 100%;height: 200px">
      <div style="width: 250px;height:100%;float: left;">
        <div style="width: 100%;height: calc(50% - 5px);background: #fff">
          <div style="height: 100%;width: 85px;float: left;position:relative;">
            <a-avatar :size="64" icon="database" style="background: #1890ee;position: absolute;top: 50%;left: 50%;margin-top: -32px;margin-left: -32px"/>
          </div>
          <div style="height: 100%;width: calc(100% - 100px);float: left;position:relative;">
            <div class="content">
              <div style="color: #999;">主机数量<a-icon type="question-circle" style="float: right"/></div>
              <div style="color: #333;font-size: 32px;line-height: 1em">{{ hostCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')}}</div>
            </div>
          </div>
        </div>
        <div style="width: 100%;height: calc(50% - 5px);background: #fff;margin-top: 10px">
          <div style="height: 100%;width: 85px;float: left;position:relative;">
            <a-avatar :size="64" icon="database" style="background: #1890ee;position: absolute;top: 50%;left: 50%;margin-top: -32px;margin-left: -32px"/>
          </div>
          <div style="height: 100%;width: calc(100% - 100px);float: left;position:relative;">
            <div class="content">
              <div style="color: #999;">异常检测规则数量<a-icon type="question-circle" style="float: right"/></div>
              <div style="color: #333;font-size: 32px;line-height: 1em">{{ ruleCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')}}</div>
            </div>
          </div>
        </div>
      </div>
      <div style="width: 250px;height:100%;float: left;background: #fff;margin-left: 10px;padding: 15px 20px;">
        <div style="color: #999;">业务域同步率<a-icon type="question-circle" style="float: right"/></div>
        <div style="font-size: 32px;padding-left: 15px;line-height: 45px">78%</div>
        <div><a-progress :percent="78" :show-info="false" :strokeWidth="12" :strokeColor="'#1890ee'"/></div>
        <div style="border-top: 1px solid #ccc;margin-top: 15px;color: #999;padding-top: 5px">未同步业务域</div>
        <div style="font-size: 32px;padding-left: 15px;line-height: 45px;color: #FA5151">{{ '1345'.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')}}</div>
      </div>
      <drawer-view title="异常检测结果统计">
        <template slot="click">
          <div class="showAllResult">查看全部结果</div>
        </template>
        <template slot="drawerView">
          <get-check-result-drawer></get-check-result-drawer>
        </template>
      </drawer-view>
      <div style="width: calc(100% - 555px);height: 100%;float: right;background: #fff;padding: 5px;padding-top: 10px">
        <a-row style="width: 100%;height: 100%">
          <a-col style="height: 100%;" :span="12">
            <div style="width: 100%;height: 40%;">
              <div style="padding-left: 20px;font-size: 18px;line-height: 40px;height: calc(100% - 30px);color: #000;font-weight: bold">异常检测结果统计</div>
              <a-row style="color: #999;line-height: 30px">
                <a-col :span="3" style="text-align: center">排名</a-col>
                <a-col :span="15">主机名IP地址</a-col>
                <a-col :span="6">异常数</a-col>
              </a-row>
            </div>
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(0, 3)" :key="index">
              <a-col :span="3"><a-tag style="background: #1890ee;color: #fff;border-color:#1890ee">{{ index+1 }}</a-tag></a-col>
              <a-col :span="15">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6" style="color: #ff58ab">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
          <a-col style="float: left;height: 100%;" :span="12">
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(3, 8)" :key="index">
              <a-col :span="3"><a-tag>{{ index+4 }}</a-tag></a-col>
              <a-col :span="15">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
        </a-row>
      </div>
    </div>
    <a-card style="width: 100%;float: left;margin-top: 10px">
      <div style="font-weight: bold;font-size: 18px;margin-top: -12px;margin-bottom: 10px">异常检测记录</div>
      <a-table
        rowKey="host_id"
        :columns="columns"
        :data-source="resultList"
        :pagination="false"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="3">
        <div slot="expandedRowRender" slot-scope="result" style="width: 100%;margin: 1px;padding-left: 50px;">
          <check-result-expanded :dataSource="result.data_list"></check-result-expanded>
        </div>
      </a-table>
      <div style="margin-top: 10px;text-align: right;">
        <router-link :to="{ path: '/diagnosis/abnormal-check' }" target="_blank">
          <a style="cursor: pointer;border-bottom: 1px solid;padding: 0 3px 1px">查看更多异常检测记录<a-icon type="right" style="line-height: 30px;padding-left: 3px"/></a>
        </router-link>
      </div>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import DrawerView from '@/views/utils/DrawerView'
import GetCheckResultDrawer from '@/views/diagnosis/components/GetCheckResultDrawer'
import AddAbnormalCheckRuleDrawer from '@/views/diagnosis/components/AddAbnormalCheckRuleDrawer'
import CheckResultExpanded from '@/views/diagnosis/components/CheckResultExpanded'
import { getRuleCount, getResultCountTopTen, getResult } from '@/api/check'
import { hostCount } from '@/api/assest'
import { dateFormat } from '@/views/utils/Utils'

export default {
  name: 'Dashboard',
  components: {
    MyPageHeaderWrapper,
    DrawerView,
    AddAbnormalCheckRuleDrawer,
    GetCheckResultDrawer,
    CheckResultExpanded
  },
  mounted: function () {
    this.getRuleCount()
    this.getHostCount()
    this.getResultCountTopTen()
    this.getResultList()
  },
  data () {
    return {
      hostCount: 0,
      ruleCount: 0,
      filters: null,
      sorter: null,
      tableIsLoading: false,
      columns,
      resultCountList: [],
      resultList: []
    }
  },
  methods: {
    getHostCount () {
      var that = this
      hostCount().then(function (data) {
        that.hostCount = data.host_count
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      })
    },
    getRuleCount () {
      var that = this
      getRuleCount().then(function (data) {
        that.ruleCount = data.rule_count
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      })
    },
    getResultCountTopTen () {
      var that = this
      getResultCountTopTen().then(function (data) {
        that.resultCountList = data.results
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      })
    },
    getResultList () {
      var that = this
      getResult({ perPage: 5 }).then(function (data) {
        that.resultList = data.check_result
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      })
    }
  }
}

const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    key: 'index',
    align: 'center',
    width: 70,
    customRender: (text, record, index) => `${index + 1}`
  },
  {
    dataIndex: 'hostName',
    key: 'hostName',
    title: '主机名称'
  },
  {
    dataIndex: 'ip',
    key: 'ip',
    title: 'IP地址'
  },
  {
    dataIndex: 'check_item',
    key: 'check_item',
    title: '检测项'
  },
  {
    dataIndex: 'condition',
    key: 'condition',
    title: '检测条件'
  },
  {
    dataIndex: 'value',
    key: 'value',
    title: '检测结果'
  },
  {
    title: '检测时间段',
    customRender: (text, record, index) => dateFormat('YYYY-mm-dd HH:MM:SS', record.start * 1000) + ' 至 ' + dateFormat('YYYY-mm-dd HH:MM:SS', record.end * 1000)
  }
]

</script>

<style lang="less" scoped>
.content{position: absolute;width: 100%;height: 60px;top: 50%;margin-top: -30px;padding-left: 5px}
.myBtn{width: calc(50% - 1px);height: 100%;background:#1890ee;text-align: center;cursor: pointer}
.myBtn:hover{background: #0075d0;}
.showAllResult{width: 35px;height: 100%;background:#1890ee;float: right;border: 1px solid #fff;color: #fff;padding: 15px 5px;text-align: center;cursor: pointer}
.showAllResult:hover{background: #0075d0;}
.myRow{height: calc(20% - 5px);width: 100%;margin-bottom:5px}
.myRow>.ant-col:nth-child(1){position: relative;height: 100%}
.myRow>.ant-col:nth-child(1) .ant-tag{border-radius: 50%;padding: 0 1px 0 0;width: 24px;height: 24px;line-height: 22px;text-align: center;position: absolute;top: 50%;left: 50%;margin-top: -12px;margin-left: -12px}
.myRow>.ant-col:nth-child(2){line-height: 1.2em!important;}
.myRow>.ant-col:nth-child(3){line-height: 30px}
</style>
