<template>
  <page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div>
        <div>共获取到{{ tableData.length }}条主机组信息</div>
        <a-row class="aops-app-table-control-row" type="flex" justify="space-between">
          <a-col>
            <a-row type="flex" :gutter="16">
              <a-col>
                <a-alert type="info" show-icon>
                  <div slot="message">
                    <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
                    <a v-if="selectedRowKeys.length > 0" @click="deleteHostBash(selectedRowKeys, selectedRowsAll)">批量删除</a>
                  </div>
                </a-alert>
              </a-col>
              <a-col>
                <a-button @click="handleReset">
                  重置条件
                </a-button>
              </a-col>
            </a-row>
          </a-col>
          <a-col>
            <a-row type="flex" :gutter="16">
              <!---------后续功能----------
              <a-col>
                <a-input placeholder="请搜索主机组名称"/>
              </a-col>
              --------------------------->
              <a-col>
                <add-host-group-modal :onSuccess="handleAddHostGroupSuccess">
                  <a-button type="primary" slot="button">
                    <a-icon type="plus" />添加主机组
                  </a-button>
                </add-host-group-modal>
              </a-col>
              <a-col>
                <a-button @click="handleRefresh">
                  <a-icon type="redo" />刷新
                </a-button>
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
          :expandIconColumnIndex="0"
          @expend="aleret(1)"
        >
          <span slot="action" slot-scope="record">
            <!------后续增加-----
            <span>编辑</span>
            <a-divider type="vertical" />
            ------------------->
            <a @click="deleteHostGroup(record)">删除</a>
            <a-divider type="vertical" />
            <a href="javascript:;" @click="showHostList(record.host_group_name)">组内主机</a>
          </span>
        </a-table>
        <a-drawer
          title="拥有主机"
          :width="720"
          placement="right"
          :visible="hostListVisible"
          :body-style="{ paddingBottom: '80px' }"
          @close="closeHostList"
        >
          <a-table
            :rowKey="hostRowKey"
            :columns="hostListColumns"
            :data-source="this.hostListDataStore[this.hostGroupName] || []"
            :loading="hostListIsLoading ? true : false"
            :pagination="false"
          >
            <span slot="isManagement" slot-scope="isMana">{{ isMana ? '是' : '否' }}</span>
          </a-table>
        </a-drawer>
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import AddHostGroupModal from './components/AddHostGroupModal'
import { getSelectedRow } from './utils/getSelectedRow'

import { hostList, hostGroupList, deleteHostGroup } from '@/api/assest'

const defaultPagination = {
    current: 1,
    pageSize: 5,
    showSizeChanger: true,
    showQuickJumper: true
}

const hostListColumns = [
    {
        dataIndex: 'host_name',
        key: 'host_name',
        title: '主机名称'
    },
    {
        dataIndex: 'public_ip',
        key: 'public_ip',
        title: 'IP地址'
    },
    {
        dataIndex: 'ssh_port',
        key: 'ssh_port',
        title: 'SSH登录接口'
    },
    {
        dataIndex: 'management',
        key: 'management',
        title: '管理节点',
        scopedSlots: { customRender: 'isManagement' }
    }
]

