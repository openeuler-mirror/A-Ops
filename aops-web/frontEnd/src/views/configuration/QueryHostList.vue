
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false">
      <div>
        <h3 class="card-title">{{domainName}}主机列表</h3>
      </div>
      <div>
        <div>共获取到{{ tableData.length }}条主机信息</div>
        <a-row class="aops-table-control-row" type="flex" justify="space-between">
          <a-col>
            <a-alert type="info" show-icon>
              <div slot="message">
                <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
                <a v-if="selectedRowKeys.length > 0" @click="deleteHostBash(selectedRowKeys, selectedRows)">批量删除</a>
              </div>
            </a-alert>
          </a-col>
          <a-col>
            <a-row type="flex" :gutter="16">
              <a-col>
                <a-button type="primary" @click="showAddHostDrawer">
                  <a-icon type="plus" />添加主机
                </a-button>
              </a-col>
              <a-col>
                <a-button @click="syncConf(selectedRowKeys, selectedRows)">
                  <a-icon type="sync" />批量同步
                </a-button>
              </a-col>
              <a-col>
                <a-button @click="handleRefresh">
                  <a-icon type="redo" />刷新
                </a-button>
              </a-col>
              <a-col>
                <a-button>
                  <a-dropdown>
                    <a class="ant-dropdown-link" @click="e => e.preventDefault()">
                      更多操作 <a-icon type="down" />
                    </a>
                    <a-menu slot="overlay">
                      <a-menu-item>
                        <a>查看主机</a>
                      </a-menu-item>
                      <a-menu-item>
                        <a>添加主机</a>
                      </a-menu-item>
                    </a-menu>
                  </a-dropdown>
                </a-button>
              </a-col>
            </a-row>
          </a-col>
        </a-row>
        <a-table
          :rowKey="rowKey"
          :columns="columns"
          :data-source="tableData"
          :row-selection="rowSelection"
          :loading="tableIsLoading"
          :pagination="false"
        >
          <span slot="filterIcon">
            同步状态
            <a-icon type="reload" @click="refreshDomainStatus()"/>
          </span>
          <template slot="state" slot-scope="record">
            <span v-if="'已同步'!=record.isSynced" style="color:#ff0000 ">
              <a-icon type="close-circle"  theme="twoTone" two-tone-color="#ff0000"/>
              {{record.isSynced}}
            </span>
            <span v-if="'已同步'==record.isSynced">
              <a-icon type="check-circle"  theme="twoTone" two-tone-color="#52c41a"/>
              {{record.isSynced}}
            </span>
          </template>
          <span slot="action" slot-scope="record">
            <a @click="showQueryRealConfsDrawer(record)">当前配置</a>
            <a-divider type="vertical" />
            <a @click="showQueryExpectConfsDrawer(record)">配置日志</a>
            <a-divider type="vertical" />
            <a @click="showDomainStatusDrawer(record)">状态详情</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="你确定要将当前业务域的配置同步到这台主机吗?"
              ok-text="确认"
              cancel-text="取消"
              @confirm="handleOneHostSyncConf(record)"
            >
              <a href="#">同步</a>
            </a-popconfirm>
            <a-divider type="vertical" />
            <a-popconfirm
              title="你确定要从当前业务域中删除这台主机吗?"
              ok-text="确认"
              cancel-text="取消"
              @confirm="deleteDomainHost(record)"
            >
              <a>删除</a>
            </a-popconfirm>
            <a-divider type="vertical" />
            <a-dropdown>
              <a class="ant-dropdown-link" @click="e => e.preventDefault()">
                更多 <a-icon type="down" />
              </a>
              <a-menu slot="overlay">
                <a-menu-item>
                  <a @click="showAddHostDrawer(domain.id)">添加主机</a>
                </a-menu-item>
                <a-menu-item>
                  <a @click="showAddHostDrawer(domain.id)">删除主机</a>
                </a-menu-item>
              </a-menu>
            </a-dropdown>
          </span>
        </a-table>
      </div>
    </a-card>
    <!--添加主机抽屉-->
    <drawer-view title="添加主机" ref="addHostDrawer">
      <template slot="drawerView">
        <add-host-drawer></add-host-drawer>
      </template>
    </drawer-view>
    <!--主机当前配置抽屉-->
    <drawer-view title="主机当前配置" ref="queryRealConfsDrawer">
      <template slot="drawerView">
        <query-real-confs-drawer></query-real-confs-drawer>
      </template>
    </drawer-view>
    <!--配置日志抽屉-->
    <drawer-view title="配置日志" ref="queryExpectConfsDrawer">
      <template slot="drawerView">
        <query-expect-confs-drawer></query-expect-confs-drawer>
      </template>
    </drawer-view>
    <!--状态详情抽屉-->
    <drawer-view title="状态详情" ref="domainStatusDrawer">
      <template slot="drawerView">
        <get-domain-status-drawer ></get-domain-status-drawer>
      </template>
    </drawer-view>
  </my-page-header-wrapper>
</template>

