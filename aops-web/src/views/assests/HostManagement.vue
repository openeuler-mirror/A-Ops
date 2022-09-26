<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div>
        <div>共获取到{{ tableData.length }}条主机信息</div>
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
                <a-button @click="handleReset">重置条件</a-button>
              </a-col>
            </a-row>
          </a-col>
          <a-col>
            <a-row type="flex" :gutter="16">
              <!-----后续功能--------
              <a-col>
                <a-input placeholder="请搜索主机名称" @pressEnter="handleInput"/>
              </a-col>
              ---------------------->
              <a-col>
                <router-link :to="{ path: `hosts-management/host-create` }">
                  <a-button type="primary" disabled>
                    <a-icon type="plus" />添加主机
                  </a-button>
                </router-link>
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
        >
            <router-link :to="{ path: `/assests/host/detail/${record.host_id}` }" slot="hostName" slot-scope="hostName, record">{{ hostName }}</router-link>
            <span slot="isManagement" slot-scope="isMana">{{ isMana ? '是' : '否' }}</span>
            <span slot="statusItem" slot-scope="status">{{ status || '暂无' }}</span>
            <span slot="action" slot-scope="record">
                <!-- <a @click="openDetail(record.host_id)">查看</a>
                ----后续增加-----
                <a-divider type="vertical" />
                <span>编辑</span>
                ----------------
                <a-divider type="vertical" /> -->
                <a @click="deleteHost(record)">删除</a>
            </span>
        </a-table>
      </div>
    </a-card>
    <host-detail-drawer
      :visible="detailVisisble"
      @close="closeDetail"
      :hostId="detailId"
    />
  </my-page-header-wrapper>
</template>

<script>
import store from '@/store'
import router from '@/vendor/ant-design-pro/router'

import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import { getSelectedRow } from '@/views/utils/getSelectedRow'
import HostDetailDrawer from './components/HostDetailDrawer'

import { hostList, deleteHost, hostGroupList } from '@/api/assest'

const defaultPagination = {
    current: 1,
    pageSize: 10,
    total: 10,
    showSizeChanger: true,
    showQuickJumper: true
}

