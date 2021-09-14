
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
              <div style="color: #333;font-size: 32px;line-height: 1em">
                <a-spin v-if="countIsLoading" />
                <span v-else>{{ ruleCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,') }}</span>
              </div>
            </div>
          </div>
        </div>
        <div style="width: 100%;height: 34px;line-height: 32px;color: #fff;padding:0 2px">
          <drawer-view title="新建异常检测规则">
            <template slot="click">
              <div class="myBtn" style="float: left">
                <a-icon type="file-add" style="margin-right: 5px"/>新建规则
              </div>
            </template>
            <template slot="drawerView">
              <add-abnormal-check-rule-drawer :addSuccess="handleAddRuleSuccess"></add-abnormal-check-rule-drawer>
            </template>
          </drawer-view>
          <router-link :to="{ path: '/diagnosis/abnormal-check/rule-management' }" target="_blank">
            <div class="myBtn" style="float: right;color: #fff;margin-right: 1px">
              <a-icon type="file-add" style="margin-right: 5px;"/>管理规则
            </div>
          </router-link>
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
      <div style="font-weight: bold;font-size: 18px;margin-top: -12px;margin-bottom: 10px">异常检测记录</div>
      <a-row class="filters-row" type="flex" :gutter="10">
        <a-col >
          <a-range-picker
            :show-time="{ format: 'HH:mm:ss' }"
            format="YYYY-MM-DD HH:mm:ss"
            :placeholder="['开始时间', '结束时间']"
            @change="handleTimeSelect"
            @ok="handleTimeSelect"
            style="width: 380px"
          />
        </a-col>
        <a-col>
          <a-button @click="filterByTime">按时间筛选</a-button>
        </a-col>
      </a-row>
      <a-table
        :columns="columns"
        :data-source="resultList"
        :pagination="pagination"
        @change="handleTableChange"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="3">
        <span slot="index" slot-scope="text, record, index">
          {{ index + firstIndex }}
        </span>
        <span slot="action" slot-scope="result">
          <span>查看报告</span>
          <a-divider type="vertical" />
          <a-popconfirm
            title="确认要删除这条异常检测记录?"
            ok-text="确认"
            cancel-text="取消"
            :disabled="true"
            @confirm="deleteResult(result)"
          ><span href="#">删除</span></a-popconfirm>
          <a-divider type="vertical" />
          <a-icon type="down" style="color: #999"/>
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
import { getRuleAll, getRuleCount, getResultCountTopTen, getResult } from '@/api/check'
import { hostList } from '@/api/assest'
import { dateFormat } from '@/views/utils/Utils'
import CheckResultExpanded from '@/views/diagnosis/components/CheckResultExpanded'

const defaultPagination = { current: 1, pageSize: 10, showSizeChanger: true, showQuickJumper: true }

  export default {
    name: 'AbnormalCheck',
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
      this.getResultList({})
      // 获取筛选数据列表
      this.getFilterListData()
    },
    computed: {
      columns () {
        let { filters } = this
        filters = filters || {}
        return [
          {
            title: '序号',
            dataIndex: 'index',
            key: 'index',
            align: 'center',
            width: 70,
            scopedSlots: { customRender: 'index' }
          },
          {
            dataIndex: 'hostName',
            key: 'hostName',
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
            key: 'ip',
            title: 'IP地址'
          },
          {
            dataIndex: 'check_item',
            key: 'check_item',
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
          },
          {
            title: '操作',
            key: 'action',
            scopedSlots: { customRender: 'action' }
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
        tableIsLoading: false,
        resultCountList: [],
        resultList: [],
        pagination: defaultPagination,
        filters: null,
        sorter: null,
        ruleAllList: [],
        hostAllList: []
      }
    },
    methods: {
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
        var that = this
        getResultCountTopTen().then(function (data) {
          that.resultCountList = data.results
        }).catch(function (err) {
          that.$message.error(err.response.data.msg)
        })
      },
      paginationChange (page, pageSize) {
        // this.getResultList({})
      },
      handleTableChange (pagination, filters, sorter) {
        if (this.paginationChange.current === pagination.current) {
          this.pagination = defaultPagination // 筛选是重置pagination
        } else {
          this.pagination = pagination // 存储翻页状态
        }
        this.filters = filters
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
      deleteResult (result) {
        this.$message.success('记录删除成功')
      },
      handleAddRuleSuccess () {
        this.getRuleCount()
      },
      getUnixTime (dateStr) {
        const newStr = dateStr.replace(/-/g, '/')
        const date = new Date(newStr)
        return date.getTime() / 1000
      }
    }
  }

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
.myBtn{width: calc(50% - 2px);height: 100%;background:#1890ee;text-align: center;cursor: pointer}
.myBtn:hover{background: #0075d0;}
.myRow{height: calc(25% - 5px);width: 100%;margin-bottom:5px}
.myRow>.ant-col:nth-child(1){position: relative;height: 100%}
.myRow>.ant-col:nth-child(1) .ant-tag{border-radius: 50%;padding: 0 1px 0 0;width: 24px;height: 24px;line-height: 22px;text-align: center;position: absolute;top: 50%;left: 50%;margin-top: -12px;margin-left: -12px}
.myRow>.ant-col:nth-child(2){line-height: 1.2em!important;}
.myRow>.ant-col:nth-child(3){line-height: 30px}

.filters-row {
  margin: 10px 0;
  /deep/ .ant-calendar-range-picker-input {
    width: 160px;
  }
}
</style>