<script>
  import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'

  import { domainHostList, deleteHost, domainStatus, syncConf } from '@/api/configuration'
  import DrawerView from '@/views/utils/DrawerView'
  import QueryRealConfsDrawer from '@/views/configuration/components/QueryRealConfsDrawer'
  import QueryExpectConfsDrawer from '@/views/configuration/components/QueryExpectConfsDrawer'
  import GetDomainStatusDrawer from '@/views/configuration/components/GetDomainStatusDrawer'
  import AddHostDrawer from '@/views/configuration/components/AddHostDrawer'

  export default {
    name: 'QueryHostList',
    components: {
      MyPageHeaderWrapper,
      DrawerView,
      QueryRealConfsDrawer,
      QueryExpectConfsDrawer,
      GetDomainStatusDrawer,
      AddHostDrawer
    },
    data () {
      return {
        rowKey: 'hostId',
        tableData: [],
        statusData: [],
        selectedRowKeys: [],
        selectedRows: [],
        tableIsLoading: false,
        domainName: this.$route.params.domainName
      }
    },
    computed: {
      columns () {
        return [
          {
            dataIndex: 'hostId',
            key: 'hostId',
            title: '主机名称'
          },
          {
            dataIndex: 'ip',
            key: 'ip',
            title: '公网IP地址'
          },
          {
            dataIndex: 'ipv6',
            key: 'ipv6',
            title: 'IP协议'
          },
          {
            dataIndex: '',
            key: 'isSynced',
            // title: '同步状态',
            filterMultiple: false,
            slots: {
              title: 'filterIcon'
            },
            scopedSlots: { customRender: 'state' }
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
      onSelectChange (selectedRowKeys, selectedRows) {
        this.selectedRowKeys = selectedRowKeys
        this.selectedRows = selectedRows
      },
      // 获取业务域列表数据
      getHostList () {
        const _this = this
        this.tableIsLoading = true
        domainHostList({
          domainName: _this.domainName
        }).then(function (res) {
          _this.tableData = res.result.domainHostData
          _this.setStatus()
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      // 获取业务域主机同步状态
      getDomainStatus () {
        const _this = this
        this.tableIsLoading = true
        domainStatus({
          domainName: _this.domainName
        }).then(function (res) {
            _this.statusData = res.result.doMainStatusData
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      setStatus () {
        const _this = this
        _this.tableData.forEach(function (item) {
          let synced = '已同步'
          _this.statusData.hostStatus.forEach(function (childItem) {
            let i = 0
            if (item.hostId === childItem.hostId) {
              childItem.syncStatus.forEach(function (status) {
                i++
                if (status.isSynced === 'NOT FOUND') {
                  synced = '未同步' + i + '条'
                }
              })
            }
          })
          item.isSynced = synced
        })
      },
      handleRefresh () {
        this.selectedRowKeys = []
        this.getHostList('')
      },
      deleteDomainHost (record) {
        this.handleDelete(record)
      },
      deleteHostBash (selectedRowKeys, selectedRows) {
        const _this = this
        this.$confirm({
          title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机:</p></div>),
        content: () => selectedRows.map(row => (<p><span>{ row.hostId }</span></p>)),
        icon: () => <a-icon type="exclamation-circle" />,
          okType: 'danger',
          okText: '删除',
          onOk: function () { return _this.handleDelete(selectedRows, true) },
          onCancel () {}
        })
      },
      handleDelete (hostInfos, isBash) {
        const _this = this
        return new Promise((resolve, reject) => {
          deleteHost({
            domainName: _this.domainName,
            hostInfos: hostInfos
          }).then((res) => {
              _this.$message.success('删除成功')
              _this.getDomainStatus()
              _this.getHostList()
              if (isBash) {
                _this.selectedRowKeys = []
                _this.selectedRows = []
              }
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.message)
              reject(err)
            })
        })
      },
      refreshDomainStatus () {
        const _this = this
        _this.getDomainStatus('')
        _this.setStatus()
      },
      syncConf (selectedRowKeys, selectedRows) {
        const _this = this
        this.$confirm({
          title: (<div><p>你确定要将当前业务域的配置同步到已选主机吗？</p></div>),
          content: (<span>同步后将配置无法恢复，但可从配置日志中查看记录,你还要继续吗?</span>),
          icon: () => <a-icon type="exclamation-circle" />,
            okType: 'danger',
            okText: '继续同步',
            onOk: function () { return _this.handleSyncConf(selectedRows, true) },
          onCancel () {}
        })
      },
      handleOneHostSyncConf (record) {
        const rows = []
        rows.push(record)
        this.handleSyncConf(rows, true)
      },
      handleSyncConf (selectedRows, isBash) {
        console.log(selectedRows)
        const hostIds = []
        selectedRows.forEach(function (item) {
          hostIds.push({ hostId: item.hostId })
        })
        const _this = this
        return new Promise((resolve, reject) => {
          syncConf({
            domainName: _this.domainName,
            hostIds: hostIds
          }).then((res) => {
            _this.$message.success('同步成功')
            _this.getDomainStatus()
            _this.getHostList()
            if (isBash) {
              _this.selectedRowKeys = []
              _this.selectedRows = []
            }
            resolve()
          })
            .catch((err) => {
              _this.$message.error(err.response.data.message)
              reject(err)
            })
        })
      },
      showAddHostDrawer () {
        this.$refs.addHostDrawer.open(this.domainName)
      },
      showQueryRealConfsDrawer (record) {
        this.$refs.queryRealConfsDrawer.open(record)
      },
      showQueryExpectConfsDrawer (record) {
        this.$refs.queryExpectConfsDrawer.open(record)
      },
      showDomainStatusDrawer (record) {
        this.$refs.domainStatusDrawer.open(record)
      }
    },
    mounted: function () {
      this.getDomainStatus()
      this.getHostList(this.domainName)
      const _this = this
      setInterval(function () {
        _this.refreshDomainStatus()
      }, 60000)
    }
  }
</script>

<style lang="less" scoped>
  .card-title {
    display: inline-block;
    margin-right: 10px;
    font-weight: 600;
  }

</style>
