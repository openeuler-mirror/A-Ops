<template>
  <div class="exceptionInfo" style="width: 100%;height: 100%;">
    <a-table
    :rowKey="(record,index) => index"
    :columns="columns"
    :data-source="data"
    :loading="isLoading"
    :pagination="false"
    class="outerTable"
    >
      <a-table
      :rowKey="(record,index) => index"
      slot="expandedRowRender"
      slot-scope="record"
      :columns="innerColumns"
      :data-source="record.host_check_result"
      :pagination="false"
      >
        <span slot="metric_label" slot-scope="text">
          <ExceptionDetailCutText :text="text" :length="10"/>
        </span>
      </a-table>
    </a-table>
  </div>
</template>

<script>
import { getAlertDetail } from '@/api/check'
import { dateFormat } from '@/views/utils/Utils'
import ExceptionDetailCutText from '@/views/diagnosis/components/ExceptionDetailCutText'
export default {
  name: 'ExceptionDetailDrawer',
  props: {
    alertId: {
      type: String,
      default: ''
    }
  },
  components: { ExceptionDetailCutText },
  data() {
    return {
      data: [],
      isLoading: false
    }
  },
  computed: {
    columns() {
      return [
        {
          title: '序号',
          width: 50,
          align: 'center',
          customRender: (text, record, index) => index + 1
        },
        {
          title: '主机名',
          dataIndex: 'host_name',
          align: 'center'
        },
        {
          title: 'IP',
          dataIndex: 'host_ip',
          align: 'center'
        },
        {
          title: '异常项个数',
          align: 'center',
          customRender: (text, record, index) => record.host_check_result.length
        },
        {
          title: '根因节点',
          dataIndex: 'is_root',
          align: 'center',
          customRender: (text, record, index) => {
            if (text) {
              return <a-tag color="red" style="font-weight:500;">是</a-tag>
            } else {
              return '否'
            }
          }
        }
      ]
    },
    innerColumns() {
      return [
        {
          title: '序号',
          customRender: (text, record, index) => index + 1
        },
        {
          title: '时间',
          dataIndex: 'time',
          align: 'center',
          customRender: (text, record, index) => dateFormat('YYYY-mm-dd HH:MM:SS', text * 1000)
        },
        {
          title: '数据项',
          dataIndex: 'metric_name',
          align: 'center'
        },
        {
          title: '标签',
          dataIndex: 'metric_label',
          align: 'center',
          scopedSlots: { customRender: 'metric_label' }
        },
        {
          title: '根因异常',
          dataIndex: 'is_root',
          align: 'center',
          customRender: (text, record, index) => {
            if (text) {
              return <a-tag color="red" style="font-weight:500;">是</a-tag>
            } else {
              return '否'
            }
          }
        }
      ]
    }
  },
  mounted() {
    this.getAlertDetail()
  },
  methods: {
    getAlertDetail() {
      const that = this
      this.isLoading = true
      getAlertDetail({
        alert_id: this.alertId
      }).then(res => {
        for (const key in res.result) {
          const tempObj = res.result[key]
          tempObj.key = key
          that.data.push(tempObj)
        }
      }).catch(err => {
        that.$message.error(err.error_msg)
      }).finally(() => {
        that.isLoading = false
      })
    }
  }
}
</script>

<style lang="less" scoped>
.exceptionInfo {
  /deep/ .ant-table-thead > tr > th {
    padding:12px 10px;
    font-weight: 500;
    color: #000;
    border-bottom: none;
    &:first-child {
      width: 30px;
      padding: 10px 0px;
    }
  }
  /deep/ .ant-table-tbody > tr > th {
    padding:10px 10px;
    border-bottom: none;
    &:first-child {
      width: 30px;
      padding: 10px 0px;
    }
  }
  /deep/ .ant-table-tbody > tr.ant-table-expanded-row {
    tbody {
      background: #fff;
      td {
        padding: 10px 10px;
      }
    }
  }
}
</style>
