
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false">
      <div>
        <a-row class="aops-table-control-row" type="flex" justify="space-between">
          <a-col>
            <a-row type="flex" :gutter="16">
              <a-col>
                <drawer-view title="新建故障诊断">
                  <template slot="click">
                    <a-button type="primary">
                      故障诊断<a-icon type="plus"/>
                    </a-button>
                  </template>
                  <template slot="drawerView">
                    <add-fault-diagnosis :saveSuccess="addFaultDiagnosisSuccess" :faultTreeList="treeData"></add-fault-diagnosis>
                  </template>
                </drawer-view>
              </a-col>
            </a-row>
          </a-col>
        </a-row>
        <a-table
          :rowKey="rowKey"
          :columns="columns"
          :data-source="tableData"
          :pagination="pagination"
          :row-selection="rowSelection"
          @change="handleTableChange"
          :loading="tableIsLoading">
              <span slot="progress" slot-scope="record">
                <a-progress :percent="record.progress" size="small" status="active" />
              </span>
              <span slot="action" slot-scope="record">
                <router-link :to="{ path: '/diagnosis/diag-report/'+record.progress }" target="_blank">查看报告</router-link>
                <a-divider type="vertical" />
                <a href="#" @click="diagnosisDelete(record)">删除</a>
              </span>
        </a-table>
      </div>
    </a-card>
    <a-card :bordered="false" style="margin-top: 12px">
      <div class="ant-pro-pages-list-applications-filterCardList">
        <a-list :loading="loading" :data-source="currentTreeData" :grid="{ gutter: 24, xl: 3, lg: 3, md: 3, sm: 2, xs: 1 }" >
          <a-list-item slot="renderItem" slot-scope="item">
            <template v-if="!item || item.tree_name === ''">
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
                      <img class="avatar-img" :src="item.avatar">
                    </div>
                    <div class="content-div">
                      <div class="title">{{item.tree_name}}</div>
                      <div class="remark">{{item.content}}</div>
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
                                title="您确定要删除该信息吗?"
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
      <div style="text-align: center"><a @click="getMoreTree">加载更多</a></div>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
  import { getReportList, getDiagTree, getDiagProgress, delDiagReport, delDiagTree } from '@/api/diagnosis'
  import DrawerView from '@/views/utils/DrawerView'
  import AddFaultTree from '@/views/diagnosis/components/AddFaultTree'
  import AddFaultDiagnosis from '@/views/diagnosis/components/AddFaultDiagnosis'
  // import CardInfo from './components/CardInfo'
  const columns = [
    {
      dataIndex: 'task_id',
      key: 'task_id',
      title: '任务ID',
      sorter: false
    },
    {
      dataIndex: 'tree_name',
      key: 'tree_name',
      title: '所用故障树'
    },
    {
      dataIndex: 'time',
      key: 'time',
      title: '诊断时间段'
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
        pagination: {
          current: 1,
          pageSize: 10,
          showSizeChanger: true,
          showQuickJumper: true
        },
        filters: {},
        sorter: {},
        columns,
        tableData: [],
        selectedRowKeys: [],
        tableIsLoading: false,
        treeData: [],
        currentTreeData: [],
        currentTreeData_index: 0,
        loading: true
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
      tableFilters () {
        return {
          ...this.filters
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
      this.getDiagTree({
        pagination: this.tablePagination
      })
      // const _this = this
      // setInterval(function () {
      //   if (_this.tableData.length > 0) {
      //     _this.loadDiagProgress(_this.tableData)
      //   }
      // }, 30000)
    },
    methods: {
      addDiagTreeSuccess () {
        console.log('刷新故障树列表页')
      },
      addFaultDiagnosisSuccess () {
        this.refreshFaultDiagnosisList()
        console.log('刷新故障诊断列表页')
      },
      handleTableChange (pagination, filters, sorter) {
        // 设置翻页状态
        this.pagination = pagination
        this.filters = filters
        this.sorter = sorter
        // 出发排序、筛选、分页时，重新请求主机列表
        this.getHostList({
          pagination: this.tablePagination,
          filters: this.tableFilters,
          sorter: this.tableSorter
        })
      },
      onSelectChange (selectedRowKeys, selectedRows) {
        console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows)
        this.selectedRowKeys = selectedRowKeys
      },
      refreshFaultDiagnosisList () {
        const that = this
        that.getFaultDiagnosisList({
          pagination: that.tablePagination,
          filters: that.tableFilters,
          sorter: that.tableSorter
        })
      },
      // 获取列表数据
      getFaultDiagnosisList (tableInfo) {
        const _this = this
        this.tableIsLoading = true

        getReportList({
          uid: '123',
          tableInfo
        })
          .then(function (res) {
            _this.tableData = res.result.host_infos
            _this.loadDiagProgress(_this.tableData)
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      // 获取故障树列表
      getDiagTree: function (tableInfo) {
        const _this = this
        this.loading = true
        getDiagTree({
          uid: '123',
          tableInfo
        }).then(function (res) {
          _this.treeData = res.result.diagTree_infos
          if (_this.treeData.length > 5) {
            for (let i = 0; i < 6; i++) {
              _this.currentTreeData.push(_this.treeData[i])
            }
            _this.currentTreeData_index = 6
          } else {
            _this.currentTreeData = _this.treeData
            _this.currentTreeData_index = _this.treeData.length
          }
          _this.loading = false
        }).catch(function (err) {
          _this.$message.error(err.response.data.message)
          _this.loading = false
        }).finally(function () {
          _this.loading = false
        })
      },
      // 加载更多故障树
      getMoreTree () {
        const _this = this
        if (_this.treeData.length > _this.currentTreeData_index + 6) {
          for (let i = _this.currentTreeData_index; i < _this.currentTreeData_index + 6; i++) {
            _this.currentTreeData.push(_this.treeData[i])
          }
          _this.currentTreeData_index = _this.currentTreeData_index + 6
        } else {
          for (let i = _this.currentTreeData_index; i < _this.treeData.length; i++) {
            _this.currentTreeData.push(_this.treeData[i])
            _this.currentTreeData_index = _this.treeData.length
          }
        }
      },
      // 删除故障诊断报告
      diagnosisDelete (record) {
        const _this = this
        const reportList = []
        reportList.push(record.report_id)
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
          delDiagReport({
            uid: '123',
            reportList
          }).then((res) => {
              _this.$message.success('删除成功')
              _this.refreshFaultDiagnosisList()
              if (isBash) _this.selectedRowKeys = []
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.message)
              reject(err)
            })
        })
      },
      // 获取故障诊断进度
      loadDiagProgress (taskData) {
          const _this = this
          const taskList = []
          taskData.forEach(function (item) {
            taskList.push(item.task_id)
          })
          getDiagProgress({
            uid: '123',
            taskList
          }).then(function (res) {
            const newTableData = []
            _this.tableData.forEach(function (item) {
              res.result.diagProgress_infos.forEach(function (childItem) {
                if (item.task_id === childItem.task_id) {
                  item.progress = childItem.progress
                }
              })
              newTableData.push(item)
            })
            _this.tableData = newTableData
            console.log(res.result.diagProgress_infos)
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () {
        })
      },
      // 导出故障树
      getdiagtree () {
        console.log('导出故障树')
      },
      // 删除故障树
      deletediagtree (treeName) {
        const _this = this
        const treeList = []
        treeList.push(treeName)
        delDiagTree({
          uid: '123',
          treeList
        }).then(function (res) {
            _this.$message.success(res.message)
            _this.getDiagTree({
              pagination: _this.tablePagination
            })
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () {
        })
      }
    }
  }
</script>

<style lang="less" scoped>
  .avatar-div {
    float: left;
    width: 60px;
  }
  .avatar-img {
    height: 60px;
    width: 60px
  }
  .content-div {
    float: left;margin-left: 10px;
    width: 77%;
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
    height: 158px;
  }
</style>
