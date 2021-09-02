
<template>
  <page-header-wrapper>
    <a-card :bordered="false">
      <div>
        <div>
          <h2 class="card-title">{{configName}}配置表</h2>
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
                <a-input placeholder="请搜索配置项名称" @pressEnter="handleInput"/>
              </a-col>
              <a-col>
                <a @click="showAddConfig">
                  <a-button type="primary">
                    <a-icon type="plus" />新增配置
                  </a-button>
                </a>
              </a-col>
              <a-col>
                <a-button @click="handleRefresh">
                  <a-icon type="redo" />刷新
                </a-button>
              </a-col>
              <a-col>
                <a-button>
                  更多操作<a-icon type="arrow-down" />
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
            <span slot="action" slot-scope="record">
                <a @click="showConfigContent(record)">查看配置文件</a>
                <a-divider type="vertical" />
                <a @click="showConfigChange(record)">配置修改日志</a>
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
          title="新增配置"
          :width="720"
          placement="right"
          :visible="addConfigVisible"
          :body-style="{ paddingBottom: '80px' }"
          @close="closeAddConfig"
        >
          <a-form
            :model="configList"
            v-for="(item, index) in configList"
            :key="item.key"
            :label-col="{ span: 5 }"
            :wrapper-col="{ span: 18 }"
          >
            <a-form-item label="所属业务域" v-if="index === 0">
              <a-input :value="configName" disabled ></a-input>
            </a-form-item>
            <a-descriptions style="border-top: 1px solid #e9e9e9;" :column="1" layout="horizontal" v-if="configList.length > 1">
              <a-descriptions-item>
                <a-icon
                  class="dynamic-delete-button"
                  type="minus-circle-o"
                  @click="removeRows(item)"
                />
                新增配置{{index+1}}
              </a-descriptions-item>
            </a-descriptions>
            <a-form-item label="存储地址">
              <a-input v-model="configList[index].filePath" placeholder="请输入存储地址"></a-input>
            </a-form-item>
            <a-form-item label="配置来源">
              <a-row>
                <a-col :span="12">
                  <a-select v-model="configList[index].configSource" placeholder="请选择来源">
                    <a-select-option value="0">手动输入</a-select-option>
                    <a-select-option value="1">从主机导入</a-select-option>
                  </a-select>
                </a-col>
                <a-col :span="12" :push="1">
                  <a-tooltip placement="topLeft">
                    <template slot="title">
                      <span>配置来源二选一，推荐使用手动输入</span>
                    </template>
                    <a-icon type="question-circle" />
                  </a-tooltip>
                </a-col>
              </a-row>
            </a-form-item>
            <a-form-item label="配置内容" v-if="configList[index].configSource === '0'">
              <a-input type="textarea" v-model="configList[index].contents" placeholder="请输入配置内容"></a-input>
            </a-form-item>
            <a-form-item label="选择主机" v-if="configList[index].configSource === '1'">
              <a-select placeholder="请选择文件所在主机" v-model="configList[index].hostId">
                <a-select-option value="host123">host123 | IP:255.255.255.255</a-select-option>
                <a-select-option value="host111">host111 | IP:111.111.111.111</a-select-option>
                <a-select-option value="host222">host222 | IP:222.222.222.222</a-select-option>
              </a-select>
            </a-form-item>
            <a-button v-if="configList.length === index+1" type="dashed" style="width: 100%" @click="addRows()">
              <a-icon type="plus" /> 新增配置
            </a-button>
          </a-form>
          <div class="areaButton">
            <a-button :style="{ marginRight: '8px' }" @click="closeAddConfig">取消</a-button>
            <a-button type="primary" @click="sumbitAddConfig">确定</a-button>
          </div>
        </a-drawer>
        <a-drawer
          title="配置文件内容"
          :width="720"
          placement="right"
          :visible="configContentVisible"
          :body-style="{ paddingBottom: '80px' }"
          @close="closeConfigContent"
        >
          <a-descriptions :column="1" layout="horizontal">
            <a-descriptions-item label="配置项">
              {{configContent.name}}
            </a-descriptions-item>
            <a-descriptions-item label="配置文件地址">
              {{configContent.filePath}}
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
          <a-descriptions :column="1" layout="horizontal">
            <a-descriptions-item label="所属业务域">
              {{configName}}
            </a-descriptions-item>
          </a-descriptions>
          <a-descriptions :column="1" layout="vertical" bordered>
            <a-descriptions-item :label="'配置项：'+manageConfChange[0].filePath">
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
        </a-drawer>
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
  import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
  import { addManagementConf, getManagementConf, queryManageConfChange, deleteManagementConf } from '@/api/management'

  const defaultPagination = {
    current: 1,
    pageSize: 10,
    showSizeChanger: true,
    showQuickJumper: true
  }

  export default {
    name: 'TranscationDomainConfigurations',
    components: {
      PageHeaderWrapper
    },
    data () {
      return {
        rowKey: 'id',
        pagination: defaultPagination,
        filters: null,
        sorter: null,
        tableData: [],
        selectedRowKeys: [],
        selectedRows: [],
        tableIsLoading: false,
        addIsLoading: false,
        configName: '业务域456',
        configContent: {},
        addConfigVisible: false,
        configContentVisible: false,
        configChangeVisible: false,
        manageConfChange: [{}],
        /* 新增表单相关 */
        form: this.$form.createForm(this),
        submitLoading: false,
        configList: [{
          filePath: '',
          configSource: '',
          contents: '',
          hostId: ''
        }]
      }
    },
    computed: {
      columns () {
        let { sorter } = this
        sorter = sorter || {}
        return [
          {
            dataIndex: 'name',
            key: 'name',
            title: '配置项',
            sorter: true,
            sortOrder: sorter.columnKey === 'name' && sorter.order
          },
          {
            dataIndex: 'filePath',
            key: 'filePath',
            title: '配置文件地址'
          },
          {
            key: 'operation',
            title: '操作',
            scopedSlots: { customRender: 'action' }
          }
        ]
      },
      confChangeColumns () {
        return [
          { title: '变更ID', dataIndex: 'changeId', key: 'changeId' },
          { title: '变更时间', dataIndex: 'date', key: 'date' },
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
    methods: {
      handleTableChange (pagination, filters, sorter) {
        console.log(pagination, filters, sorter)
        // 存储翻页状态
        this.pagination = pagination
        this.filters = filters
        this.sorter = sorter
        // 出发排序、筛选、分页时，重新请求主机列表
        this.getTranscationDomainConfig({})
      },
      handleInput (e) {
        console.log(e)
      },
      onSelectChange (selectedRowKeys, selectedRows) {
        console.log(`selectedRowKeys: ${selectedRowKeys}`, 'selectedRows: ', selectedRows)
        this.selectedRowKeys = selectedRowKeys
        this.selectedRows = selectedRows
      },
      // 获取列表数据
      getTranscationDomainConfig ({ p, f, s }) {
        const _this = this
        this.tableIsLoading = true
        const pagination = p || this.pagination
        const filters = f || this.filters
        const sorter = s || this.sorter

        getManagementConf({
          uid: '123',
          tableInfo: {
            pagination: {
              current: pagination.current,
              pageSize: pagination.pageSize
            },
            filters: filters || {},
            sorter: sorter ? {
              field: sorter.field,
              order: sorter.order
            } : {}
          }
        })
          .then(function (res) {
            console.log(res)
            _this.tableData = res.result.manageConf_infos
          }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      deleteConfig (record) {
        return this.handleDelete([record.id])
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
        console.log(managementConfList)
        return new Promise((resolve, reject) => {
          deleteManagementConf({
            managementConfList
          })
            .then((res) => {
              _this.$message.success('删除成功')
              _this.getTranscationDomainConfig({})
              if (isBash) _this.selectedRowKeys = []
              resolve()
            })
            .catch((err) => {
              _this.$message.error(err.response.data.message)
              reject(err)
            })
        })
      },
      handleRefresh () {
        this.pagination = defaultPagination
        this.sorter = null
        this.filters = null
        this.selectedRowKeys = []
        this.getTranscationDomainConfig({})
      },
      /* 新增配置 */
      showAddConfig () {
        this.addConfigVisible = true
      },
      closeAddConfig () {
        this.addConfigVisible = false
      },
      addRows () {
        this.configList.push({
          filePath: '',
          configSource: '',
          contents: '',
          hostId: '',
          key: Date.now()
        })
      },
      removeRows (item) {
        const index = this.configList.indexOf(item)
        if (index !== -1) {
          if (this.configList.length === 2) {
            this.configList = [{
              filePath: '',
              configSource: '',
              contents: '',
              hostId: ''
            }]
          } else {
            this.configList.splice(index, 1)
          }
        }
      },
      sumbitAddConfig () {
        const _this = this
        this.addIsLoading = true
        for (let i = 0; i < _this.configList.length; i++) {
          delete _this.configList[i].configSource
        }
        addManagementConf({
          uid: '123',
          name: _this.configName,
          configList: _this.configList
        }).then(function () {
            _this.$message.success('添加成功')
            _this.addConfigVisible = false
          })
          .catch(function (err) {
            _this.$message.error(err.response.data.message)
          })
          .finally(function () {
            _this.addIsLoading = false
          })
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
        queryManageConfChange({
          managementConfId: record.id
        }).then(function (res) {
          _this.manageConfChange = res.result.manageConfChange
          console.log(_this.manageConfChange)
        }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      }
    },
    mounted: function () {
      this.getTranscationDomainConfig({})
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
</style>
