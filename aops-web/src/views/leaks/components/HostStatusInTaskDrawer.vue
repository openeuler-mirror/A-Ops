<template>
  <a-drawer
    title="CVE-主机列表"
    closable
    :visible="visible"
    width="600"
    @close="handleClose"
  >
    <a-table
      rowKey="host_id"
      :columns="columns"
      :data-source="tableData"
      :pagination="false"
      :loading="tableIsLoading"
      bordered
    >
      <div slot="status" slot-scope="status">
        <span ><a-badge :status="statusValueMap[status]" />{{ statusTextMap[status] }}</span>
      </div>
    </a-table>
  </a-drawer>
</template>

<script>
/****************
/* 展示任务中各个主机状态的抽屉组件
****************/

import { getHostOfCveInCveTask } from '@/api/leaks'

const statusTextMap = {
  'fixed': '已修复',
  'unfixed': '未修复',
  'running': '运行中',
  'on standby': '等待'
}

const statusValueMap = {
  'fixed': 'success',
  'unfixed': 'error',
  'running': 'processing',
  'on standby': 'default'
}

export default {
  name: 'HostStatusInTaskDrawer',
  props: {
    visible: {
      type: Boolean,
      default: false
    },
    taskId: {
      type: String,
      default: null
    },
    cveId: {
      type: String,
      default: null
    }
  },
  data () {
    return {
      tableData: [],
      tableIsLoading: false,

      statusTextMap,
      statusValueMap
    }
  },
  computed: {
    columns () {
      return [
        {
          dataIndex: 'index',
          title: '序号'
        },
        {
          dataIndex: 'host_name',
          title: '主机名'
        },
        {
          dataIndex: 'host_ip',
          title: 'IP地址'
        },
        {
          dataIndex: 'status',
          title: '最新状态',
          scopedSlots: { customRender: 'status' }
        }
      ]
    }
  },
  watch: {
    visible () {
      if (this.visible) {
        const _this = this
        this.tableIsLoading = true
        getHostOfCveInCveTask({
          taskId: this.taskId,
          cveList: [this.cveId]
        }).then(function (res) {
          _this.tableData = res.result && res.result[_this.cveId] || []
          _this.tableData = _this.tableData.map((row, idx) => {
            const tempObj = row
            tempObj.index = idx + 1
            return tempObj
          })
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.tableIsLoading = false
        })
      }
    }
  },
  methods: {
    handleClose () {
      this.$emit('close')
    }
  }
}
</script>
<style lang="less" scoped>
</style>