export default {
    name: 'HostManagement',
    components: {
        MyPageHeaderWrapper,
        HostDetailDrawer
    },
    data () {
        return {
            rowKey: 'host_id',
            pagination: defaultPagination,
            filters: null,
            sorter: null,
            tableData: [],
            groupData: [],
            selectedRowKeys: [],
            selectedRowsAll: [],
            tableIsLoading: false,
            detailId: undefined,
            detailVisisble: false,
            deleteHostTempInfo: {}
        }
    },
    computed: {
        columns () {
            let { sorter, filters } = this
            sorter = sorter || {}
            filters = filters || {}
            return [
                {
                    dataIndex: 'host_name',
                    key: 'host_name',
                    title: '主机名称',
                    scopedSlots: { customRender: 'hostName' },
                    sorter: true,
                    sortOrder: sorter.columnKey === 'host_name' && sorter.order
                },
                {
                    dataIndex: 'public_ip',
                    key: 'public_ip',
                    title: 'IP地址'
                },
                {
                    dataIndex: 'host_group_name',
                    key: 'host_group_name',
                    title: '所属主机组',
                    filteredValue: filters.host_group_name || null,
                    filters: this.groupData.map(group => {
                        return {
                            text: group.host_group_name,
                            value: group.host_group_name
                        }
                    })
                },
                {
                    dataIndex: 'management',
                    key: 'management',
                    title: '管理节点',
                    filteredValue: filters.management || null,
                    filters: [{
                        text: '是',
                        value: 'true'
                    }, {
                        text: '否',
                        value: 'false'
                    }],
                    filterMultiple: false,
                    scopedSlots: { customRender: 'isManagement' }
                },
                {
                    dataIndex: 'status',
                    key: 'status',
                    title: '运行状态',
                    scopedSlots: { customRender: 'statusItem' }
                },
                {
                    dataIndex: 'scene',
                    key: 'scene',
                    title: '场景',
                    customRender: scene => scene || '暂无'
                },
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
    methods: {
        handleTableChange (pagination, filters, sorter) {
            // 存储翻页状态
            this.pagination = pagination
            this.filters = filters
            this.sorter = sorter
            // 出发排序、筛选、分页时，重新请求主机列表
            this.getHostList()
        },
        onSelectChange (selectedRowKeys, selectedRows) {
            this.selectedRowKeys = selectedRowKeys
            this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, this.tableData, 'host_id')
        },
        // 获取列表数据
        getHostList () {
            const _this = this
            this.tableIsLoading = true
            const pagination = this.pagination || {}
            const filters = this.filters || {}
            const sorter = this.sorter || {}

            hostList({
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
                _this.tableData = res.host_infos || []
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
        deleteHost (record) {
            const _this = this
            // 保存单独删除时的主机信息，错误提示时需要展示主机名
            this.deleteHostTempInfo = {
                host_id: record.host_id,
                host_name: record.host_name
            }

            this.$confirm({
                title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机:</p></div>),
                content: (<span>{ record.host_name }</span>),
                icon: () => <a-icon type="exclamation-circle" />,
                okType: 'danger',
                okText: '删除',
                onOk: function () { return _this.handleDelete([record.host_id]) },
                onCancel () {}
            })
        },
        deleteHostBash (selectedRowKeys, selectedRowsAll) {
            const _this = this
            this.$confirm({
                title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机:</p></div>),
                content: () => selectedRowsAll.map(row => (<p><span>{ row.host_name }</span></p>)),
                icon: () => <a-icon type="exclamation-circle" />,
                okType: 'danger',
                okText: '删除',
                onOk: function () { return _this.handleDelete(selectedRowKeys, true) },
                onCancel () {}
            })
        },
        handleDelete (hostList, isBash) {
            const _this = this
            return new Promise((resolve, reject) => {
                deleteHost({
                    hostList
                })
                .then((res) => {
                    if (res.fail_list && Object.keys(res.fail_list).length > 0) {
                        _this.deleteErrorHandler(res);
                    } else {
                        this.$message.success('删除成功')
                    }
                    _this.getHostList()
                    if (isBash) {
                        _this.selectedRowKeys = []
                        _this.selectedRowsAll = []
                    }
                    resolve()
                })
                .catch((err) => {
                    if (err.data.code === 1103) {
                        _this.deleteErrorHandler(err.data, true);
                    } else {
                        _this.$message.error(err.response.data.msg)
                    }
                    // 业务逻辑，报错时依然关闭弹窗。因此触发resolve()
                    resolve()
                })
            })
        },
        deleteErrorHandler (data, allFailed = false) {
            const deleteErrorList = Object.keys(data.fail_list || {})
                .map(hostId => {
                    let matchedHost = this.selectedRowsAll.filter(item => item.host_id === hostId)[0];
                    // 正常情况下，未匹配到说明selectedRowsAll和返回的错误主机id不匹配。则说明用户是直接点击表格的删除按钮提交的
                    if (!matchedHost) {
                        matchedHost = this.deleteHostTempInfo
                    }
                    return {
                        hostId,
                        hostName: matchedHost && matchedHost.host_name,
                        errorInfo: data.fail_list && data.fail_list[hostId]
                    }
                });
            this.$notification['error']({
                message: `${ allFailed ? '删除失败' : '部分主机删除失败'}`,
                description: (<div>
                    <p>{`${ allFailed ? '全部' : ''}${deleteErrorList.length}个主机删除失败：`}</p>
                    {
                        deleteErrorList.slice(0, 3).map((errorInfo, idx) => {
                            return (<p>{`${idx + 1}、`}
                                <span>{`${errorInfo.hostName}: `}</span>
                                <span>{ errorInfo.errorInfo }</span>
                            </p>)
                        })
                    }
                    {
                        deleteErrorList.length > 3 &&
                            <p>更多错误信息请查看返回信息...</p>
                    }
                </div>),
                duration: 5
            });
        },
        handleReset () {
            this.pagination = defaultPagination
            this.sorter = null
            this.filters = null
            this.selectedRowKeys = []
            this.getHostList()
            this.getGroupList()
        },
        handleRefresh () {
            this.selectedRowKeys = []
            this.getHostList()
            this.getGroupList()
        },
        closeDetail () {
            this.detailVisisble = false
        },
        openEdit (hostInfo) {
            store.dispatch('setHostInfo', hostInfo)
            router.push('hosts-management/host-edit')
        },
        getGroupList () {
            const _this = this
            hostGroupList({
                tableInfo: {
                    pagination: {},
                    filters: {},
                    sorter: {}
                }
            }).then(function (res) {
                _this.groupData = res.host_group_infos
            }).catch(function (err) {
                _this.$message.error(err.response.data.msg)
            }).finally(function () {})
        }
    },
    mounted: function () {
        this.getHostList()
        this.getGroupList()
    }
}
</script>

<style lang="less" scoped>
.ant-lert {
    line-height: 14px;
}

</style>
