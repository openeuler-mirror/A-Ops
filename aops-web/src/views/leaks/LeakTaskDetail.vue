<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <div class="detail-info-content">
        <a-spin :spinning="infoLoading">
          <h1>{{ detail.task_name }}</h1>
          <a-row type="flex">
            <a-col :span="8"><p>任务类型：{{ taskTypeMap[taskType] }}</p></a-col>
          </a-row>
          <a-row type="flex">
            <a-col :span="8"><p>主机个数：{{ detail.host_num }}</p></a-col>
            <a-col :span="8"><p>{{ detail.need_reboot }}台主机需要重启</p></a-col>
          </a-row>
          <a-row type="flex">
            <a-col :span="8"><p>自动重启：{{ detail.auto_reboot ? '是' : '否' }}</p></a-col>
          </a-row>
          <a-row v-if="detail.latest_execute_time">
            <a-col :span="8">
              <p>
                最新状态
                <span><a-icon type="check-circle" class="color-check-circle" />{{ detail.statuses && detail.statuses['succeed'] }}</span>
                <span><a-icon type="close-circle" class="color-close-circle" />{{ detail.statuses && detail.statuses['fail'] }}</span>
                <span>
                  <a-icon v-if="detail.statuses && detail.statuses['running']" type="loading" class="color-running-circle" />
                  <a-icon v-else type="loading-3-quarters" />
                  {{ detail.statuses && detail.statuses['running'] }}
                </span>
                <span><a-icon type="question-circle" class="color-standby-circle" />{{ detail.statuses && detail.statuses['unknown'] }}</span>
              </p>
            </a-col>
            <a-col :span="16">
              <p>
                上次执行时间：{{ detail.latest_execute_time && dateFormat('YYYY-mm-dd HH:MM:SS', detail.latest_execute_time * 1000) }}
                <router-link :to="`/leaks/task-report/${taskType}/${taskId}`" target="blank">查看报告</router-link>
              </p>
            </a-col>
          </a-row>
          <div>
            <h3>任务描述：</h3>
            <p class="detail-description">{{ detail.description }}</p>
          </div>
          <a-row type="flex" :gutter="8" justify="end">
            <a-col>
              <a-button type="primary" @click="executeTask">执行</a-button>
            </a-col>
            <a-col>
              <a-button @click="handleGetPlaybook">下载playbook</a-button>
            </a-col>
          </a-row>
        </a-spin>
      </div>
    </a-card>
    <a-card :bordered="false" class="aops-theme">
      <a-row type="flex" class="aops-app-table-control-row" :gutter="6" justify="space-between">
        <a-col>
          <a-alert type="info" show-icon class="selection-alert" v-if="selectedRowKeys.length > 0" >
            <div slot="message">
              <span>{{ `已选择`+ selectedRowKeys.length +`项用于回滚` }}</span>
              <a @click="resetSelection"> 清除选择</a>
            </div>
          </a-alert>
        </a-col>
        <a-col>
          <a-row type="flex" :gutter="6">
            <a-col>
              <a-input-search :placeholder="taskType === 'cve' ? `按CVE ID搜索` : `按主机名搜索`" style="width: 200px" @search="onSearch" />
            </a-col>
            <a-col>
              <a-button
                v-if="taskType === 'cve'"
                type="danger"
                @click="handleRollback"
                :loading="detail.statuses['running'] > 0"
                :disabled="selectedRowKeys.length <= 0 || detail.statuses['running'] > 0"
              >回滚</a-button>
            </a-col>
          </a-row>
        </a-col>
      </a-row>
      <a-table
        :rowKey="rowKeyMap[taskType]"
        :columns="taskType === 'cve' ? cveColumns: repoColumns"
        :data-source="tableData"
        :pagination="pagination"
        :row-selection="taskType === 'cve' ? rowSelection : undefined"
        @change="handleTableChange"
        :loading="tableIsLoading"
      >
        <a slot="hosts" slot-scope="hosts, record" @click="showHostListUnderCve(record.cve_id)">{{ hosts }}</a>
        <div slot="progress" slot-scope="progress, record">
          <a-progress :percent="Math.ceil(((progress || 0) / record.host_num) * 100)" />
        </div>
        <div slot="status" slot-scope="status, record">
          <span class="task-status" @click="handleCheckResult(taskType === 'cve' ? record.cve_id : record.host_id)">
            <a-badge :status="statusValueMap[status]" />
            {{ status ? statusTextMap[status] : '未知' }}
            <a-icon v-if="statusValueMap[status]==='processing'" type="loading" class="color-running-circle" />
          </span>
        </div>
      </a-table>
    </a-card>
    <host-status-in-task-drawer
      :visible="hostListUnderCveVisible"
      @close="closeHostListUnderCve"
      :taskId="taskId"
      :cveId="hostListOfCveId"
    />
  </page-header-wrapper>
