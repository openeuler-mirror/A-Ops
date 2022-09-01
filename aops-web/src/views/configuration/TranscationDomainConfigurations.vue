
<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <div>
        <div>
          <h2 class="card-title">{{ oldDomainName }}<span>配置表</span></h2>
          <span>共获取到{{ tableData.length }}条配置信息</span>
        </div>
        <a-row class="aops-table-control-row" type="flex" justify="space-between">
          <a-col>
            <a-alert type="info" show-icon>
              <div slot="message">
                <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
                <a v-if="selectedRowKeys.length > 0" @click="deleteConfigBash(selectedRowKeys, selectedRows)">批量删除</a>
              </div>
            </a-alert>
          </a-col>
          <a-col>
            <a-row type="flex" :gutter="16">
              <a-col>
                <add-configuration-drawer :domainName="domainName" @ok="onAddConfsOk">
                  <a-button type="primary" slot="button">
                    <a-icon type="plus" />新增配置
                  </a-button>
                </add-configuration-drawer>
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
          rowKey="filePath"
          :columns="columns"
          :data-source="tableData"
          :pagination="pagination"
          :row-selection="rowSelection"
          @change="handleTableChange"
          :loading="tableIsLoading"
        >
          <span slot="contents" slot-scope="record">
            <div class="oneRow">{{ record.contents }}</div>
          </span>
          <span slot="action" slot-scope="record">
            <a @click="showConfigContent(record)">查看配置文件</a>
            <a-divider type="vertical" />
            <a @click="showConfigChange(record)">配置变更日志</a>
            <a-divider type="vertical" />
            <a @click="showEditDrawer(record)">编辑配置&emsp;&emsp;</a>
            <a-divider type="vertical" />
            <a-popconfirm
              title="你确定删除这行配置吗?"
              ok-text="确认"
              cancel-text="取消"
              @confirm="deleteConfig(record)"
            >
              <a-icon slot="icon" type="close-circle" style="color: red" />
              <a>删除</a>
            </a-popconfirm>
          </span>
        </a-table>
        <a-drawer
          title="配置文件内容"
          :width="720"
          placement="right"
          :visible="configContentVisible"
          :body-style="{ paddingBottom: '80px' }"
          @close="closeConfigContent"
        >
          <a-descriptions :column="1" layout="horizontal">
            <a-descriptions-item label="配置文件">
              {{ configContent.filePath }}
            </a-descriptions-item>
            <a-descriptions-item>
              <div class="contentBox1">
                <span class="diffContent">
                  {{ configContent.contents }}
                </span>
              </div>
            </a-descriptions-item>
          </a-descriptions>
        </a-drawer>
        <a-drawer
          title="配置日志"
          :width="1080"
          placement="right"
          :visible="configChangeVisible"
          :body-style="{ paddingBottom: '80px' }"
          @close="closeConfigChange"
        >
          <a-spin :spinning="logIsLoading">
            <a-descriptions :column="1" layout="horizontal">
              <a-descriptions-item label="所属业务域">
                {{ domainName }}
              </a-descriptions-item>
            </a-descriptions>
            <a-descriptions :column="1" layout="vertical" bordered>
              <a-descriptions-item :label="'配置文件：'+manageConfChange[0].filePath">
                <p class="pContent">期望配置文本：</p>
                <div class="contentBox2">
                  <span class="diffContent">
                    {{ manageConfChange[0].expectedContents }}
                  </span>
                </div>
                <p class="pLog">变更历史：</p>
                <a-table
                  rowKey="changeId"
                  :columns="confChangeColumns"
                  :data-source="manageConfChange[0].changeLog"
                  :expandIconAsCell="false"
                  :expandIconColumnIndex="4"
                  :expandIcon="(props)=>this.customExpandIcon(props)"
                  :pagination="false"
                  bordered
                >
                  <div slot="expandedRowRender" slot-scope="record" style="margin: 0">
                    <p>preValue:</p>
                    {{ record.preValue }}
                    <p>postValue:</p>
                    {{ record.postValue }}
                  </div>
                </a-table>
              </a-descriptions-item>
            </a-descriptions>
          </a-spin>
        </a-drawer>
      </div>
    </a-card>
    <domain-selection-modal
      :showDomainSelection="choiceDomainNameModalVisible"
      @cancel="handleDomainSelectCancel"
    />
    <add-configuration-drawer
      :isEdit="true"
      :visibleControl="editConfVisible"
      :domainName="domainName"
      :editFilePath="editFilePath"
      @ok="onEditConfsOk"
      @cancel="onEditConfsCancel"
    />
  </page-header-wrapper>
