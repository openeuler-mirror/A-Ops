
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div>
        <a-row class="aops-table-control-row" type="flex" justify="space-between">
          <a-col>
            <h3>
              诊断任务
              <a-icon
                :type="expandedStatus[0] ? 'caret-up' : 'caret-down'"
                @click="setExpandStatus(0, !expandedStatus[0])"
              />
            </h3>
          </a-col>
          <a-col>
            <a-row type="flex" :gutter="16">
              <a-col>
                <drawer-view title="新建故障诊断" :bodyStyle="{ paddingBottom: '80px' }">
                  <template slot="click">
                    <a-button type="primary">
                      故障诊断<a-icon type="plus"/>
                    </a-button>
                  </template>
                  <template slot="drawerView">
                    <add-fault-diagnosis
                      :saveSuccess="addFaultDiagnosisSuccess"
                      :faultTreeList="treeData"
                    ></add-fault-diagnosis>
                  </template>
                </drawer-view>
              </a-col>
            </a-row>
          </a-col>
        </a-row>
        <div v-show="expandedStatus[0]">
          <a-table
            :rowKey="rowKey"
            :columns="columns"
            :data-source="taskList"
            :pagination="pagination"
            @change="handleTableChange"
            :loading="tableIsLoading"
          >
            <span slot="action" slot-scope="record">
              <a @click="handleReportListOpen(record)">查看报告</a>
            </span>
          </a-table>
        </div>
      </div>
    </a-card>
    <a-card :bordered="false" class="aops-theme" style="margin-top: 20px">
      <h3>
        故障树
        <a-icon
          :type="expandedStatus[1] ? 'caret-up' : 'caret-down'"
          @click="setExpandStatus(1, !expandedStatus[1])"
        />
      </h3>
      <div class="ant-pro-pages-list-applications-filterCardList" v-show="expandedStatus[1]">
        <a-list :loading="loading" :data-source="treeData.slice(0,showIndex)" :grid="{ gutter: 24, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }" >
          <a-list-item slot="renderItem" slot-scope="item">
            <template v-if="!item.tree_name">
              <drawer-view title="新增故障树">
                <template slot="click">
                  <a-button class="new-btn" type="dashed">
                    <a-icon type="plus"/>新增故障树
                  </a-button>
                </template>
                <template slot="drawerView">
                  <add-fault-tree :saveSuccess="addDiagTreeSuccess"></add-fault-tree>
                </template>
              </drawer-view>
            </template>
            <template v-else>
              <subject-card
                :linkTo="'/diagnosis/fault-trees/'+item.tree_name"
                :itemLabel="item.tree_name"
                :itemContent="item.description"
                :tagList="['3C', '故障重启', '硬件']"
              >
                <template #logoImg>
                  <img src="~@/assets/dtree-icon.png">
                </template>
                <a-tooltip placement="bottom">
                  <template slot="title">
                    编辑
                  </template>
                  <a-icon type="edit" />
                </a-tooltip>
                <a-tooltip placement="bottom">
                  <template slot="title">
                    导出
                  </template>
                  <a-icon type="download" />
                </a-tooltip>
                <a-popconfirm
                  title="您确定要删除该故障树吗?"
                  ok-text="确认"
                  cancel-text="取消"
                  @confirm="deletediagtree(item.tree_name)"
                >
                  <a-tooltip placement="bottom">
                    <template slot="title">
                      删除
                    </template>
                    <a-icon type="delete" />
                  </a-tooltip>
                </a-popconfirm>
              </subject-card>
            </template>
          </a-list-item>
        </a-list>
      </div>
      <div style="text-align: center" v-if="treeData.length>showIndex"><a @click="showIndex = showIndex+6">加载更多</a></div>
    </a-card>
    <a-drawer
      title="诊断报告列表"
      :width="800"
      :visible="reportListVisible"
      @close="handleReportListClose"
    >
      <div>
        {{ `已生成/总报告数：${taskProgressStatus.finished} / ${taskProgressStatus.total}` }}
      </div>
      <a-table
        rowKey="report_id"
        :dataSource="reportList"
        :loading="reportListLoading"
        :columns="reportListColumns"
        :pagination="reportListPagination"
        @change="reportListChange"
      >
        <span slot="check" slot-scope="report">
          <router-link :to="{ path: '/diagnosis/diag-report/'+report.report_id }" target="_blank">查看</router-link>
          <a-divider type="vertical" />
          <a href="#" @click="diagnosisDelete(report)">删除</a>
        </span>
        <span slot="hName" slot-scope="hostName">
          <a-spin v-if="hostInfoLoading" />
          <span v-else>{{ hostName }}</span>
        </span>
      </a-table>
    </a-drawer>
  </my-page-header-wrapper>
</template>

