<template>
  <a-table
    rowKey="host_id"
    :columns="columns"
    :data-source="tableData"
    :pagination="pagination"
    @change="handleTableChange"
    bordered>
        <span slot="index" slot-scope="text, record, index">
          {{ index + firstIndex }}
        </span>
  </a-table>
</template>

<script>
  import { getResultCount } from '@/api/check'

  export default {
    name: 'GetCheckResultDrawer',
    computed: {
      firstIndex () {
        return (this.pagination.current - 1) * this.pagination.pageSize + 1
      }
    },
    data () {
      return {
        columns,
        pagination: { current: 1, pageSize: 5, showSizeChanger: true, showQuickJumper: true },
        tableIsLoading: false,
        tableData: []
     }
    },
    mounted: function () {
      this.getHostList({})
    },
    methods: {
      handleTableChange (pagination) {
        this.pagination = pagination // 存储翻页状态
        this.getHostList() // 出发排序、筛选、分页时，重新请求主机列表
      },
      // 获取列表数据
      getHostList () {
        const that = this
        this.tableIsLoading = true
        getResultCount({ sort: 'count', direction: 'desc', perPage: this.pagination.pageSize, page: this.pagination.current }).then(function (data) {
          that.tableData = data.results
          that.pagination = { ...that.pagination }
          that.pagination.total = data.total_count
        }).catch(function (err) {
          that.$message.error(err.response.data.msg)
        }).finally(function () { that.tableIsLoading = false })
      }
    }
  }

  const columns = [
    {
      title: '序号',
      align: 'center',
      width: 70,
      scopedSlots: { customRender: 'index' }
    },
    {
      title: '主机名',
      dataIndex: 'hostName'
    },
    {
      title: 'IP地址',
      dataIndex: 'ip'
    },
    {
      title: '异常数',
      dataIndex: 'count'
    }
  ]
</script>
