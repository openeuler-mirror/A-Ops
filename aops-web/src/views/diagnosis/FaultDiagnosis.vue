
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false">
      <div>
        <a-row class="aops-table-control-row" type="flex" justify="space-between">
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
        <a-table
          :rowKey="rowKey"
          :columns="columns"
          :data-source="taskList"
          :pagination="pagination"
          :row-selection="rowSelection"
          @change="handleTableChange"
          :loading="tableIsLoading"
        >
          <span slot="progress" slot-scope="record">
            <a-progress :percent="record.progressPercent" size="small" :status="record.progressPercent === 100 ? 'success' : 'active'" />
          </span>
          <span slot="action" slot-scope="record">
            <a @click="handleReportListOpen(record)">查看报告</a>
            <a-divider type="vertical" />
            <a href="#" @click="diagnosisDelete(record)">删除</a>
          </span>
        </a-table>
      </div>
    </a-card>
    <a-card :bordered="false" style="margin-top: 12px">
      <div class="ant-pro-pages-list-applications-filterCardList">
        <a-list :loading="loading" :data-source="treeData.slice(0,showIndex)" :grid="{ gutter: 24, xl: 3, lg: 3, md: 3, sm: 2, xs: 1 }" >
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
              <router-link :to="{ path: '/diagnosis/fault-trees/'+item.tree_name }" target="_blank">
                <a-card>
                  <div>
                    <div class="avatar-div">
                      <img class="avatar-img" src="~@/assets/vertical-left.png">
                    </div>
                    <div class="content-div">
                      <div class="title">{{ item.tree_name }}</div>
                      <div class="remark">{{ item.description }}</div>
                    </div>
                  </div>
                  <template slot="actions">
                    <div @click.prevent>
                      <div class="tagList">
                        <a-tag>3C</a-tag>
                        <a-tag>故障重启</a-tag>
                        <a-tag>硬件</a-tag>
                      </div>
                      <div style="float: right;width: 100px;border-left: 1px solid #ddd">
                        <a-tooltip title="编辑" style="float: left;width: 50%;text-align: center;line-height: 22px">
                          <a-icon type="edit" />
                        </a-tooltip>
                        <a-dropdown style="float: right;width: 50%">
                          <a class="ant-dropdown-link">
                            <a-icon type="ellipsis" />
                          </a>
                          <a-menu slot="overlay">
                            <a-menu-item>
                              <a href="javascript:;" @click="getdiagtree">导出</a>
                            </a-menu-item>
                            <a-menu-item>
                              <a-popconfirm
                                title="您确定要删除该故障树吗?"
                                ok-text="确认"
                                cancel-text="取消"
                                @confirm="deletediagtree(item.tree_name)"
                              >
                                <a href="javascript:;" >删除</a>
                              </a-popconfirm>
                            </a-menu-item>
                          </a-menu>
                        </a-dropdown>
                      </div>
                    </div>
                  </template>
                </a-card>
              </router-link>
            </template>
          </a-list-item>
        </a-list>
      </div>
      <div style="text-align: center" v-if="treeData.length>showIndex"><a @click="showIndex = showIndex+6">加载更多</a></div>
    </a-card>
    <a-drawer
      title="诊断报告列表"
      :width="720"
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
        </span>
      </a-table>
    </a-drawer>
  </my-page-header-wrapper>
</template>

<script>
  import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
  import { getTaskList, getProgress, getReportList, getDiagTree, delDiagReport, delDiagTree } from '@/api/diagnosis'
  import DrawerView from '@/views/utils/DrawerView'
  import AddFaultTree from '@/views/diagnosis/components/AddFaultTree'
  import AddFaultDiagnosis from '@/views/diagnosis/components/AddFaultDiagnosis'
  import { dateFormat } from '@/views/utils/Utils'

  import defaultSettings from '@/config/defaultSettings'
  // import CardInfo from './components/CardInfo'
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
      title: '诊断进度',
      scopedSlots: { customRender: 'progress' }
    },
    {
      key: 'operation',
      title: '操作',
      scopedSlots: { customRender: 'action' }
    }
  ]
  const reportListColumns = [
    {
      key: 'check',
      title: '查看',
      scopedSlots: { customRender: 'check' }
    },
    {
      dataIndex: 'host_id',
      key: 'host_id',
      title: '主机名'
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
      customRender: (text, item) => `${dateFormat('YYYY-mm-dd HH:MM', item.start * 1000)} - ${dateFormat('YYYY-mm-dd HH:MM', item.end * 1000)}`
    }
  ]
  export default {
    name: 'FaultDiagnosis',
    components: {
      MyPageHeaderWrapper,
      DrawerView,
      AddFaultTree,
      AddFaultDiagnosis
    },
    data () {
      return {
        rowKey: 'task_id',
        taskList: [],
        pagination: {
          current: 1,
          pageSize: 5,
          total: 0,
          showSizeChanger: true,
          showQuickJumper: true
        },
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
        }
      }
    },
    computed: {
      rowSelection () {
        return {
          onChange: this.onSelectChange
        }
      },
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
        reportList.push(record.task_id)
        this.$confirm({
          title: (<div><p>删除后无法恢复</p><p>请确认删除以下故障诊断报告:</p></div>),
          content: () => record.task_id,
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
              _this.$message.success('删除成功')
              _this.refreshFaultDiagnosisList()
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
                  item.progressPercent = Math.floor((progressItem.progress / item.expected_report_num) * 100)
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
            _this.$message.success('删除成功')
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
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.reportListLoading = false })
      }
    }
  }
</script>

<style lang="less" scoped>
  .avatar-div {
    float: left;
    width: 80px;
  }
  .avatar-img {
    height: 60px;
    width: 80px
  }
  .content-div {
    float: left;
    margin-left: 10px;
    width: calc(100% - 90px);
  }
  .title {
    font-weight: 600;
  }
  .tagList{
    float: left;
    text-align: left;
    padding-left: 10px;
    text-overflow: -o-ellipsis-lastline;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
  }
  .tagList span{cursor: pointer}
  .remark {
    text-overflow: -o-ellipsis-lastline;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 2;
    line-clamp: 2;
    -webkit-box-orient: vertical;
  }
  .new-btn {
    background-color: #fff;
    border-radius: 2px;
    width: 100%;
    height: 157px;
  }
</style>
