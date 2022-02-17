<template>
  <div>
    <a-row class="aops-app-table-control-row" type="flex" justify="space-between">
      <a-col>
        <a-row type="flex" :gutter="6">
          <a-col v-if="selectedRowKeys.length > 0">
            <a-alert type="info" show-icon>
              <div slot="message">
                <span>{{ `已选择`+ selectedRowKeys.length +`项` }}</span>
                <a @click="resetSelection"> 清除选择</a>
              </div>
            </a-alert>
          </a-col>
        </a-row>
      </a-col>
      <a-col>
        <a-row type="flex" :gutter="6">
          <a-col>
            <a-input-search placeholder="按CVE ID搜索" style="width: 200px" @search="onSearch" />
          </a-col>
          <a-col>
            <status-change-modal
              :selectedRowsAll="selectedRowsAll"
              @statusUpdated="handleStatusUpdated"
            />
          </a-col>
          <a-col>
            <upload-file v-if="standalone ? true : false" @addSuccess="handleUploadSuccess" />
          </a-col>
          <a-col v-if="selectedRowKeys.length === 0">
            <create-repair-task-drawer
              text="生成修复任务"
              taskType="cve"
              :cveListProps="standalone ? cveAllList : cveAllListProp"
              :loading="standalone ? cveAllIsLoading: cveAllIsLoadingProp"
              :hostListType="standalone ? 'byLoading' : 'byOneHost'"
              :hostList="hostList"
              @createSuccess="handleTaskCreateSuccess"
            />
          </a-col>
          <a-col v-else>
            <create-repair-task-drawer
              taskType="cve"
              :cveListProps="selectedRowsAll"
              :hostListType="standalone ? 'byLoading' : 'byOneHost'"
              :hostList="hostList"
              @createSuccess="handleTaskCreateSuccess"
            />
          </a-col>
          <a-col>
            <a-button @click="handleRefresh">
              <a-icon type="redo" />
            </a-button>
          </a-col>
        </a-row>
      </a-col>
    </a-row>
    <a-table
      rowKey="cve_id"
      :columns="standalone ? tableColumnsStandalone : tableColumns"
      :data-source="standalone ? tableData : inputList"
      :pagination="pagination"
      :rowSelection="rowSelection"
      :expandIconAsCell="false"
      :expandIconColumnIndex="1"
      @change="handleTableChange"
      :loading="standalone ? tableIsLoading : inputLoading"
    >
      <router-link :to="{ path: `/leaks/cves-management/${id}` }" slot="cve_id" slot-scope="id">{{ id }}</router-link>
      <div slot="expandedRowRender" slot-scope="record" style="margin: 0">
        <p>Description:</p>
        <p>{{ record.description }}</p>
      </div>
    </a-table>
  </div>
</template>

<script>
/****************
/* cve表格组件
/* cve 表格的业务逻辑公共组件。根据props中standalone属性确定是自动获取列表信息，还是通过外部获取列表信息。
****************/

import CreateRepairTaskDrawer from './CreateRepairTaskDrawer'
import StatusChangeModal from './StatusChangeModal'
import { getSelectedRow } from '../utils/getSelectedRow'
import { getCveList } from '@/api/leaks'

import { statusList, statusMap, severityMap } from '../config'
import UploadFile from './UploadFile.vue'

const defaultPagination = {
  current: 1,
  pageSize: 10,
  total: 10,
  showSizeChanger: true,
  showQuickJumper: true
}

