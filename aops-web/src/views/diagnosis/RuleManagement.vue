
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <h3>
        异常检测规则列表
        <a-spin v-if="countIsLoading" size="small" />
        <span v-else style="font-size: 14px">
          {{ `共${ruleCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')}项` }}
        </span>
      </h3>
      <a-row class="aops-app-table-control-row" type="flex" :gutter="6" justify="space-between">
        <a-col>
          <a-alert type="info" show-icon>
            <div slot="message">
              <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
              <a v-if="selectedRowKeys.length > 0" @click="handleDeleteBash()">批量删除</a>
            </div>
          </a-alert>
        </a-col>
        <a-col>
          <drawer-view title="新建异常检测规则">
            <template slot="click">
              <a-button type="primary">
                新建规则
              </a-button>
            </template>
            <template slot="drawerView">
              <add-abnormal-check-rule-drawer :addSuccess="handleAddSuccess"></add-abnormal-check-rule-drawer>
            </template>
          </drawer-view>
        </a-col>
      </a-row>
      <a-table
        rowKey="check_item"
        :columns="columns"
        :data-source="ruleList"
        :pagination="pagination"
        :row-selection="rowSelection"
        @change="handleTableChange"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="2">
        <span slot="index" slot-scope="text, record, index">
          {{ index + firstIndex }}
        </span>
        <span slot="desc" slot-scope="text">
          <cut-text :text="text" :length="8"/>
        </span>
        <span slot="action" slot-scope="rule">
          <a href="#" @click="handleDelete([rule.check_item])">删除</a>
        </span>
        <div slot="expandedRowRender" slot-scope="result" style="width: 100%;margin: 1px;padding-left: 50px;">
          <check-result-expanded :dataSource="result.data_list"></check-result-expanded>
        </div>
      </a-table>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
// this component is abandoned
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import DrawerView from '@/views/utils/DrawerView'
import GetCheckResultDrawer from '@/views/diagnosis/components/GetCheckResultDrawer'
import AddAbnormalCheckRuleDrawer from '@/views/diagnosis/components/AddAbnormalCheckRuleDrawer'
import CheckResultExpanded from '@/views/diagnosis/components/CheckResultExpanded'
import CutText from '@/components/CutText'

import { getRule, getResultCountTopTen, getRuleCount, deleteRule } from '@/api/check'

export default {
  name: 'RuleManagement',
  components: {
    MyPageHeaderWrapper,
    DrawerView,
    AddAbnormalCheckRuleDrawer,
    GetCheckResultDrawer,
    CheckResultExpanded,
    CutText
  },
  mounted: function () {
    this.getRuleCount()
    this.getResultCountTopTen()
    this.getRuleList()
  },
  computed: {
    firstIndex () {
      return (this.pagination.current - 1) * this.pagination.pageSize + 1
    },
    rowSelection () {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: this.onSelectChange
      }
    }
  },
  data () {
    return {
      ruleCount: 0,
      countIsLoading: false,
      filters: null,
      sorter: null,
      tableIsLoading: false,
      columns,
      resultCountList: [],
      ruleList: [],
      pagination: { current: 1, pageSize: 10, showSizeChanger: true, showQuickJumper: true },
      selectedRowKeys: [],
      selectedRows: []
    }
  },
  methods: {
    onSelectChange (selectedRowKeys, selectedRows) {
      this.selectedRowKeys = selectedRowKeys
      this.selectedRows = selectedRows
    },
    getRuleCount () {
      var that = this
      this.countIsLoading = true
      getRuleCount().then(function (data) {
        that.ruleCount = data.rule_count
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      }).finally(() => {
        that.countIsLoading = false
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
      this.tableIsLoading = true
      getRule({ perPage: this.pagination.pageSize, page: this.pagination.current }).then(function (data) {
        that.ruleList = data.check_items
        that.pagination = { ...that.pagination }
        that.pagination.total = data.total_count
      }).catch(function (err) {
        that.$message.error(err.response.data.msg)
      }).finally(() => {
        that.tableIsLoading = false
      })
    },
    deleteRule (chekcItemList) {
      var that = this
      const _this = this
      return new Promise((resolve, reject) => {
        deleteRule(chekcItemList)
        .then((res) => {
          that.selectedRowKeys = []
          that.refresh()
          that.$message.success(res.msg)
          resolve()
        }).catch((err) => {
          _this.$message.error(err.response.data.msg)
          reject(err)
        })
      })
    },
    handleDelete (checkItemList) {
      const _this = this
      this.$confirm({
        title: (<div><p>删除后无法恢复</p></div>),
        content: () => `确定要删除这条异常检测规则么？`,
        icon: () => <a-icon type="exclamation-circle" />,
        okType: 'danger',
        okText: '删除',
        onOk: function () { return _this.deleteRule(checkItemList) },
        onCancel () {}
      })
    },
    handleDeleteBash () {
      const _this = this
      this.$confirm({
        title: (<div><p>删除后无法恢复</p></div>),
        content: () => `确定要删除选中的${_this.selectedRowKeys.length}项规则么？`,
        icon: () => <a-icon type="exclamation-circle" />,
        okType: 'danger',
        okText: '删除',
        onOk: function () { return _this.deleteRule(_this.selectedRowKeys) },
        onCancel () {}
      })
    },
    handleAddSuccess () {
      this.refresh()
    },
    refresh () {
      const _this = this
      this.tableIsLoading = true
      this.countIsLoading = true
      setTimeout(function () {
        _this.getRuleCount()
        _this.getRuleList()
      }, 1500)
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
    title: '检测结果描述',
    scopedSlots: { customRender: 'desc' }
  },
  {
    title: '操作',
    width: 70,
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

/deep/ td:nth-child(3) {
  white-space: nowrap;
}
/deep/ td:nth-child(5) {
  white-space: nowrap;
}
</style>
