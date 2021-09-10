
<template>
  <my-page-header-wrapper>
    <a-row class="topBox">
      <a-col span="24" :xl="5" class="topItem">
        <div style="height: calc(100% - 35px);padding: 15px 10px;">
          <div style="height: 100%;width:calc(40% - 5px);margin-right: 5px; float: left;position:relative;overflow: hidden">
            <a-avatar :size="64" icon="database" style="background: #1890ee;position: absolute;top: 50%;left: 50%;margin-top: -32px;margin-left: -32px"/>
          </div>
          <div style="height: 100%;width:60%;float: left;position:relative;">
            <div class="content">
              <div style="color: #999;">异常检测规则数量</div>
              <div style="color: #333;font-size: 32px;line-height: 1em">{{ ruleCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,') }}</div>
            </div>
          </div>
        </div>
        <div style="width: 100%;height: 34px;line-height: 32px;color: #fff;padding-left:2px">
          <drawer-view title="新建异常检测规则">
            <template slot="click">
              <div class="newRule" style="float: left">
                <a-icon type="file-add" style="margin-right: 5px"/>新建规则
              </div>
            </template>
            <template slot="drawerView">
              <add-abnormal-check-rule-drawer :addSuccess="getRuleList"></add-abnormal-check-rule-drawer>
            </template>
          </drawer-view>
        </div>
      </a-col>
      <a-col span="24" :xl="19" class="topItem">
        <a-row style="width: calc(100% - 45px);height: 100%;padding:10px 5px 5px;margin-left: 10px;background: #fff; float: left">
          <a-col style="height: 100%;" :span="8">
            <div style="width: 100%;height: 40%;">
              <div style="padding-left: 20px;font-size: 18px;line-height: 40px;height: calc(100% - 30px);color: #000;font-weight: bold">异常检测结果统计</div>
              <a-row style="color: #999;line-height: 30px">
                <a-col :span="4" style="text-align: center" class="oneRow">排名</a-col>
                <a-col :span="14" class="oneRow">主机名IP地址</a-col>
                <a-col :span="6" class="oneRow">异常数</a-col>
              </a-row>
            </div>
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(0, 2)" :key="index">
              <a-col :span="4"><a-tag style="background: #1890ee;color: #fff;border-color:#1890ee">{{ index+1 }}</a-tag></a-col>
              <a-col :span="14">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6" style="color: #ff58ab" class="oneRow">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
          <a-col style="float: left;height: 100%;" :span="8">
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(2, 6)" :key="index">
              <a-col :span="4"><a-tag>{{ index+3 }}</a-tag></a-col>
              <a-col :span="14">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6" class="oneRow">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
          <a-col style="float: left;height: 100%;" :span="8">
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(6, 9)" :key="index">
              <a-col :span="4"><a-tag>{{ index+7 }}</a-tag></a-col>
              <a-col :span="14">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6" class="oneRow">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
        </a-row>
        <drawer-view title="异常检测结果统计">
          <template slot="click">
            <div class="showAllResult">查看全部结果</div>
          </template>
          <template slot="drawerView">
            <get-check-result-drawer></get-check-result-drawer>
          </template>
        </drawer-view>
      </a-col>
    </a-row>
    <a-card style="width: 100%;float: left;margin-top: 10px">
      <div style="font-weight: bold;font-size: 18px;margin-top: -12px;margin-bottom: 10px">异常检测规则列表</div>
      <a-table
        rowKey="check_item"
        :columns="columns"
        :data-source="ruleList"
        :pagination="pagination"
        @change="handleTableChange"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="1">
        <span slot="index" slot-scope="text, record, index">
          {{ index + firstIndex }}
        </span>
        <span slot="action" slot-scope="rule">
          <a-popconfirm
            title="确认要删除这条异常检测记录?"
            ok-text="确认"
            cancel-text="取消"
            @confirm="deleteRule(rule)"
          ><a href="#">删除</a></a-popconfirm>
        </span>
        <div slot="expandedRowRender" slot-scope="result" style="width: 100%;margin: 1px;padding-left: 50px;">
          <check-result-expanded :dataSource="result.data_list"></check-result-expanded>
        </div>
      </a-table>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import DrawerView from '@/views/utils/DrawerView'
import GetCheckResultDrawer from '@/views/diagnosis/components/GetCheckResultDrawer'
import AddAbnormalCheckRuleDrawer from '@/views/diagnosis/components/AddAbnormalCheckRuleDrawer'
import CheckResultExpanded from '@/views/diagnosis/components/CheckResultExpanded'
import { getRule, getResultCountTopTen, getRuleCount, deleteRule } from '@/api/check'

export default {
  name: 'RuleManagement',
  components: {
    MyPageHeaderWrapper,
    DrawerView,
    AddAbnormalCheckRuleDrawer,
    GetCheckResultDrawer,
    CheckResultExpanded
  },
  mounted: function () {
    this.getRuleCount()
    this.getResultCountTopTen()
    this.getRuleList()
  },
  computed: {
    firstIndex () {
      return (this.pagination.current - 1) * this.pagination.pageSize + 1
    }
  },
  data () {
    return {
      ruleCount: 0,
      filters: null,
      sorter: null,
      tableIsLoading: false,
      columns,
      resultCountList: [],
      ruleList: [],
      pagination: { current: 1, pageSize: 5, showSizeChanger: true, showQuickJumper: true }
    }
  },
  methods: {
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
    handleTableChange (pagination) {
      this.pagination = pagination // 存储翻页状态
      this.getRuleList() // 出发排序、筛选、分页时，重新请求
    },
    getRuleList () {
      this.ruleList = []
      var that = this
      getRule({ perPage: this.pagination.pageSize, page: this.pagination.current }).then(function (data) {
        that.ruleList = data.check_items
        that.pagination = { ...that.pagination }
        that.pagination.total = data.total_count
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      })
    },
    deleteRule (rule) {
      var that = this
      deleteRule([rule.check_item]).then(function () {
        that.getRuleList()
        that.$message.success('记录删除成功')
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
    scopedSlots: { customRender: 'index' }
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
    dataIndex: 'description',
    key: 'description',
    title: '检测结果描述'
  },
  {
    title: '操作',
    scopedSlots: { customRender: 'action' }
  }
]

</script>

<style lang="less" scoped>
.topBox{display:inline-block;width: 100%}
.topItem{height:170px;float: left;}
.topItem:nth-child(1){min-width: 170px;background: #fff;}
.topItem:nth-child(2){min-width: 670px;}
.showAllResult{width: 35px;height:100%;float: right;background:#1890ee;border: 1px solid #fff;color: #fff;padding: 21px 5px;text-align: center;cursor: pointer}
.showAllResult:hover{background: #0075d0;}
.oneRow{
  text-overflow: -o-ellipsis-lastline;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 1;
  line-clamp: 1;
  -webkit-box-orient: vertical;
}

.content{position: absolute;width: 100%;height: 60px;top: 50%;margin-top: -30px;padding-left: 5px}
.newRule{width: calc(100% - 2px);height: 100%;background:#1890ee;text-align: center;cursor: pointer}
.newRule:hover{background: #0075d0;}
.myRow{height: calc(25% - 5px);width: 100%;margin-bottom:5px}
.myRow>.ant-col:nth-child(1){position: relative;height: 100%}
.myRow>.ant-col:nth-child(1) .ant-tag{border-radius: 50%;padding: 0 1px 0 0;width: 24px;height: 24px;line-height: 22px;text-align: center;position: absolute;top: 50%;left: 50%;margin-top: -12px;margin-left: -12px}
.myRow>.ant-col:nth-child(2){line-height: 1.2em!important;}
.myRow>.ant-col:nth-child(3){line-height: 30px}
</style>