export default {
  name: 'CVEsTable',
  components: {
    CreateRepairTaskDrawer,
    StatusChangeModal,
    UploadFile
  },
  props: {
    // 判断表格是自己发起请求获取数据还是，触发事件通过父组件获取列表数据
    standalone: {
      type: Boolean,
      default: false
    },
    // 如果通过父组件获取数据，则此属性为外部传入的列表数据
    inputList: {
      type: Array,
      default: () => []
    },
    inputLoading: {
      type: Boolean,
      default: false
    },
    // 生成修复任务时，如果任务中的host是指定的，则使用此属性
    // 目前只有主机详情页中生成修复任务时会用到
    hostList: {
      type: Array,
      default: () => []
    },
    // 当通过父组件获取数据时，通过此属性同步数据的最大数量
    paginationTotal: {
      type: Number,
      default: undefined
    },
    // 当通过父组件获取全量cve列表数据时，使用此属性
    cveAllListProp: {
      type: Array,
      default: () => []
    },
    cveAllIsLoadingProp: {
      type: Boolean,
      default: false
    }
  },
  computed: {
    tableColumnsStandalone () {
      let { filters } = this
      filters = filters || {}
      return [
        {
          dataIndex: 'cve_id',
          key: 'cve_id',
          title: 'CVE_ID',
          sorter: true,
          scopedSlots: { customRender: 'cve_id' },
          width: 250
        },
        {
          dataIndex: 'publish_time',
          key: 'publish_time',
          title: '发布时间',
          sorter: true
        },
        {
          dataIndex: 'severity',
          key: 'severity',
          title: '严重性',
          customRender: (severity) => severityMap[severity],
          filteredValue: filters.severity || null,
          filters: [
            {
              text: '严重',
              value: 'Critical'
            },
            {
              text: '高风险',
              value: 'High'
            },
            {
              text: '中风险',
              value: 'Medium'
            },
            {
              text: '低风险',
              value: 'Low'
            },
            {
              text: '未知',
              value: 'Unknown'
            }
          ]
        },
        {
          dataIndex: 'cvss_score',
          key: 'cvss_score',
          title: 'CVSS 分数',
          sorter: true
        },
        {
          dataIndex: 'host_num',
          key: 'host_num',
          title: '主机',
          sorter: true
        },
        {
          dataIndex: 'status',
          key: 'status',
          title: '状态',
          filteredValue: filters.status || null,
          filters: statusList,
          customRender: (status) => statusMap[status]
        }
      ]
    },
    tableColumns () {
      let { filters } = this
      filters = filters || {}
      return [
        {
          dataIndex: 'cve_id',
          key: 'cve_id',
          title: 'CVE_ID',
          scopedSlots: { customRender: 'cve_id' },
          width: 250
        },
        {
          dataIndex: 'publish_time',
          key: 'publish_time',
          title: '发布时间',
          sorter: true
        },
        {
          dataIndex: 'severity',
          key: 'severity',
          title: '严重性',
          customRender: (severity) => severityMap[severity],
          filteredValue: filters.severity || null,
          filters: [
            {
              text: '严重',
              value: 'Critical'
            },
            {
              text: '高风险',
              value: 'High'
            },
            {
              text: '中风险',
              value: 'Medium'
            },
            {
              text: '低风险',
              value: 'Low'
            },
            {
              text: '未知',
              value: 'Unknown'
            }
          ]
        },
        {
          dataIndex: 'cvss_score',
          key: 'cvss_score',
          title: 'CVSS 分数',
          sorter: true
        },
        {
          dataIndex: 'status',
          key: 'status',
          title: '状态',
          filteredValue: filters.status || null,
          filters: statusList,
          customRender: (status) => statusMap[status]
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
    paginationTotal () {
      this.pagination.total = this.paginationTotal
    }
  },
  data () {
    return {
      tableData: [],
      tableIsLoading: false,
      // pagination control
      pagination: defaultPagination,
      filters: null,
      sorter: null,
      // selection control
      selectedRowKeys: [],
      selectedRowsAll: [],
      // standalone模式下获取全量cve数据
      cveAllList: [],
      cveAllIsLoading: false,
      // 控制上传弹框显隐
      upLoadFileVisible: false
    }
  },
  methods: {
    handleTableChange (pagination, filters, sorter) {
      // 存储翻页状态
      this.pagination = pagination
      this.filters = Object.assign({}, this.filters, filters)
      this.sorter = sorter
      // 出发排序、筛选、分页时，重新请求主机列表
      this.getCves()
    },
    onSelectChange (selectedRowKeys, selectedRows) {
      const tableData = this.standalone ? this.tableData : this.inputList
      this.selectedRowKeys = selectedRowKeys
      this.selectedRowsAll = getSelectedRow(selectedRowKeys, this.selectedRowsAll, tableData, 'cve_id')
    },
    resetSelection () {
      this.selectedRowKeys = []
      this.selectedRowsAll = []
    },
    handleRefresh () {
      this.selectedRowKeys = []
      this.selectedRowsAll = []
      this.getCves()
    },
    handleReset () {
      this.pagination = defaultPagination
      this.sorter = null
      this.filters = null
      this.selectedRowKeys = []
      this.selectedRowsAll = []
      this.getCves()
    },
    // 获取cve列表数据
    getCves () {
      const _this = this
      this.tableIsLoading = true
      const pagination = this.pagination || {}
      const filters = this.filters || {}
      const sorter = this.sorter || {}
      // 非standalone模式下，触发事件通过父组件获取数据
      if (!this.standalone) {
        this.$emit('getTableData', {
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
        return
      }
      getCveList({
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
        _this.tableData = res.result || []
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
    // 获取全部cve数据，用于生成修复任务时选择全部cve
    getCvesAll () {
      const _this = this
      this.cveAllIsLoading = true
      if (!this.standalone) {
        this.$emit('getCveAll', {
          tableInfo: {
            pagination: {},
            filters: {},
            sorter: {}
          }
        })
        return
      }
      getCveList({
        tableInfo: {
          pagination: {},
          filters: {},
          sorter: {}
        }
      }).then(function (res) {
        _this.cveAllList = res.result || []
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () { _this.cveAllIsLoading = false })
    },
    onSearch (text) {
      this.pagination = defaultPagination
      if (!this.filters) {
        this.filters = {}
      }
      if (text !== '') {
        this.filters.cveId = text
      } else {
        this.filters.cveId = undefined
      }
      this.getCves()
    },
    handleTaskCreateSuccess () {
      this.handleRefresh()
    },
    handleStatusUpdated () {
      this.selectedRowKeys = []
      this.selectedRowsAll = []
      if (this.standalone) {
        this.handleRefresh()
      } else {
        const pagination = this.pagination || {}
        const filters = this.filters || {}
        const sorter = this.sorter || {}
        this.$emit('statusUpdated', {
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
      }
    },
    uploadfile() {
    },
    handleUploadSuccess() {
    }
  },
  mounted () {
    this.getCves()
    this.getCvesAll()
  }
}
</script>

<style lang="less" scoped>
</style>