</template>

<script>
  import router from '@/vendor/ant-design-pro/router'
  import { i18nRender } from '@/vendor/ant-design-pro/locales'
  import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
  import DomainSelectionModal from './components/DomainSelectionModal'
  import AddConfigurationDrawer from './components/AddConfigurationDrawer'

  import { getManagementConf, queryManageConfChange, deleteManagementConf } from '@/api/management'
  import { dateFormat } from '@/views/utils/Utils'

  const defaultPagination = {
    current: 1,
    pageSize: 10,
    showSizeChanger: true,
    showQuickJumper: true
  }

  export default {
    name: 'TranscationDomainConfigurations',
    components: {
      PageHeaderWrapper,
      DomainSelectionModal,
      AddConfigurationDrawer
    },
    data () {
      return {
        pagination: defaultPagination,
        filters: null,
        sorter: null,
        tableData: [],
        selectedRowKeys: [],
        selectedRows: [],
        tableIsLoading: false,
        logIsLoading: false,
        hostListIsLoading: false,
        addIsLoading: false,
        configContent: {},
        configContentVisible: false,
        configChangeVisible: false,
        manageConfChange: [{}],
        form: this.$form.createForm(this),
        hostList: [],
        configList: [{
          filePath: '',
          configSource: '',
          contents: '',
          hostId: ''
        }],
        choiceDomainNameModalVisible: false,
        domainNameList: [],
        selectDomainName: this.$route.params.domainName || null,
        editConfVisible: false,
        editFilePath: '',
        oldDomainName: null
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
              if (routes.indexOf(route) === routes.length - 1) {
                return <span>{route.breadcrumbName}</span>
              } else {
                return <router-link to={route.path}>{route.breadcrumbName}</router-link>
              }
            }
          }
        }
      },
      domainName () {
        return this.$route.params.domainName
      },
      columns () {
        return [
          {
            dataIndex: 'filePath',
            key: 'filePath',
            title: '配置文件'
          },
          {
            key: 'contents',
            title: '配置详情',
            scopedSlots: { customRender: 'contents' }
          },
          {
            key: 'operation',
            title: '操作',
            scopedSlots: { customRender: 'action' },
            width: 240
          }
        ]
      },
      confChangeColumns () {
        return [
          { title: '变更ID', dataIndex: 'changeId', key: 'changeId' },
          { title: '变更时间', dataIndex: 'date', key: 'date', customRender: (text, record, index) => dateFormat('YYYY-mm-dd HH:MM:SS', text) },
          { title: '变更人', dataIndex: 'author', key: 'author' },
          { title: '变更原因', dataIndex: 'changeReason', key: 'changeReason' },
          { title: '变更详情', dataIndex: '', key: 'x', align: 'center' }
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
      '$route': {
        handler: 'routerChangeInital',
        immediate: true
      }
    },
    methods: {
      handleTableChange (pagination, filters, sorter) {
        // 存储翻页状态
        this.pagination = pagination
        this.filters = filters
        this.sorter = sorter
        // 出发排序、筛选、分页时，重新请求主机列表
        this.getTranscationDomainConfig()
      },
      onSelectChange (selectedRowKeys, selectedRows) {
        this.selectedRowKeys = selectedRowKeys
        this.selectedRows = selectedRows
      },
      onAddConfsOk () {
        this.getTranscationDomainConfig()
      },
      onEditConfsOk () {
        this.editConfVisible = false
        this.getTranscationDomainConfig()
      },
      onEditConfsCancel () {
        this.editConfVisible = false
      },
      showEditDrawer (record) {
        this.editFilePath = record.filePath.replace(/openEuler:/, '')
        this.editConfVisible = true
      },
      // 获取列表数据
      getTranscationDomainConfig () {
        const _this = this
        this.tableIsLoading = true
        getManagementConf({
          domainName: _this.domainName
        }).then(function (data) {
          _this.tableData = data.confFiles
        }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      deleteConfig (record) {
        return this.handleDelete([record.filePath])
      },
      deleteConfigBash (selectedRowKeys, selectedRows) {
        const _this = this
        this.$confirm({
            title: (<div><p>删除后无法恢复</p><p>请确认删除以下配置项:</p></div>),
          content: () => selectedRows.map(row => (<p><span>{ row.name }</span></p>)),
          icon: () => <a-icon type="exclamation-circle" />,
            okType: 'danger',
            okText: '删除',
            onOk: function () { return _this.handleDelete(selectedRowKeys, true) },
          onCancel () {}
        })
      },
      handleDelete (managementConfList, isBash) {
        const _this = this
        return new Promise((resolve, reject) => {
          deleteManagementConf({
            domainName: _this.domainName,
            confFiles: managementConfList.map(filePath => {
              return { filePath: filePath.replace(/openEuler:/, '') }
            })
          })
            .then((res) => {
              _this.$message.success(res.msg)
              _this.getTranscationDomainConfig()
              if (isBash) _this.selectedRowKeys = []
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      },
      handleRefresh () {
        this.pagination = defaultPagination
        this.sorter = null
        this.filters = null
        this.selectedRowKeys = []
        this.getTranscationDomainConfig()
      },
      /* 配置文件内容 */
      showConfigContent (record) {
        this.configContentVisible = true
        this.configContent = record
      },
      closeConfigContent () {
        this.configContentVisible = false
        this.configContent = {}
      },
      /* 配置日志 */
      showConfigChange (record) {
        this.getConfigChange(record)
        this.configChangeVisible = true
      },
      closeConfigChange () {
        this.configChangeVisible = false
        this.configContent = {}
      },
      customExpandIcon (props) {
        if (props.expanded) {
          return <a style={{ color: 'balck', marginRight: 8 }} onClick={(e) => {
            props.onExpand(props.record, e)
          }}>收起<a-icon type="arrow-up" /></a>
        } else {
          return <a style={{ color: 'balck', marginRight: 8 }} onClick={(e) => {
            props.onExpand(props.record, e)
          }}>更多<a-icon type="arrow-down" /></a>
        }
      },
      getConfigChange (record) {
        const _this = this
        _this.logIsLoading = true
        queryManageConfChange({
          domainName: _this.domainName,
          confFiles: [{ filePath: record.filePath.replace('openEuler:', '') }]
        }).then(function (data) {
          _this.manageConfChange = data.confBaseInfos
        }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.logIsLoading = false })
      },
      handleDomainSelectCancel () {
        this.choiceDomainNameModalVisible = false
        if (this.oldDomainName) {
          router.replace(`${this.oldDomainName}`)
        } else {
          this.$message.warning('未选择业务域，返回管理列表页。')
          router.push('/configuration/transcation-domain-management')
        }
      },
      routerChangeInital () {
        // 每次路由变化都会触发，代替mounted
        if (this.domainName === '$noDomain') {
          this.choiceDomainNameModalVisible = true
        } else {
          this.oldDomainName = this.domainName
          this.choiceDomainNameModalVisible = false
          this.getTranscationDomainConfig()
        }
      }
    }
  }
</script>

<style lang="less" scoped>
  .card-title {
    display: inline-block;
    margin-right: 10px;
  }
  .diffContent {
    margin:0 -2px;
    word-break: break-all;
    white-space: pre;
  }
  .pContent{
    font-size: 16px;
    color: rgba(0, 0, 0, 0.85);
    line-height: 24px;
    display: block;
    margin-bottom: 16px;
  }
  .pLog{
    font-size: 16px;
    color: rgba(0, 0, 0, 0.85);
    line-height: 24px;
    display: block;
    margin-top: 20px;
    padding-top: 18px;
    border-top: 1px solid #e9e9e9;
  }
  .contentBox1{
    box-sizing: border-box;
    border: 1px solid #e8e8e8;
    overflow: scroll;
    height: 300px;
    width: 600px;
    white-space:nowrap;
  }
  .contentBox2{
    box-sizing: border-box;
    border: 1px solid #e8e8e8;
    overflow: scroll;
    height: 300px;
    width: 970px;
    white-space:nowrap;
  }
  .areaButton{
    position: absolute;
    right: 0;
    bottom: 0;
    width: 100%;
    border-top: 1px solid #e9e9e9;
    padding: 10px 16px;
    background: #fff;
    text-align: right;
    z-index: 1;
  }
  .oneRow{
    text-overflow: -o-ellipsis-lastline;
    overflow: hidden;
    text-overflow: ellipsis;
    display: -webkit-box;
    -webkit-line-clamp: 1;
    line-clamp: 1;
    -webkit-box-orient: vertical;
  }
  .domainName{
    border-bottom: 1px solid;
    padding: 0 3px;
    cursor: pointer;
  }
  .emptyDomainName{color: #ccc}
</style>