export default {
    name: 'HostGroupManagement',
    components: {
        PageHeaderWrapper,
        AddHostGroupModal
    },
    data () {
        return {
            rowKey: 'host_group_name',
            hostRowKey: 'host_id',
            pagination: defaultPagination,
            // 筛选和排序信息
            filters: null,
            sorter: null,
            hostListColumns,
            tableData: [],
            hostListDataStore: {},
            hostListData: [],
            hostGroupName: undefined,
            selectedRowKeys: [],
            selectedRowsAll: [],
            tableIsLoading: false,
            hostListIsLoading: 0,
            hostListVisible: false
        }
    },
    computed: {
        columns () {
            let { sorter } = this
            sorter = sorter || {}
            return [
                {
                    dataIndex: 'host_group_name',
                    key: 'host_group_name',
                    title: '主机组',
                    sortOrder: sorter.columnKey === 'host_group_name' && sorter.order,
                    sorter: true
                },
                {
                    dataIndex: 'host_count',
                    key: 'host_count',
                    title: '拥有主机数',
                    sortOrder: sorter.columnKey === 'host_count' && sorter.order,
                    sorter: true
                },
                // {
                //     dataIndex: 'hasControl',
                //     key: 'hasControl',
                //     title: '是否包含管理节点'
                // },
                {
                    dataIndex: 'description',
                    key: 'description',
                    title: '信息描述'
                },
                // {
                //     dataIndex: 'status',
                //     key: 'status',
                //     title: '运行状态'
                // },
                {
                    key: 'operation',
                    title: '操作',
                    scopedSlots: { customRender: 'action' }
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
    watch: {
        hostListIsLoading: function () {
            // loaidng改变后，检查hostListDataStore[this.hostGroupId]的值，触发vue更新
            if (this.hostGroupId && this.hostListDataStore[this.hostGroupId]) {
                return true
            }
        }
    },
    methods: {
        handleTableChange (pagination, filters, sorter) {
            // 设置翻页状态
            this.pagination = pagination
            this.filters = filters
            this.sorter = sorter
            // 触发排序、筛选、分页时，重新请求主机列表
            this.getHostGroupList()
        },
        handleExpand (expend, record) {
        },
        onSelectChange (selectedRowKeys) {
            this.selectedRowKeys = selectedRowKeys

            this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, this.tableData)
        },
        // 获取列表数据
        getHostGroupList () {
            const _this = this
            this.tableIsLoading = true
            const pagination = this.pagination || {}
            const filters = this.filters || {}
            const sorter = this.sorter || {}

            hostGroupList({
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
                _this.tableData = res.host_group_infos
                _this.pagination = {
                    ..._this.pagination,
                    current: pagination.current,
                    pageSize: pagination.pageSize,
                    total: res.total_count || (res.total_count === 0 ? 0 : pagination.total)
                }
            }).catch(function (err) {
                _this.$message.error(err.data.msg)
            }).finally(function () { _this.tableIsLoading = false })
        },
        showHostList (hostGroupName) {
            this.hostGroupName = hostGroupName
            this.hostListVisible = true
            this.getHostUnderGroup(hostGroupName)
        },
        closeHostList () {
            this.hostListVisible = false
        },
        // 获取主机组下的主机信息，全量
        getHostUnderGroup (hostGroupName) {
            if (this.hostListDataStore[hostGroupName]) return
            const _this = this
            this.hostListIsLoading += 1
            hostList({
                tableInfo: {
                    pagination: {},
                    filters: {
                        host_group_name: [hostGroupName]
                    },
                    sorter: {}
                }
            }).then(function (res) {
                _this.hostListDataStore[hostGroupName] = res.host_infos
            }).catch(function (err) {
                _this.$message.error(err.response.data.msg)
            }).finally(function () { _this.hostListIsLoading -= 1 })
        },
        deleteHostGroup (record) {
            if (record.host_count > 0) {
                this.$warning({ title: '主机组内有主机时无法删除' })
                return
            }
            const _this = this
            this.$confirm({
                title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机组:</p></div>),
                content: (<span>{ record.host_group_name }</span>),
                icon: () => <a-icon type="exclamation-circle" />,
                okType: 'danger',
                okText: '删除',
                onOk: function () { return _this.handleDelete([record.host_group_name]) },
                onCancel () {}
            })
        },
        deleteHostBash (selectedRowKeys, selectedRowsAll) {
            const filteredRows = selectedRowsAll.filter(row => row.host_count > 0)
            if (filteredRows.length > 0) {
                this.$warning({
                    title: '主机组内有主机时无法删除',
                    content: (
                        <div>
                            <p>请移除下列组内主机后再尝试</p>
                            { filteredRows.map(row => <p><span>{ row.host_group_name }</span></p>) }
                        </div>
                    )
                })
                return
            }

            const _this = this
            this.$confirm({
                title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机组:</p></div>),
                content: () => selectedRowsAll.map(row => (<p><span>{ row.host_group_name }</span></p>)),
                icon: () => <a-icon type="exclamation-circle" />,
                okType: 'danger',
                okText: '删除',
                onOk: function () { return _this.handleDelete(selectedRowKeys, true) },
                onCancel () {}
            })
        },
        handleAddHostGroupSuccess () {
            // 添加完成后，清空table设置，刷新列表
            this.handleReset()
        },
        handleDelete (hostGroupList, isBash) {
            const _this = this
            return new Promise((resolve, reject) => {
                deleteHostGroup({
                    hostGroupList
                })
                .then((res) => {
                    _this.$message.success(res.msg)
                    _this.getHostGroupList({})
                    if (isBash) _this.selectedRowKeys = []
                    resolve()
                })
                .catch((err) => {
                    _this.$message.error(err.response.data.msg)
                    reject(err)
                })
            })
        },
        handleReset () {
            this.pagination = defaultPagination
            this.sorter = null
            this.filters = null
            this.selectedRowKeys = []
            this.getHostGroupList()
        },
        handleRefresh () {
            this.selectedRowKeys = []
            this.getHostGroupList()
        }
    },
    mounted: function () {
        this.getHostGroupList()
    }
}
</script>

<style lang="less" scoped>
.ant-lert {
    line-height: 14px;
}
</style>
