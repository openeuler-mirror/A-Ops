
<template>
  <my-page-header-wrapper>
    <a-row :gutter="24">
      <a-col :xs="24" :xl="7">
        <a-card :bordered="false" class="aops-theme check-rule-card">
          <a-row class="flex-no-wrap" type="flex" :gutter="16">
            <a-col>
              <div class="theme-img-box">
                <img class="theme-img" src="~@/assets/dash-fault.png"/>
              </div>
            </a-col>
            <a-col>
              <p class="theme-title">异常检测规则数量</p>
              <p class="theme-number">
                <a-spin v-if="countIsLoading" />
                <span v-else>{{ ruleCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,') }}</span>
              </p>
            </a-col>
          </a-row>
          <a-row class="flex-no-wrap theme-button-box" type="flex" justify="space-between">
            <a-col span="12">
              <drawer-view title="新建异常检测规则">
                <template slot="click">
                  <div class="theme-button make-space">新建规则</div>
                </template>
                <template slot="drawerView">
                  <add-abnormal-check-rule-drawer :addSuccess="handleAddRuleSuccess"></add-abnormal-check-rule-drawer>
                </template>
              </drawer-view>
            </a-col>
            <a-col span="12">
              <router-link :to="{ path: '/diagnosis/abnormal-check/rule-management' }">
                <div class="theme-button theme-button-right">管理规则</div>
              </router-link>
            </a-col>
          </a-row>
        </a-card>
      </a-col>
      <a-col :xs="24" :xl="17">
        <a-card :bordered="false" class="aops-theme check-result-card">
          <h3>异常检测结果统计</h3>
          <div>
            <a-row type="flex" :gutter="12">
              <a-table
                class="check-result-table"
                row-key="hostName"
                :columns="columnsReulst"
                :data-source="resultCountList.slice(0, 5)"
                :bordered="false"
                :pagination="false"
                :loading="countTopLoading"
              />
            </a-row>
          </div>
          <drawer-view title="异常检测结果统计">
            <template slot="click">
              <p class="showAllResult">查看全部结果 ></p>
            </template>
            <template slot="drawerView">
              <get-check-result-drawer></get-check-result-drawer>
            </template>
          </drawer-view>
        </a-card>
      </a-col>
    </a-row>
    <a-card class="aops-theme">
      <h3>异常检测记录</h3>
      <a-row class="filters-row aops-app-table-control-row" type="flex" justify="space-between">
        <a-col>
          <a-row type="flex" :gutter="10">
            <a-col >
              <aops-range-picker
                :show-time="{ format: 'HH:mm:ss' }"
                format="YYYY-MM-DD HH:mm:ss"
                :placeholder="['开始时间', '结束时间']"
                @ok="timeRangeOk"
                @clear="timeRangeClear"
                style="width: 380px"
              />
            </a-col>
          </a-row>
        </a-col>
        <a-col>
          <drawer-view title="新建故障诊断" :bodyStyle="{ paddingBottom: '80px' }">
            <template slot="click">
              <a-button type="primary" @click="setDiagnosisParams">
                故障诊断<a-icon type="plus"/>
              </a-button>
            </template>
            <template slot="drawerView">
              <add-fault-diagnosis
                :saveSuccess="addFaultDiagnosisSuccess"
                :faultTreeList="treeDataAll"
                :diagnosisParams="diagnosisParams"
              ></add-fault-diagnosis>
            </template>
          </drawer-view>
        </a-col>
      </a-row>
      <a-table
        :columns="columns"
        :data-source="resultList"
        :pagination="pagination"
        @change="handleTableChange"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="4"
      >
        <span slot="index" slot-scope="text, record, index">
          {{ index + firstIndex }}
        </span>
        <div slot="expandedRowRender" slot-scope="result" style="width: 100%;margin: 1px;padding-left: 50px;">
          <check-result-expanded :dataSource="result.data_list"></check-result-expanded>
        </div>
        <span slot="desc" slot-scope="text">
          <cut-text :text="text" :length="10"/>
        </span>
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
import AddFaultDiagnosis from '@/views/diagnosis/components/AddFaultDiagnosis'
import CheckResultExpanded from '@/views/diagnosis/components/CheckResultExpanded'
import CutText from '@/components/CutText'
import AopsRangePicker from './components/AopsRangePicker.vue'

import { getSelectedRow } from '@/views/utils/getSelectedRow'
import { getRuleAll, getRuleCount, getResultCountTopTen, getResult } from '@/api/check'
import { getDiagTree } from '@/api/diagnosis'
import { hostList } from '@/api/assest'
import { dateFormat } from '@/views/utils/Utils'

const defaultPagination = { current: 1, pageSize: 10, showSizeChanger: true, showQuickJumper: true }

  export default {
    name: 'AbnormalCheck',
    components: {
      MyPageHeaderWrapper,
      DrawerView,
      AddAbnormalCheckRuleDrawer,
      GetCheckResultDrawer,
      CheckResultExpanded,
      AddFaultDiagnosis,
      CutText,
      AopsRangePicker
    },
    mounted: function () {
      this.getRuleCount()
      this.getResultCountTopTen()
      this.getResultList({})
      // 获取筛选数据列表
      this.getFilterListData()
      // 获取故障树列表
      this.getDiagTreeList()
    },
    computed: {
      columns () {
        let { filters } = this
        filters = filters || {}
        return [
          {
            title: '序号',
            dataIndex: 'index',
            align: 'center',
            width: 70,
            scopedSlots: { customRender: 'index' }
          },
          {
            dataIndex: 'hostName',
            title: '主机名称',
            filteredValue: filters.hostName || null,
            filters: this.hostAllList.map(host => {
                return {
                    text: host.host_name,
                    value: host.host_id
                }
            })
          },
          {
            dataIndex: 'ip',
            title: 'IP地址'
          },
          {
            dataIndex: 'check_item',
            title: '检测项',
            filteredValue: filters.check_item || null,
            filters: this.ruleAllList.map(rule => {
                return {
                    text: rule.check_item,
                    value: rule.check_item
                }
            })
          },
          {
            dataIndex: 'condition',
            title: '检测条件'
          },
          {
            dataIndex: 'description',
            title: '描述',
            width: 120,
            scopedSlots: { customRender: 'desc' }
          },
          {
            dataIndex: 'count',
            title: '异常时间段',
            customRender: (text, record, index) => dateFormat('YYYY-mm-dd HH:MM:SS', record.start * 1000) + ' 至 ' + dateFormat('YYYY-mm-dd HH:MM:SS', record.end * 1000)
          }
        ]
      },
      columnsReulst () {
        return [
          {
            title: '序号',
            dataIndex: 'index',
            key: 'index',
            align: 'center',
            customRender: (text, record, index) => {
              if (index < 3) {
                return <a-tag class="result-tag hight-light">{ index + 1 }</a-tag>
              } else {
                return <a-tag class="result-tag">{ index + 1 }</a-tag>
              }
            }
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
            dataIndex: 'count',
            title: '异常数',
            customRender: count => (<span class="result-count">{count}</span>)
          }
        ]
      },
      firstIndex () {
        return (this.pagination.current - 1) * this.pagination.pageSize + 1
      }
    },
    data () {
      return {
        ruleCount: 0,
        countIsLoading: false,
        countTopLoading: false,
        tableIsLoading: false,
        resultCountList: [],
        resultList: [],
        resultListShort: [],
        pagination: defaultPagination,
        filters: null,
        sorter: null,
        selectedRowKeys: [],
        selectedRowsAll: [],
        ruleAllList: [],
        hostAllList: [],
        treeDataAll: [],
        diagnosisParams: {}
      }
    },
    methods: {
      onSelectChange (selectedRowKeys) {
        this.selectedRowKeys = selectedRowKeys
        this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, this.resultList, 'key')
      },
      getDiagTreeList () {
        const _this = this
        getDiagTree({
          treeList: []
        }).then(function (res) {
          _this.treeDataAll = [{}].concat(res.trees)
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
      },
      filterByTime () {
        this.pagination = defaultPagination
        this.getResultList()
      },
      handleTimeSelect (value) {
        if (!this.filters) {
          this.filters = {
            timeRange: value
          }
        } else {
          this.filters.timeRange = value
        }
        this.filterByTime()
      },
      timeRangeOk (val) {
        this.handleTimeSelect(val)
      },
      timeRangeClear (val) {
        this.handleTimeSelect(val)
      },
      getFilterListData () {
        const _this = this
        getRuleAll().then(function (res) {
          _this.ruleAllList = res.check_items.map(function (item) {
            return {
              check_item: item.check_item
            }
          })
        })
        hostList({
          tableInfo: {
            pagination: {},
            filters: {},
            sorter: {}
          }
        }).then(function (res) {
          _this.hostAllList = res.host_infos.map(function (host) {
            return {
              host_name: host.host_name,
              host_id: host.host_id
            }
          })
        })
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
        const that = this
        this.countTopLoading = true
        getResultCountTopTen().then(function (data) {
          that.resultCountList = data.results
        }).catch(function (err) {
          that.$message.error(err.response.data.msg)
        }).finally(() => {
          that.countTopLoading = false
        })
      },
      paginationChange (page, pageSize) {
        // this.getResultList({})
      },
      handleTableChange (pagination, filters, sorter) {
        const timeFilter = this.filters && this.filters.timeRange
        if (this.paginationChange.current === pagination.current) {
          this.pagination = defaultPagination // 筛选是重置pagination
        } else {
          this.pagination = pagination // 存储翻页状态
        }
        this.filters = {
          ...filters,
          timeRange: timeFilter
        }
        this.sorter = sorter
        this.getResultList() // 出发排序、筛选、分页时，重新请求
      },
      getResultList () {
        var that = this
        const pagination = this.pagination || {}
        const filters = this.filters || {}
        this.tableIsLoading = true
        getResult({
          perPage: pagination.pageSize,
          page: pagination.current,
          hostList: filters.hostName || [],
          checkItems: filters.check_item || [],
          timeRange: filters.timeRange && filters.timeRange.map(momentTime => momentTime ? that.getUnixTime(momentTime.format('YYYY-MM-DD HH:mm:ss')) : undefined)
        }).then(function (data) {
          that.resultList = data.check_result ? data.check_result.map(result => {
            return {
              ...result,
              key: `${result.host_id}+${result.check_item}+${result.start}+${result.end}`
            }
          }) : []
          that.pagination = { ...that.pagination }
          that.pagination.total = data.total_count
        }).catch(function (err) {
          that.$message.error(err.response.data.msg)
        }).finally(() => {
          this.tableIsLoading = false
        })
      },
      handleAddRuleSuccess () {
        this.getRuleCount()
      },
      getUnixTime (dateStr) {
        const newStr = dateStr.replace(/-/g, '/')
        const date = new Date(newStr)
        return date.getTime() / 1000
      },
      addFaultDiagnosisSuccess () {
        this.$router.push('/diagnosis/fault-diagnosis')
      },
      setDiagnosisParams () {
        if (this.selectedRowsAll.length <= 0) {
          this.diagnosisParams = {}
          return
        }
        let startTime = this.selectedRowsAll[0].start
        let endTime = this.selectedRowsAll[0].end
        const hostList = [this.selectedRowsAll[0].host_id]
        this.selectedRowsAll.forEach(rows => {
          if (rows.start < startTime) {
            startTime = rows.start
          }
          if (rows.end > endTime) {
            endTime = rows.end
          }
          if (hostList.indexOf(rows.host_id) < 0) {
            hostList.push(rows.host_id)
          }
        })
        startTime -= 60
        endTime += 60
        this.diagnosisParams = Object.assign({}, {
          startTime,
          endTime,
          hostList
        })
      }
    }
  }

</script>

<style lang="less" scoped>
.filters-row {
  margin: 10px 0;
  /deep/ .ant-calendar-range-picker-input {
    width: 160px;
  }
}

/deep/ td:nth-child(5) {
  white-space: nowrap;
}

.check-rule-card {
  margin-bottom: 20px;
  height:220px;
  /deep/ .ant-card-body {
    padding: 24px 12px;
  }
  .theme-img-box {
    width: 136px;
    margin-top: 22px;
  }
  .theme-img {
    display: block;
    width: 74px;
    height: 74px;
    margin:0 auto 26px;
  }
  .theme-title {
    margin-top: 22px;
    font-size: 14px;
    font-weight: 400;
    line-height: 20px;
    text-align: center;
  }
  .theme-number {
    font-size: 36px;
    font-weight: bold;
    line-height: 20px;
    margin-bottom: 8px;
    text-align: center;
  }
  .theme-button-box {
    position: absolute;
    bottom: 0;
    left: 0;
    width: 100%;
    height: 50px;
  }
  .theme-button {
    width: 100%;
    height: 100%;
    line-height: 50px;
    background: #537de7;
    border-radius: 0 0 0 8px;
    &-right {
      border-radius: 0 0 8px 0;
      border-left: 1px solid #fff;
    }
    text-align: center;
    color: #fff;
    cursor: pointer;
    font-weight: 600;
    font-size: 16px;
    &:hover {
      background: #7997e4;
    }
  }
}
.check-result-card {
  min-height:220px;
  margin-bottom: 20px;
  h3 {
    margin-top: -12px;
    margin-bottom: 4px;
  }
  .result-item {
    margin-bottom:10px;
    &:last-child {
      margin-bottom: 0;
    }
  }
  .result-tag {
    color: #002FA7;
    font-weight: 900;
    background: none;
    border: 0;
    &.hight-light {
      background: #dde6fa;
      border-radius: 50%;
      border: 0;
    }
  }
  /deep/ .check-result-table {
    .ant-table-thead > tr > th {
      padding:2px 16px;
      border-bottom: 0;
      background: #fff;
    }
    .ant-table-tbody > tr > td {
      padding:2px 16px;
      border-bottom: 0;
    }
    .ant-empty-normal {
      margin-top: 16px;
      margin-bottom: 0;
    }
    .ant-table-placeholder {
      border: 0;
    }
  }
  .result-count {
    color: #F95858;
  }
  .showAllResult{
    position: absolute;
    top: 12px;
    right: 24px;
    font-weight: 600;
    color: #002FA7;
    cursor:pointer;
    &:hover {
      color: #3455a7;
    }
  }
}
</style>
