
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div>
        <div>
          <h3 class="card-title">
            部署任务列表
            <a-icon
              :type="expandedStatus[0] ? 'caret-up' : 'caret-down'"
              @click="setExpandStatus(0, !expandedStatus[0])"
            />
          </h3>
        </div>
        <div v-show="expandedStatus[0]">
          <a-row class="aops-app-table-control-row" type="flex" justify="space-between">
            <a-col>
              <a-row type="flex" :gutter="6">
                <a-col>
                  <a-alert type="info" show-icon class="selection-alert">
                    <div slot="message">
                      <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
                      <a v-if="selectedRowKeys.length > 0" @click="resetSelection">清除选择</a>
                    </div>
                  </a-alert>
                </a-col>
                <a-col>
                  <a-button :disabled="selectedRowKeys.length <= 0" @click="deleteTaskBash(selectedRowKeys, selectedRowsAll)">批量删除</a-button>
                </a-col>
                <a-col>
                  <a-button :disabled="selectedRowKeys.length <= 0" @click="executeTaskBash(selectedRowKeys, selectedRowsAll)">批量执行</a-button>
                </a-col>
              </a-row>
            </a-col>
            <a-col>
              <a-row type="flex" :gutter="16">
                <a-col>
                  <drawer-view title="新增部署任务">
                    <template slot="click">
                      <a-button type="primary">
                        新增部署任务<a-icon type="plus"/>
                      </a-button>
                    </template>
                    <template slot="drawerView">
                      <add-task :saveSuccess="addTaskSuccess"></add-task>
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
            :loading="tableIsLoading"
          >
            <span slot="name" slot-scope="text">
              <cut-text :text="text" :length="20"/>
            </span>
            <span slot="desc" slot-scope="text">
              <cut-text :text="text" :length="20"/>
            </span>
            <span slot="action" slot-scope="record">
              <a @click="executeTask(record)">执行</a>
              <a-divider type="vertical" />
              <a-popconfirm title="你确定删除这个任务吗?" ok-text="确认" cancel-text="取消" @confirm="deleteTask(record)">
                <a-icon slot="icon" type="close-circle" style="color: red" />
                <a>删除</a>
              </a-popconfirm>
            </span>
          </a-table>
        </div>
      </div>
    </a-card>
    <a-card :bordered="false" class="aops-theme" style="margin-top: 20px">
      <h3>
        Playbook模板
        <a-icon
          :type="expandedStatus[1] ? 'caret-up' : 'caret-down'"
          @click="setExpandStatus(1, !expandedStatus[1])"
        />
      </h3>
      <div class="ant-pro-pages-list-applications-filterCardList" v-show="expandedStatus[1]">
        <a-list :loading="templateIsLoading" :data-source="templateData.slice(0,showIndex)" :grid="{ gutter: 24, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }" >
          <a-list-item slot="renderItem" slot-scope="item">
            <template v-if="!item.template_name">
              <drawer-view title="新增playbook模板">
                <template slot="click">
                  <a-button class="new-btn" type="dashed">
                    <a-icon type="plus"/>新增playbook模板
                  </a-button>
                </template>
                <template slot="drawerView">
                  <add-template :saveSuccess="addTemplateSuccess"></add-template>
                </template>
              </drawer-view>
            </template>
            <template v-else>
              <subject-card
                :itemLabel="item.template_name"
                :itemContent="item.description"
                :tagList="['安装', '用户管理', '加密']"
              >
                <template #logoImg>
                  <img class="avatar-img" src="~@/assets/playbook-icon.png">
                </template>
                <a-tooltip placement="bottom">
                  <template slot="title">
                    编辑
                  </template>
                  <a-icon type="edit" />
                </a-tooltip>
                <a-popconfirm
                  title="您确定要删除该模板吗?"
                  ok-text="确认"
                  cancel-text="取消"
                  @confirm="deleteTemplate(item.template_name)"
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
      <div style="text-align: center" v-if="templateData.length>showIndex"><a @click="showIndex = showIndex+6">加载更多</a></div>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
  import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
  import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
  import DrawerView from '@/views/utils/DrawerView'
  import AddTask from '@/views/task/components/AddTask'
  import AddTemplate from '@/views/task/components/AddTemplate'
  import SubjectCard from '@/components/SubjectCard'
  import CutText from '@/components/CutText'

  import { getSelectedRow } from '@/views/utils/getSelectedRow'
  import { getTaskList, deleteTask, executeTask, getTemplateList, deleteTemplate } from '@/api/task'

  const defaultPagination = {
    current: 1,
    pageSize: 10,
    showSizeChanger: true,
    showQuickJumper: true
  }
  const columns = [
    {
      dataIndex: 'task_id',
      key: 'task_id',
      title: '任务ID',
      sorter: false
    },
    {
      dataIndex: 'task_name',
      key: 'task_name',
      title: '任务名称',
      scopedSlots: { customRender: 'name' }
    },
    {
      dataIndex: 'description',
      key: 'description',
      title: '任务描述',
      scopedSlots: { customRender: 'desc' }
    },
    {
      dataIndex: 'playbook_name',
      key: 'playbook_name',
      title: '所用playbook',
      customRender (text, record, index) {
        if (record.template_name !== undefined) {
          return record.template_name.join(',')
        } else {
          return record.template_name
        }
      }
    },
    {
      key: 'operation',
      title: '操作',
      scopedSlots: { customRender: 'action' }
    }
  ]

  export default {
    name: 'TaskManagement',
    components: {
      PageHeaderWrapper,
      MyPageHeaderWrapper,
      DrawerView,
      AddTask,
      AddTemplate,
      SubjectCard,
      CutText
    },
    data () {
      return {
        rowKey: 'task_id',
        pagination: defaultPagination,
        filters: {},
        sorter: {},
        columns,
        tableData: [],
        selectedRowKeys: [],
        selectedRowsAll: [],
        tableIsLoading: false,
        templateData: [],
        showIndex: 6,
        templateIsLoading: true,
        expandedStatus: [true, true]
      }
    },
    computed: {
      rowSelection () {
        return {
          selectedRowKeys: this.selectedRowKeys,
          onChange: this.onSelectChange
        }
      }
    },
    mounted: function () {
      this.getTaskList()
      this.getTemplateList()
    },
    methods: {
      // 新增playbook模板
      addTemplateSuccess () {
        this.refreshTemplateList()
      },
      // 新增部署任务
      addTaskSuccess () {
        this.handleRefresh()
      },
      handleTableChange (pagination, filters, sorter) {
        // 设置翻页状态
        this.pagination = pagination
        this.filters = filters
        this.sorter = sorter
        // 出发排序、筛选、分页时，重新请求主机列表
        this.getTaskList()
      },
      onSelectChange (selectedRowKeys) {
        this.selectedRowKeys = selectedRowKeys
        this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, this.tableData, 'task_id')
      },
      // 获取列表数据
      getTaskList () {
        const _this = this
        this.tableIsLoading = true
        const pagination = this.pagination || {}
        const filters = this.filters || {}
        const sorter = this.sorter || {}

        getTaskList({
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
        })
          .then(function (res) {
            _this.tableData = res.task_infos || []
            _this.pagination = {
              ..._this.pagination,
              current: pagination.current,
              pageSize: pagination.pageSize,
              total: res.total_count || (res.total_count === 0 ? 0 : pagination.total)
            }
          }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.tableIsLoading = false })
      },
      // 刷新列表数据
      handleRefresh () {
        const _this = this
        this.pagination = defaultPagination
        this.sorter = null
        this.filters = null
        this.selectedRowKeys = []
        this.tableIsLoading = true
        setTimeout(function () {
          _this.getTaskList()
        }, 1500)
      },
      resetSelection () {
        this.selectedRowKeys = []
        this.selectedRowsAll = []
      },
      // 删除配置任务
      deleteTask (record) {
        return this.handleDeleteTask([record.task_id])
      },
      deleteTaskBash (rowKeys, rows) {
        const _this = this
        const list = rows.map((row, idx) => <p class="aops-app-list-in-modal-item">{`${idx + 1}:${row.task_name}`}</p>)
        this.$confirm({
            title: (<div><p>{ `确认批量删除以下${rowKeys.length}个任务：` }</p></div>),
            content: () => (<div class="aops-app-list-in-modal">{list}</div>),
            icon: () => <a-icon type="exclamation-circle" />,
            okType: 'danger',
            okText: '删除',
            onOk: function () { return _this.handleDeleteTask(rowKeys, true) },
            onCancel () {}
        })
      },
      // 删除配置任务
      handleDeleteTask (taskList, isBash) {
        const _this = this
        return new Promise((resolve, reject) => {
          deleteTask({
            taskList
          }).then((res) => {
            _this.$message.success(res.msg)
            _this.handleRefresh()
            if (isBash) _this.selectedRowKeys = []
            resolve()
          })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      },
      // 执行配置任务
      executeTask (record) {
        const hostNameList = record.host_list && record.host_list.map(host => host.host_name)
        const _this = this
        this.$confirm({
            title: (<div><p>{ `确认执行任务：${record.task_name}？` }</p></div>),
            content: (<div><p>{hostNameList ? `该任务可能会修改以下主机配置：${hostNameList.join('、')}` : ''}</p>
                <p>详情请查看任务描述。</p>
              </div>
            ),
            icon: () => <a-icon type="exclamation-circle" />,
            okType: 'danger',
            okText: '执行',
            onOk: function () { return _this.handleExecuteTask([record.task_id]) },
            onCancel () {}
        })
      },
      // 批量执行
      executeTaskBash (rowKeys, rows) {
        const _this = this
        const list = rows.map((row, idx) => <p class="aops-app-list-in-modal-item">{`${idx + 1}:${row.task_name}`}</p>)
        this.$confirm({
            title: (<div><p>{ `确认批量执行以下${rowKeys.length}个任务：` }</p></div>),
            content: () => (<div class="aops-app-list-in-modal">{list}</div>),
            icon: () => <a-icon type="exclamation-circle" />,
            okType: 'danger',
            okText: '执行',
            onOk: function () { return _this.handleExecuteTask(rowKeys, true) },
            onCancel () {}
        })
      },
      // 执行部署任务
      handleExecuteTask (taskList, isBash) {
        const _this = this
        return new Promise((resolve, reject) => {
          executeTask({
            taskList
          }).then((res) => {
            _this.$message.success('excute successed')
            _this.handleRefresh()
            if (isBash) _this.selectedRowKeys = []
            resolve()
          })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      },
      // 获取playbook模板列表
      getTemplateList: function () {
        const _this = this
        this.templateIsLoading = true
        getTemplateList({})
          .then(function (res) {
            _this.templateData = [{}]
            _this.templateData.push(...res.template_infos)
          }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.templateIsLoading = false
        })
      },
      refreshTemplateList () {
        const _this = this
        this.templateIsLoading = true
        setTimeout(function () {
          _this.getTemplateList()
        }, 1500)
      },
      // 删除playbook模板
      deleteTemplate (templateName) {
        const _this = this
        const templateList = []
        templateList.push(templateName)
        deleteTemplate({
          templateList
        }).then(function (res) {
          _this.$message.success(res.msg)
          _this.refreshTemplateList()
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
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
