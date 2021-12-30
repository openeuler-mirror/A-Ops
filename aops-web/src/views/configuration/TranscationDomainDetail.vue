
<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div>
        <h2 class="card-title">业务域{{ domainName }}</h2>
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
                <a-button @click="syncConf(selectedRowKeys, selectedRows)" disabled>
                  <a-icon type="sync" />批量同步
                </a-button>
              </a-col>
              <a-col>
                <a-button @click="handleRefresh">
                  <a-icon type="redo" />刷新
                </a-button>
              </a-col>
              <!--------暂时没有其他功能--------
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
              -------------------------------->
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
          <!------------暂不做同步---------------
          <span slot="filterIcon">
            同步状态
            <a-icon type="reload" @click="refreshDomainStatus()"/>
          </span>
          ------------------------------------->
          <template slot="syncStatus" slot-scope="statusInfo">
            <div v-if="domainStatusIsLoading">
              <a-icon type="loading" />
            </div>
            <div v-else>
              <a-icon v-if="statusInfo.syncStatus === statusEnum.sync" type="check-circle" theme="twoTone" two-tone-color="#52c41a"/>
              <a-icon v-if="statusInfo.syncStatus === statusEnum.notSync" type="close-circle" theme="twoTone" two-tone-color="#f00"/>
              <a-icon v-if="statusInfo.syncStatus === statusEnum.notFound" type="question-circle" theme="twoTone" two-tone-color="#ccc"/>
              {{ statusTitleEnum[statusInfo.syncStatus] }}
              <span v-if="statusInfo.syncStatus === statusEnum.notSync" >{{ `${statusInfo.count}条` }}</span>
            </div>
          </template>
          <span slot="action" slot-scope="record">
            <a @click="showQueryRealConfsDrawer(record)">当前配置</a>
            <a-divider type="vertical" />
            <!---- 只是没有这个功能---------
            <a @click="showQueryExpectConfsDrawer(record)">配置日志</a>
            <a-divider type="vertical" />
            ----------------------------->
            <a @click="showDomainStatusDrawer(record)">状态详情</a>
            <a-divider type="vertical" />
            <!-----------暂时不做同步功能----------
            <a-popconfirm
              title="你确定要将当前业务域的配置同步到这台主机吗?"
              ok-text="确认"
              cancel-text="取消"
              @confirm="handleOneHostSyncConf(record)"
            >
              <a href="#">同步</a>
            </a-popconfirm>
            <a-divider type="vertical" />
            ------------------------------------->
            <a-popconfirm
              title="你确定要从当前业务域中删除这台主机吗?"
              ok-text="确认"
              cancel-text="取消"
              @confirm="deleteDomainHost(record)"
            >
              <a>删除</a>
            </a-popconfirm>
          </span>
        </a-table>
      </div>
    </a-card>
    <!--添加主机抽屉-->
    <drawer-view title="添加主机" ref="addHostDrawer" :bodyStyle="{ paddingBottom: '80px' }">
      <template slot="drawerView">
        <add-host-drawer @addHostSuccess="addHostSuccess"></add-host-drawer>
      </template>
    </drawer-view>
    <!--主机当前配置抽屉-->
    <drawer-view ref="queryRealConfsDrawer" :bodyStyle="{ paddingBottom: '80px' }">
      <template slot="drawerView">
        <query-real-confs-drawer
          :confsOfDomain="confsOfDomain"
          :confsOfDomainLoading="confsOfDomainLoading"
        />
      </template>
    </drawer-view>
    <!--状态详情抽屉-->
    <drawer-view title="状态详情" ref="domainStatusDrawer" :hasButtonOnBottom="false" :bodyStyle="{ paddingBottom: '80px' }">
      <template slot="drawerView">
        <get-domain-status-drawer
          :tableData="tableData"
          :domainStatusIsLoading="domainStatusIsLoading"
        />
      </template>
    </drawer-view>
  </my-page-header-wrapper>
</template>