</template>

<script>
/****************
/* 任务详情页面
****************/

import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import HostStatusInTaskDrawer from './components/HostStatusInTaskDrawer'
import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { dateFormat } from '@/views/utils/Utils'
import { downloadBlobFile } from '@/views/utils/downloadBlobFile'
import { getSelectedRow } from '../utils/getSelectedRow'
import {
  getTaskInfo,
  getCveUnderCveTask,
  getCveProgressUnderCveTask,
  getHostUnderRepoTask,
  getPlaybook,
  executeTask,
  getTaskProgress,
  rollbackCveTask
} from '@/api/leaks'
import configs from '@/config/defaultSettings'

const taskTypeMap = {
  'cve': '漏洞修复',
  'repo': 'REPO设置'
}
const rowKeyMap = {
  'cve': 'cve_id',
  'repo': 'host_id'
}

const statusTextMap = {
  'succeed': '修复成功',
  'fail': '待修复',
  'running': '运行中',
  'unknown': '未知',
  'set': '已设置',
  'unset': '未设置'
}

const statusValueMap = {
  'succeed': 'success',
  'fail': 'error',
  'running': 'processing',
  'unknown': 'default',
  'set': 'success',
  'unset': 'warning'
}

const defaultPagination = {
  current: 1,
  pageSize: 10,
  showSizeChanger: true,
  showQuickJumper: true
}

