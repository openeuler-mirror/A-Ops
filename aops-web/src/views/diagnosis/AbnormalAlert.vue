<template>
  <page-header-wrapper>
    <div class="diagnosis-abnormal-alert">
      <alert-header-board />
      <a-row>
        <a-card :bordered="false" class="aops-theme alert-record-card">
          <h2>告警记录</h2>
          <div style="display:flex;justify-content:space-between;">
            <p style="margin-bottom:10px;font-size:17px;font-weight:600;">
              共获取到 {{ alertRecordData.length }} 条记录
            </p>
            <div style="margin-bottom:10px;">
              <a-button type="primary" :loading="buttonLoading" @click="getAlertRecordResult">
                刷新<a-icon type="reload" />
              </a-button>
            </div>
          </div>
          <a-table
          rowKey="alert_id"
          :columns="alertRecordColumns"
          :data-source="alertRecordData"
          :pagination="pagination"
          :loading="alertRecordLoading"
          @change="handleTableChange"
          class="alert-record-table"
          >
            <span slot="operation" slot-scope="text,record">
              <a-popconfirm
              title="确认后,该告警将不再提示"
              ok-text="确定"
              cancel-text="取消"
              @confirm="confirmAlert(record.alert_id)"
              >
                <img slot="icon" src="~@/assets/alertConfirmIcon.png" style="width:16px;position:absolute;top:5px;"/>
                <a>确认</a>
              </a-popconfirm>
              <a-divider type="vertical" />
              <drawer-view title="异常信息" :width="800" :hasButtonOnBottom="false">
                <template slot="click">
                  <a>异常详情</a>
                </template>
                <template slot="drawerView">
                  <exception-detail-drawer :alertId="record.alert_id"/>
                </template>
              </drawer-view>
              <a-divider type="vertical" />
              <a @click="downloadReport(record.alert_id)">下载报告</a>
            </span>
          </a-table>
        </a-card>
      </a-row>
    </div>
  </page-header-wrapper>
</template>

<script>
import store from '@/store'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import AlertHeaderBoard from './components/AlertHeaderBoard'
import ExceptionDetailDrawer from '@/views/diagnosis/components/ExceptionDetailDrawer'
import DrawerView from '@/views/utils/DrawerView'
import { confirmTheAlert, downloadReport, getAlertRecordResult } from '@/api/check'
import { hostGroupList } from '@/api/assest'
import { dateFormat } from '@/views/utils/Utils'
import { downloadBlobFile } from '@/views/utils/downloadBlobFile'

const defaultPagination = {
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  pageSizeOptions: ['10', '15', '20']
};

export default {
  name: 'AbnormalAlert',
  components: {
    PageHeaderWrapper,
    AlertHeaderBoard,
    DrawerView,
    ExceptionDetailDrawer
  },
  computed: {
    alertRecordColumns() {
      const filters = this.filters || {}
      return [
        {
          title: '时间',
          dataIndex: 'time',
          align: 'center',
          sorter: true,
          customRender: (text, record, index) => dateFormat('YYYY-mm-dd HH:MM:SS', text * 1000)
        },
        {
          title: '主机组',
          dataIndex: 'domain',
          align: 'center',
          filters: this.domainFilters,
          filteredValue: filters.domain || null,
          filterMultiple: false
        },
        {
          title: '异常主机数',
          dataIndex: 'host_num',
          align: 'center'
        },
        {
          title: '告警信息',
          dataIndex: 'alert_name',
          align: 'center'
        },
        {
          title: '等级',
          dataIndex: 'level',
          align: 'center',
          customRender: (text, reccord, index) => {
            if (text === null) {
              return '暂无'
            }
          }
        },
        {
          title: '操作',
          align: 'center',
          scopedSlots: {customRender: 'operation'}
        }
      ]
    }
  },
  data () {
    return {
      alertRecordLoading: false,
      buttonLoading: false,
      alertRecordData: [],
      domainFilters: [],
      sorter: null,
      filters: null,
      pagination: defaultPagination
    }
  },
  methods: {
    getAlertRecordResult({page, pageSize, domain, direction} = {}) {
      const that = this
      this.alertRecordLoading = true
      const sorter = this.sorter || {}
      const pagination = this.pagination || {}
      const filters = this.filters || {}

      getAlertRecordResult({
        page: pagination.current,
        per_page: pagination.pageSize,
        domain: filters.domain,
        direction: sorter.order
      }).then(res => {
        that.alertRecordData = res.result
        that.pagination.total = res.total_count
      }).catch(err => {
        this.$message.error(err.error_msg)
      }).finally(() => {
        that.alertRecordLoading = false
      })
    },
    confirmAlert(e) {
      confirmTheAlert({
        alert_id: e
      }).then(res => {
        this.$message.success(res.msg)
        this.getAlertRecordResult()
        // update alert count data in AlertHeaderBoard component
        store.dispatch('updateCount')
      }).catch(err => {
        this.$message.error(err.error_msg)
      })
    },
    downloadReport(e) {
      downloadReport({
        alert_id: e
      }).then(res => {
        downloadBlobFile(res.data, res.fileName)
      }).catch(err => {
        this.$message.error(err.error_msg)
      })
    },
    handleTableChange (pagination, filters, sorter) {
      // 存储状态
      this.pagination = pagination
      this.filters = filters
      this.sorter = sorter
      this.getAlertRecordResult()
    },
    getDomainFilters() {
      const that = this
      hostGroupList({
        tableInfo: {
          pagination: {},
          filters: {},
          sorter: {}
        }
      }).then(res => {
        that.domainFilters = res.host_group_infos.map(item => {
          return {
            text: item.host_group_name,
            value: item.host_group_name
          }
        })
      }).catch(err => {
        that.$message.error(err.response.data.msg)
      })
    }
  },
  mounted() {
    this.getAlertRecordResult()
    this.getDomainFilters()
  }
}
</script>

<style lang="less" scoped>
.alert-record-card{
  margin-bottom: 20px;
  /deep/ .alert-record-table{
    .ant-table-thead > tr > th {
      padding: 16px 10px;
    }
    .ant-table-body {
      overflow: auto;
    }
    .ant-table-tbody > tr > td {
      padding:14px 10px;
    }
  }
  .ant-btn-primary {
    border: none;
    border-radius: 3px;
  }
}
</style>
