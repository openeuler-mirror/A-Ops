<template>
  <div id="alertInfoDrawer" style="width: 100%;overflow: auto;">
    <p>共获取到 {{ alertInfoResult.length }} 条告警信息</p>
    <a-table
      :rowKey="(record,index) => index"
      :columns="columns"
      :data-source="alertInfoResult"
      :loading="isLoading"
      :pagination="pagination"
      @change="handleTableChange"
    />
  </div>
</template>

<script>
import { getAlertInfoResult } from '@/api/check'

const defaultPagination = {
  current: 1,
  pageSize: 10,
  total: 0,
  showSizeChanger: true,
  showQuickJumper: true,
  size: 'small',
  pageSizeOptions: ['10', '15', '20']
}
export default {
  name: 'CountAlertInfoDrawer',
  data() {
    return {
      isLoading: false,
      alertInfoResult: [],
      pagination: defaultPagination
    }
  },
  computed: {
    columns() {
      return [
        {
          title: '序号',
          align: 'center',
          customRender: (text, record, index) => index + 1
        },
        {
          title: '主机组',
          align: 'center',
          dataIndex: 'domain'
        },
        {
          title: '告警数',
          align: 'center',
          dataIndex: 'count',
          customRender: (text, record, index) => {
            if (index < 5) {
              return <span class="result-count high-light">{text}</span>
            } else {
              return <span class="result-count">{text}</span>
            }
          }
        }
      ]
    }
  },
  mounted() {
    this.getAlertInfoResult()
  },
  methods: {
    getAlertInfoResult({page, pageSize, direction} = {}) {
      const that = this
      const pagination = this.pagination
      this.isLoading = true
      getAlertInfoResult({
        page: pagination.current,
        per_page: pagination.pageSize,
        direction: direction
      }).then(res => {
        that.alertInfoResult = res.results
        that.pagination.total = res.total_count
      }).catch(err => {
        that.$message.error(err.error_msg)
      }).finally(() => {
        that.isLoading = false
      })
    },
    handleTableChange (pagination, filters, sorter) {
      this.pagination = pagination
      this.getAlertInfoResult()
    }
  }
}
</script>

<style lang="less" scoped>
#alertInfoDrawer {
  p {
    color: #000;
  }
  /deep/ .ant-table-thead > tr > th {
    padding:12px 10px;
    font-weight: 500;
    color: #000;
    border-bottom: 0px;
  }
  /deep/ .ant-table-tbody > tr > td {
    padding:10px 10px;
  }
  .result-count {
    &.high-light {
      color: #f84b4b;
      font-weight: 500;
    }
  }
}
</style>