export default {
  name: 'LeakTaskDetail',
  components: {
    PageHeaderWrapper,
    HostStatusInTaskDrawer
  },
  data () {
    return {
      timer: '',
      taskId: this.$route.params.taskId,
      taskType: this.$route.params.taskType,
      detail: { statuses: {} },
      infoLoading: false,
      // cve/repo任务详情下表格数据
      tableData: [],
      tableIsLoading: false,
      pagination: defaultPagination,
      filters: null,
      sorter: null,
      cveProgressIsLoading: false,
      selectedRowKeys: [],
      selectedRowsAll: [],
      // 每个cve下host详情数据
      hostListUnderCveVisible: false,
      hostListOfCveId: null,

      taskTypeMap,
      rowKeyMap,
      statusTextMap,
      statusValueMap
    }
  },
  computed: {
    breadcrumb () {
      const routes = this.$route.meta.diyBreadcrumb.map((route) => {
        return {
          path: route.path,
          breadcrumbName: i18nRender(route.breadcrumbName)
        }
      })
      return {
        props: {
          routes,
          itemRender: ({ route, params, routes, paths, h }) => {
            // 若为路由diyBreadcrumb数组的最后一个元素，替换标题文本为其对应的任务名称
            if (routes.indexOf(route) === routes.length - 1) {
              return <span>{this.detail.task_name}</span>
            } else {
              return <router-link to={route.path}>{route.breadcrumbName}</router-link>
            }
          }
        }
      }
    },
    rowSelection () {
      return {
        selectedRowKeys: this.selectedRowKeys,
        onChange: this.onSelectChange
      }
    },
    cveColumns () {
      let { filters } = this
      filters = filters || {}

      return [
        {
          dataIndex: 'cve_id',
          title: 'CVE ID',
          scopedSlots: { customRender: 'cveId' }
        },
        {
          dataIndex: 'host_num',
          title: '主机',
          sorter: true,
          scopedSlots: { customRender: 'hosts' }
        },
        {
          dataIndex: 'package',
          title: '解决方案'
        },
        {
          dataIndex: 'reboot',
          title: '重启后生效',
          customRender: (reboot) => reboot ? '是' : '否',
          filteredValue: filters.reboot || null,
          filterMultiple: false,
          filters: [
            { text: '是', value: 'true' },
            { text: '否', value: 'false' }
          ]
        },
        {
          dataIndex: 'progress',
          title: '执行进度（已处理/总数）',
          scopedSlots: { customRender: 'progress' }
        },
        {
          dataIndex: 'status',
          title: '修复状态',
          width: 140,
          scopedSlots: { customRender: 'status' },
          filteredValue: filters.status || null,
          filters: [
            { text: '修复成功', value: 'succeed' },
            { text: '待修复', value: 'fail' },
            { text: '运行中', value: 'running' },
            { text: '未知', value: 'unknown' }
          ]
        }
      ]
    },
    repoColumns () {
      let { filters } = this
      filters = filters || {}
      return [
        {
          dataIndex: 'host_name',
          title: '主机名称',
          scopedSlots: { customRender: 'hostName' }
        },
        {
          dataIndex: 'host_ip',
          title: 'IP地址'
        },
        {
          dataIndex: 'repo_name',
          title: 'CVE REPO'
        },
        {
          dataIndex: 'status',
          title: '最新状态',
          width: 140,
          scopedSlots: { customRender: 'status' },
          filteredValue: filters.status || null,
          filters: [
            { text: '未设置', value: 'fail' },
            { text: '运行中', value: 'running' },
            { text: '未知', value: 'unknown' },
            { text: '已设置', value: 'set' }
          ]
        }
      ]
    }
  },
  methods: {
    dateFormat,
    handleTableChange (pagination, filters, sorter) {
      // 存储翻页状态
      this.pagination = pagination
      this.filters = Object.assign({}, this.filters, filters)
      this.sorter = sorter
      // 出发排序、筛选、分页时，重新请求主机列表
      if (this.taskType === 'cve') {
        this.getCveList()
      } else {
        this.getHostList()
      }
    },
    onSelectChange (selectedRowKeys, selectedRows) {
      const tableData = this.tableData
      this.selectedRowKeys = selectedRowKeys
      this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, tableData, 'cve_id')
    },
    resetSelection () {
      this.selectedRowKeys = []
      this.selectedRowsAll = []
    },
    getInfo () {
      const _this = this
      this.infoLoading = true
      getTaskInfo({
        taskId: this.taskId
      }).then(function (res) {
        _this.detail = res.result || {}
        _this.detail.statuses = {}
        // update progress
        _this.updateProgress([_this.taskId])
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.infoLoading = false
      })
    },
    // 轮训当前任务进度，没用running状态时停止
    updateProgress (taskList) {
      const _this = this
      this.progressLoading = true
      getTaskProgress({ taskList }).then(function (res) {
        _this.detail.statuses = res.result && res.result[_this.taskId]
        _this.detail = Object.assign({}, _this.detail)
        if (!_this.prgressFinishedCheck(res.result)) {
          _this.progressUpdateCaller = setTimeout(function () {
            _this.updateProgress(taskList)
          }, configs.taskProgressUpdateInterval)
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.progressLoading = false
      })
    },
    prgressFinishedCheck (statusMap) {
      for (const taskId in statusMap) {
        if (statusMap[taskId]['running']) {
          return false
        }
      }
      return true
    },
    // for cve task
    getCveList () {
      const _this = this
      this.tableIsLoading = true
      const pagination = this.pagination || {}
      const filters = this.filters || {}
      const sorter = this.sorter || {}
      getCveUnderCveTask({
        taskId: this.taskId,
        tableInfo: {
          pagination: {
            current: pagination.current,
            pageSize: pagination.pageSize
          },
          filters: filters,
          sorter: {
            field: sorter.field,
            order: sorter.order
          }
        }
      }).then(function (res) {
        _this.tableData = res.result || []
        _this.pagination = {
          ..._this.pagination,
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: res.total_count || (res.total_count === 0 ? 0 : pagination.total)
        }
        _this.updateCveProgress(_this.taskId, res.result.map(cve => cve.cve_id))
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () { _this.tableIsLoading = false })
    },
    updateCveProgress (taskId, cveList) {
      const _this = this
      this.cveProgressIsLoading = true
      getCveProgressUnderCveTask({
        taskId,
        cveList
      }).then(function (res) {
        _this.addCveProgressToList(res.result)
        const runningCveIds = _this.getRunningCve(res.result)
        if (runningCveIds.length > 0) {
          setTimeout(function () {
            _this.updateCveProgress(taskId, cveList)
          }, configs.taskProgressUpdateInterval)
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.cveProgressIsLoading = false
      })
    },
    // 将查询到的cve进度更新到表格数据中，用于数据展示
    addCveProgressToList (progressMap) {
      this.tableData.forEach(cveinfo => {
        if (progressMap[cveinfo.cve_id]) {
          cveinfo.progress = progressMap[cveinfo.cve_id] && progressMap[cveinfo.cve_id].progress
          cveinfo.status = progressMap[cveinfo.cve_id] && progressMap[cveinfo.cve_id].status
        }
      })
      this.tableData = Object.assign([], this.tableData)
    },
    getRunningCve (progressMap) {
      const arr = []
      for (const cveId in progressMap) {
        if (progressMap[cveId].status === 'running') {
          arr.push(cveId)
        }
      }
      return arr
    },
    // for repo task
    getHostList () {
      const _this = this
      this.tableIsLoading = true
      const pagination = this.pagination || {}
      const filters = this.filters || {}
      getHostUnderRepoTask({
        taskId: this.taskId,
        tableInfo: {
          pagination: {
            current: pagination.current,
            pageSize: pagination.pageSize
          },
          filters: filters
        }
      }).then(function (res) {
        _this.tableData = res.result || []
        _this.pagination = {
          ..._this.pagination,
          current: pagination.current,
          pageSize: pagination.pageSize,
          total: res.total_count || (res.total_count === 0 ? 0 : pagination.total)
        }
        if (_this.hostRepostatusCheck(res.result)) {
          setTimeout(function () {
            _this.getHostList()
          }, configs.taskProgressUpdateInterval)
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () { _this.tableIsLoading = false })
    },
    hostRepostatusCheck (dataList) {
      const runningHost = dataList.filter(host => host.status === 'running')[0]
      if (runningHost) {
        return true
      } else {
        return false
      }
    },
    // 下载playbook
    handleGetPlaybook () {
      const _this = this
      getPlaybook({
        taskId: this.taskId,
        taskType: this.taskType
      }).then(function (res) {
        // download files
        downloadBlobFile(res.data, res.fileName)
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      })
    },
    executeTask () {
      const _this = this
      if (this.detail.statuses['running'] > 0) {
        this.$warning({
          title: '有任务正在运行，不能执行。'
        })
        return
      }
      this.$confirm({
        title: `确定执行任务${this.detail.task_name}?`,
        icon: () => <a-icon type="exclamation-circle" />,
        okText: '执行',
        onOk: function () {
          return executeTask(_this.taskId).then(function (res) {
            _this.$message.success(res.msg)
            // 执行任务成功后刷新
            setTimeout(function () {
               _this.getInitalData()
            }, 3000)
            // _this.getInitalData()
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          })
        }
      })
    },
    showHostListUnderCve (cveId) {
      this.hostListUnderCveVisible = true
      this.hostListOfCveId = cveId
    },
    closeHostListUnderCve () {
      this.hostListUnderCveVisible = false
    },
    getInitalData () {
      this.getInfo()
      switch (this.taskType) {
        case 'cve':
          this.getCveList()
          break
        case 'repo':
          this.getHostList()
          break
      }
    },
    handleRollback () {
      const _this = this
      if (this.detail.statuses['running'] > 0) {
        this.$warning({
          title: '有任务正在运行，不能回滚。'
        })
        return
      }
      this.$confirm({
        title: <p>回滚后无法恢复<br/>请确认回滚CVE修复任务：</p>,
        content: _this.selectedRowKeys.map(cveId => <p>{ cveId }</p>),
        icon: () => <a-icon type="exclamation-circle" />,
        okText: '回滚',
        okType: 'danger',
        onOk: function () {
          return rollbackCveTask({
            taskId: _this.taskId,
            cveList: _this.selectedRowKeys
          }).then(function (res) {
            _this.$message.success(res.msg)
            _this.getInitalData()
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          }).finally(function () {
            _this.selectedRowKeys = []
            _this.selectedRowsAll = []
          })
        }
      })
    },
    onSearch (text) {
      this.pagination = defaultPagination
      if (!this.filters) {
        this.filters = {}
      }
      if (this.taskType === 'cve') {
        if (text !== '') {
          this.filters.cveId = text
        } else {
          this.filters.cveId = undefined
        }
        this.getCveList()
      } else {
        if (text !== '') {
          this.filters.hostName = text
        } else {
          this.filters.hostName = undefined
        }
        this.getHostList()
      }
    }
  },
  mounted: function () {
    this.getInitalData()
  }
}
</script>

<style lang="less" scoped>
.color {
  &-check-circle {
    color: #52c41a;
  }
  &-close-circle {
    color: #f5222d;
  }
  &-running-circle {
    color: #722ed1;
  }
  &-standby-circle {
    color: #666
  }
}

.task-status {
  cursor: pointer
}

.result-label {
  text-align: right;
}
.result-content {
  white-space: pre;
  border: 1px solid #ddd;
  border-radius: 4px;
  padding:4px;
}

.detail-info-content{
  h1 {
    font-size: 24px;
    font-weight: bold;
    color: rgba(0,0,0,.65);
  }
  padding: 0 12px 0 24px;
}
.reuslt-item-title{
  font-weight: 500;
  color: rgba(0,0,0,.85)
}
/deep/ .ant-descriptions-item {
  .ant-descriptions-item-label {
    font-weight: 500;
  }
}
.result-log {
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 4px 6px 20px;
}
</style>
