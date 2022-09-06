<template>
    <a-modal :visible="visible" title="修改模型" on-ok="handleOk" @cancel="handleCancel" :width="800">
        <template slot="footer">
          <a-button key="back" @click="handleCancel">
            取消
          </a-button>
          <a-button key="submit" type="primary" @click="handleOk" :loading="updateIsLoading">
            应用
          </a-button>
        </template>
        <p>已取得模型总条数：{{ pagination.total }}</p>
        <div><a href="javascript:;">{{ modelName?'已选择'+modelName+'模型':'未选择模型' }}</a></div>
            <a-select
              style="width: 100px"
              :value="keywordType"
              @change="selectSearchType"
            >
              <a-select-option value="model_name">
                模型名称
              </a-select-option>
              <a-select-option value="tag">
                标签
              </a-select-option>
            </a-select>
          <a-input-search
            placeholder="按关键字进行搜索"
            style="width: 200px; margin: 10px 0;"
            @search="onSearch"
            :value="keyword"
            @change="onSearchChange"
          />
          <a-table
            :columns="moduleListColumns"
            :data-source="moduleListInfo"
            rowKey="model_id"
            :pagination="pagination"
            :row-selection="{ selectedRowKeys: selectedRowKeys, onChange: onSelectChange, type: 'radio'}"
            :loading="tableIsLoading"
            @change="handleTableChange"
            :scroll="{ y: 280 }"
          >
          </a-table>
    </a-modal>
</template>
<script>
import { moduleList, updateWorkflow } from '@/api/check'
import { dateFormat } from '@/views/utils/Utils'
const defaultPagination = {
    current: 1,
    pageSize: 10,
    total: 0,
    size: 'small',
    showSizeChanger: true,
    showQuickJumper: true
}
export default {
  name: 'UpdateModel',
  props: {
    workflow: {
      type: Object,
      default: () => {}
    },
    updateTarget: {
      type: Object,
      default: () => {}
    },
    visible: {
      type: Boolean,
      default: false
    }
  },
  data() {
      return {
        pagination: defaultPagination,
        tableIsLoading: false,
        updateIsLoading: false,
        // 修改模型的弹窗
        modelName: undefined,
        modelId: undefined,
        keywordType: 'model_name',
        keyword: undefined,
        moduleListInfo: [],
        selectedRowKeys: [],
        selectedRows: [],
        sorter: {},
        filters: {}
      }
  },
  watch: {
    visible (value) {
        if (value === true) {
            this.getModuleList()
        } else {
            this.resetData()
        }
    }
  },
  computed: {
    moduleListColumns () {
      let { sorter } = this
      sorter = sorter || {}
      return [
        {
          title: '模型',
          dataIndex: 'model_name',
          key: 'model_name',
          width: 140
        },
        {
          title: '算法',
          dataIndex: 'algo_name',
          key: 'algo_name'
        },
        {
          title: '精确度',
          dataIndex: 'precision',
          width: 100,
          key: 'precision',
          sorter: true,
          sortOrder: sorter.columnKey === 'precision' && sorter.order
        },
        {
          title: '标签',
          dataIndex: 'tag',
          key: 'tag'
        },
        {
          title: '创建时间',
          width: 200,
          dataIndex: 'create_time',
          key: 'create_time',
          customRender: (time) => time && dateFormat('YYYY-mm-dd HH:MM:SS', time * 1000)
          }
      ]
    }
  },
    created() {
        this.workflow_id = this.$route.params.workflowId
    },
  methods: {
    getModuleList() {
      const _this = this
      this.tableIsLoading = true
      const pagination = this.pagination || ''
      const algpFilter = this.filters.algo_name || []
      const sorter = this.sorter || {}
      const field = this.updateTarget.field
      moduleList({
        tableInfo: {
          pagination: {
              current: pagination.current,
              pageSize: pagination.pageSize
          },
          filters: {
            model_name: this.keywordType === 'model_name' ? this.keyword : undefined,
            algo_name: algpFilter,
            tag: this.keywordType === 'tag' ? this.keyword : undefined,
            field
          },
          sorter: {
            field: sorter.field,
            order: sorter.order
          }
        }
      })
      .then(function (res) {
        _this.moduleListInfo = res.result
        if (res.total_count !== 0) {
          _this.pagination.total = res.total_count
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.tableIsLoading = false
      })
    },
    onSelectChange(selectedRowKeys, selectedRows) {
      this.selectedRows = selectedRows
      this.selectedRowKeys = selectedRowKeys;
      this.modelName = selectedRows[0].model_name
      this.modelId = selectedRows[0].model_id
    },
    handleTableChange (pagination, filters, sorter) {
      // 存储翻页状态
      this.pagination = pagination
      this.filters = filters
      this.sorter = sorter
      // 出发排序、筛选、分页时，重新请求模型列表
      this.getModuleList()
    },
    selectSearchType(type) {
      this.keywordType = type
    },
    onSearchChange(e) {
      this.keyword = e.target.value
    },
    onSearch() {
      this.getModuleList()
    },
    handleOk() {
        if (!this.modelId) {
          this.$options.methods.notifyResult(this, 'error', '请先选择模型')
          return
        }
        const _this = this
        const hostId = this.updateTarget.host_id
        this.updateIsLoading = true
        switch (this.updateTarget.field) {
          case 'singlecheck':
              this.workflow.detail.singlecheck[hostId][this.updateTarget.single] = this.modelId
              break;
          case 'multicheck':
              this.workflow.detail.multicheck[hostId] = this.modelId
              break;
          case 'diag':
              this.workflow.detail.diag = this.modelId
              break;
          default:
              break;
        }
        updateWorkflow(this.workflow.detail, this.workflow_id)
          .then(function (res) {
              _this.$options.methods.notifyResult(_this, 'success', '应用成功')
              // 重新获取检测表格数据
              _this.$emit('getWorkflowDatails')
              // 关闭对话框
              _this.$emit('changeVisible')
          }).catch(function () {
              _this.$options.methods.notifyResult(_this, 'error', '应用失败')
          }).finally(function () {
              _this.updateIsLoading = false
          })
    },
    handleCancel() {
      this.$emit('changeVisible')
    },
    notifyResult(This, type, title) {
      This.$notification[type]({
        message: title
      })
    },
    resetData() {
      this.modelId = undefined
      this.modelName = undefined
      this.keywordType = 'model_name'
      this.keyword = undefined
      this.selectedRows = []
      this.selectedRowKeys = []
      this.sorter = {}
      this.filters = {}
    }
  }
}
</script>