<script>
  import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'

  import { domainHostList, deleteHost, domainStatus, syncConf } from '@/api/configuration'
  import { getManagementConf } from '@/api/management'

  import DrawerView from '@/views/utils/DrawerView'
  import QueryRealConfsDrawer from '@/views/configuration/components/QueryRealConfsDrawer'
  import QueryExpectConfsDrawer from '@/views/configuration/components/QueryExpectConfsDrawer'
  import GetDomainStatusDrawer from '@/views/configuration/components/GetDomainStatusDrawer'
  import AddHostDrawer from '@/views/configuration/components/AddHostDrawer'

  import defaultSettings from '@/config/defaultSettings'
  import { STATUS_ENUM, getStatusInfoFromAllConfs } from './utils/statusCheckTools'

  const STATUS_TITLE_ENUM = {}
  STATUS_TITLE_ENUM[STATUS_ENUM.sync] = '已同步'
  STATUS_TITLE_ENUM[STATUS_ENUM.notSync] = '未同步'
  STATUS_TITLE_ENUM[STATUS_ENUM.notFound] = '未知状态'

  export default {
    name: 'TranscationDomainDetail',
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
        hostList: [],
        statusData: [],
        selectedRowKeys: [],
        selectedRows: [],
        tableIsLoading: false,
        domainName: this.$route.params.domainName,
        statusEnum: STATUS_ENUM,
        statusTitleEnum: STATUS_TITLE_ENUM,
        domainStatusIsLoading: false,
        hostStatusData: { a: 1 },
        confsOfDomain: [],
        confsOfDomainLoading: false,
        setTimeoutKey_statusInterval: undefined
      }
    },
    computed: {
      columns () {
        return [
          {
            dataIndex: 'ip',
            key: 'ip',
            title: 'IP地址'
          },
          {
            dataIndex: 'ipv6',
            key: 'ipv6',
            title: 'IP协议'
          },
          {
            dataIndex: 'syncStatusInfo',
            key: 'syncStatusInfo',
            title: '同步状态',
            filterMultiple: false,
            slots: {
              // title: 'filterIcon' 暂不做同步
            },
            scopedSlots: { customRender: 'syncStatus' }
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
      },
      tableData () {
        return this.hostList.map(host => {
          const hostTemp = host
          const matchedStatusHost = this.statusData.filter(item => item.hostId === hostTemp.hostId)[0] || {}
          hostTemp.syncStatusList = matchedStatusHost.syncStatus || []
          hostTemp.syncStatusInfo = getStatusInfoFromAllConfs(hostTemp.syncStatusList)
          return hostTemp
        })
      }
    },
    methods: {
      onSelectChange (selectedRowKeys, selectedRows) {
        this.selectedRowKeys = selectedRowKeys
        this.selectedRows = selectedRows
      },
      // 获取业务域列表数据
      getHostList (domainName) {
        const _this = this
        return new Promise(function (resolve, reject) {
          _this.tableIsLoading = true
          domainHostList(domainName)
            .then(function (res) {
              _this.hostList = res
              resolve(res)
            }).catch(function (err) {
              if (err.response.data.code !== 400) {
                _this.$message.error(err.response.data.msg || err.response.data.detail)
              } else {
                _this.hostList = []
              }
              reject(err)
            }).finally(function () { _this.tableIsLoading = false })
        })
      },
      // 获取业务域主机同步状态
      getDomainStatus () {
        const _this = this
        this.domainStatusIsLoading = true
        domainStatus({
          domainName: _this.domainName
        }).then(function (res) {
          _this.statusData = res.hostStatus || []
        }).catch(function (err) {
          if (err.response.data.code !== 404) {
            _this.$message.error(err.response.data.msg || err.response.data.detail)
          }
        }).finally(function () { _this.domainStatusIsLoading = false })
      },
      handleRefresh () {
        this.selectedRowKeys = []
        this.getHostAndStatus()
      },
      deleteDomainHost (record) {
        this.handleDelete([record])
      },
      deleteHostBash (selectedRowKeys, selectedRows) {
        const _this = this
        this.$confirm({
          title: (<div><p>删除后无法恢复</p><p>请确认删除以下主机:</p></div>),
        content: () => selectedRows.map(row => (<p><span>{ row.ip }</span></p>)),
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
              _this.$message.success(res.msg)
              _this.getHostAndStatus()
              if (isBash) {
                _this.selectedRowKeys = []
                _this.selectedRows = []
              }
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.nsg)
              reject(err)
            })
        })
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
            _this.$message.success(res.msg)
            _this.getHostAndStatus()
            if (isBash) {
              _this.selectedRowKeys = []
              _this.selectedRows = []
            }
            resolve()
          })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      },
      showAddHostDrawer () {
        this.$refs.addHostDrawer.open(this.domainName)
      },
      showQueryRealConfsDrawer (host) {
        this.$refs.queryRealConfsDrawer.open({
          host,
          domainName: this.domainName
        })
      },
      showQueryExpectConfsDrawer (record) {
        this.$refs.queryExpectConfsDrawer.open(record)
      },
      showDomainStatusDrawer (record) {
        this.$refs.domainStatusDrawer.open(record)
      },
      getConfsOfDomain (domainName) {
        const _this = this
        _this.confsOfDomainLoading = true
        getManagementConf({
          domainName
        }).then(function (res) {
          _this.confsOfDomain = res.confFiles || []
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.confsOfDomainLoading = false
        })
      },
      addHostSuccess () {
        this.handleRefresh()
      },
      getHostAndStatus () {
        const _this = this
        this.getHostList(this.domainName).then(function () {
          _this.getDomainStatus()
          // 启动循环更新Status
          clearInterval(_this.setTimeoutKey_statusInterval)
          _this.setTimeoutKey_statusInterval = setInterval(function () {
            _this.getDomainStatus()
          }, defaultSettings.domainStatusRefreshInterval)
        }).catch(function (err) {
          console.warn(err)
          // 获取host出错（为空或报错，则清除轮训）
          clearInterval(_this.setTimeoutKey_statusInterval)
        })
      }
    },
    mounted: function () {
      this.getHostAndStatus()
      this.getConfsOfDomain(this.domainName)
    },
    destroyed: function () {
      clearInterval(this.setTimeoutKey_statusInterval)
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
