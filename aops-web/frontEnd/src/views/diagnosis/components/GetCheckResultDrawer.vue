<template>
  <a-table :columns="columns" :data-source="tableData" bordered>
  </a-table>
</template>

<script>
  import { getcheckresult } from '@/api/diagnosis'
  const defaultPagination = {
    current: 1,
    pageSize: 2,
    showSizeChanger: true,
    showQuickJumper: true
  }
    export default {
      name: 'GetCheckResultDrawer',
       data () {
          return {
            pagination: defaultPagination,
            filters: null,
            sorter: null,
            tableIsLoading: false,
            tableData: []
         }
        },
      computed: {
        columns () {
          return [
            {
              title: '序号',
              dataIndex: '’'
            },
            {
              title: '主机名',
              dataIndex: 'host_id'
            },
            {
              title: 'IP地址',
              dataIndex: 'ip'
            },
            {
              title: '异常数',
              dataIndex: 'check_value'
            }
          ]
        },
        rowSelection () {
          return {
            selectedRowKeys: this.selectedRowKeys,
            onChange: this.onSelectChange
          }
        }
      },
      methods: {
        handleTableChange (pagination, filters, sorter) {
          // 存储翻页状态
          this.pagination = pagination
          this.filters = filters
          this.sorter = sorter
          // 出发排序、筛选、分页时，重新请求主机列表
          this.getHostList({})
        },
        // 获取列表数据
        getHostList ({ p, f, s }) {
          const _this = this
          this.tableIsLoading = true
          const pagination = p || this.pagination
          const filters = f || this.filters
          const sorter = s || this.sorter

          getcheckresult({
            uid: '123',
            tableInfo: {
              pagination: {
                current: pagination.current,
                pageSize: pagination.pageSize
              },
              filters: filters || {},
              sorter: sorter ? {
                field: sorter.field,
                order: sorter.order
              } : {}
            }
          })
            .then(function (res) {
              console.log(res.result.checkResultData.check_result)
              _this.tableData = res.result.checkResultData.check_result
            }).catch(function (err) {
            _this.$message.error(err.response.data.message)
          }).finally(function () { _this.tableIsLoading = false })
        }
      },
      mounted: function () {
        this.getHostList({})
      }
    }
</script>