<script>
// this component is abandoned
  import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
  import { getTaskList, getProgress, getReportList, getDiagTree, delDiagReport, delDiagTree } from '@/api/diagnosis'
  import { hostInfo } from '@/api/assest'
  import DrawerView from '@/views/utils/DrawerView'
  import AddFaultTree from '@/views/diagnosis/components/AddFaultTree'
  import AddFaultDiagnosis from '@/views/diagnosis/components/AddFaultDiagnosis'
  import SubjectCard from '@/components/SubjectCard'
  import { dateFormat } from '@/views/utils/Utils'

  import defaultSettings from '@/config/defaultSettings'
  const columns = [
    {
      dataIndex: 'task_id',
      key: 'task_id',
      title: '任务ID',
      sorter: false
    },
    {
      title: '所用故障树',
      customRender: (text, item) => item.tree_list.join(', ')
    },
    {
      title: '诊断时间段',
      customRender: (text, item) => item.time_range.map(time => dateFormat('YYYY-mm-dd HH:MM:SS', time * 1000)).join(' 至 ')
    },
    {
      key: 'progress',
      title: '诊断报告',
      customRender: (text, item) => `${item.progress}/${item.expected_report_num}`
    },
    {
      key: 'operation',
      title: '操作',
      width: '90px',
      scopedSlots: { customRender: 'action' }
    }
  ]
  const reportListColumns = [
    {
      key: 'check',
      title: '操作',
      scopedSlots: { customRender: 'check' }
    },
    {
      dataIndex: 'host_name',
      key: 'host_name',
      title: '主机名',
      scopedSlots: { customRender: 'hName' }
    },
    {
      dataIndex: 'tree_name',
      key: 'tree_name',
      title: '所用故障树',
      sorter: false
    },
    {
      key: 'tiemRange',
      title: '诊断时间段',
      customRender: (text, item) => `${dateFormat('YYYY-mm-dd HH:MM:SS', item.start * 1000)} - ${dateFormat('YYYY-mm-dd HH:MM:SS', item.end * 1000)}`
    }
  ]
  const defaultPagination = {
    current: 1,
    pageSize: 10,
    total: 0,
    showSizeChanger: true,
    showQuickJumper: true
  }
  export default {
    name: 'FaultDiagnosis',
    components: {
      MyPageHeaderWrapper,
      DrawerView,
      AddFaultTree,
      AddFaultDiagnosis,
      SubjectCard
    },
    data () {
      return {
        rowKey: 'task_id',
        taskList: [],
        pagination: defaultPagination,
        filters: {},
        sorter: {},
        columns,
        reportListColumns,
        selectedRowKeys: [],
        tableIsLoading: false,
        treeData: [],
        showIndex: 6,
        loading: true,
        loadProgressInterval: '',
        reportListVisible: false,
        taskId: undefined,
        reportList: [],
        reportListLoading: false,
        reportListPagination: {
          current: 1,
          pageSize: 10
        },
        taskOfReportList: undefined,
        taskProgressStatus: {
          finished: 0,
          total: 0
        },
        hostInfoLoading: false,
        expandedStatus: [true, true]
      }
    },
    computed: {
      tablePagination () {
        return {
          current: this.pagination.current,
          pageSize: this.pagination.pageSize
        }
      },
      tableSorter () {
        return {
          field: this.sorter.field,
          order: this.sorter.order
        }
      }
    },
    mounted: function () {
      this.refreshFaultDiagnosisList()
      this.getDiagTree()
      const _this = this
      this.loadProgressInterval = setInterval(function () {
        if (_this.taskList.length > 0) {
          _this.loadDiagProgress(_this.taskList)
        }
      }, defaultSettings.faultDiagnosisPropressInterval)
    },
    destroyed: function () {
      clearInterval(this.loadProgressInterval)
    },
    methods: {
      addDiagTreeSuccess () {
        this.refreshgDiagTree()
      },
      refreshgDiagTree () {
        const _this = this
        this.loading = true
        setTimeout(function () {
          _this.getDiagTree()
        }, 1500)
      },
      addFaultDiagnosisSuccess () {
        this.pagination = defaultPagination
        this.refreshFaultDiagnosisList()
      },
      handleTableChange (pagination, filters, sorter) {
        // 设置翻页状态
        this.pagination = pagination
        this.sorter = sorter
        this.getTaskList({
          pagination: pagination,
          sorter: sorter
        })
      },
      onSelectChange (selectedRowKeys, selectedRows) {
        this.selectedRowKeys = selectedRowKeys
      },
      refreshFaultDiagnosisList () {
        const that = this
        that.tableIsLoading = true
        setTimeout(function () {
          that.getTaskList({
            pagination: that.tablePagination,
            sorter: that.tableSorter
          })
        }, 1500)
      },
      // 获取诊断任务列表
      getTaskList (tableInfo) {
        const that = this
        const pagination = that.pagination || {}
        that.tableIsLoading = true
        tableInfo.sort = 'time'
        tableInfo.direction = 'desc'
        getTaskList(tableInfo).then(function (data) {
          that.taskList = data.task_infos
          var taskMap = {}
          var taskIdArray = []
          that.taskList.forEach(function (task) {
            taskMap[task.task_id] = task
            taskIdArray.push(task.task_id)
          })
          that.pagination = {
            ...that.pagination,
            current: pagination.current,
            pageSize: pagination.pageSize,
            total: data.total_count || (data.total_count === 0 ? 0 : pagination.total)
          }

          if (taskIdArray.length > 0) {
            that.updateProgress(taskIdArray)
          }
        }).catch(function (err) {
          that.$message.error(err.response.data.msg)
        }).finally(() => {
          that.tableIsLoading = false
        })
      },
      // 获取故障树列表
      getDiagTree: function () {
        const _this = this
        this.loading = true
        const treeList = []
        getDiagTree({
          treeList
        }).then(function (res) {
          _this.treeData = [{}]
          _this.treeData.push(...res.trees)
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.loading = false
        })
      },
      // 删除故障诊断报告
      diagnosisDelete (record) {
        const _this = this
        const reportList = []
        reportList.push(record.report_id)
        this.$confirm({
          title: (<div><p>删除后无法恢复</p></div>),
          content: () => '请确认删除该报告',
          icon: () => <a-icon type="exclamation-circle" />,
          okType: 'danger',
          okText: '删除',
          onOk: function () { return _this.handleDeleteDiagnosis(reportList, true) },
          onCancel () {}
        })
      },
      // 删除故障诊断报告
      handleDeleteDiagnosis (reportList, isBash) {
        const _this = this
        return new Promise((resolve, reject) => {
          delDiagReport(reportList).then((res) => {
              _this.$message.success(res.msg)
              _this.refreshFaultDiagnosisList()
              _this.refreshReportList()
              if (isBash) _this.selectedRowKeys = []
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      },
      updateProgress (taskIdList) {
        const _this = this
        getProgress(taskIdList).then(function (res) {
            const newTableData = []
            _this.taskList.forEach(function (item) {
              res.result.forEach(function (progressItem) {
                if (item.task_id === progressItem.task_id) {
                  item.progress = progressItem.progress
                  if (progressItem.progress === 0 && item.expected_report_num === 0) {
                    item.progressPercent = 100
                  } else {
                    item.progressPercent = Math.floor((progressItem.progress / item.expected_report_num) * 100)
                  }
                }
              })
              newTableData.push(item)
            })
            _this.taskList = newTableData
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
        }).finally(function () {})
      },
      // 获取故障诊断进度
      loadDiagProgress (taskData) {
          const taskList = []
          taskData.forEach(function (item) {
            taskList.push(item.task_id)
          })
          this.updateProgress(taskList)
      },
      // 导出故障树
      getdiagtree () {
      },
      // 删除故障树
      deletediagtree (treeName) {
        const _this = this
        const treeList = []
        treeList.push(treeName)
        delDiagTree({
          treeList
        }).then(function (res) {
            _this.$message.success(res.msg)
            _this.refreshgDiagTree()
          }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
      },
      handleReportListOpen (task) {
        this.taskOfReportList = task.task_id
        this.taskProgressStatus = {
          finished: task.progress,
          total: task.expected_report_num
        }
        this.reportListPagination = {
          current: 1,
          pageSize: 10
        }
        this.reportListVisible = true
        this.handleGetReportList(task.task_id)
      },
      handleReportListClose () {
        this.reportListVisible = false
      },
      reportListChange (pagination) {
        this.reportListPagination = pagination
        this.handleGetReportList(this.taskOfReportList)
      },
      refreshReportList () {
        const _this = this
        this.reportListLoading = true
        setTimeout(function () {
          _this.handleGetReportList(_this.taskOfReportList)
        }, 1500)
      },
      handleGetReportList (taskId) {
        const _this = this
        const reportListPagination = this.reportListPagination || {}

        this.reportListLoading = true
        getReportList({
          taskId,
          pagination: reportListPagination
        }).then(function (res) {
          _this.reportList = res.result || []
          _this.reportListPagination = {
            ..._this.reportListPagination,
            current: reportListPagination.current,
            pageSize: reportListPagination.pageSize,
            total: res.total_count || (res.total_count === 0 ? 0 : reportListPagination.total)
          }
          // 获取列表时，根据列表数量更新
          _this.taskProgressStatus = Object.assign({}, {
            ..._this.taskProgressStatus,
            finished: res.total_count
          })
          if (res.result.length > 0) {
            _this.hostInfoLoading = true
            hostInfo({
              basic: true,
              host_list: res.result.map(report => report.host_id)
            }).then(function (res) {
              _this.reportList = _this.reportList.map(report => {
                const temp = Object.assign({}, report)
                const matchedItem = res.host_infos.filter(host => host.host_id === report.host_id)[0]
                if (matchedItem) {
                  temp.host_name = matchedItem.host_name
                }
                return temp
              })
            }).catch(function (err) {
              _this.$message.error(err.response.data.msg)
            }).finally(() => {
              _this.hostInfoLoading = false
            })
          }
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.reportListLoading = false })
      },
      // 控制面板展开
      setExpandStatus (idx, isExpaned) {
        const newStatuses = Object.assign({}, this.expandedStatus)
        newStatuses[idx] = isExpaned
        this.expandedStatus = newStatuses
      }
    }
  }
</script>

<style lang="less" scoped>
  .new-btn {
    background-color: #fff;
    border-radius: 2px;
    width: 100%;
    height: 175px;
  }
</style>
