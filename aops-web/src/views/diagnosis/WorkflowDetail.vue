<template>
  <my-page-header-wrapper>
    <div class="diagnosis-workflow-detail">
      <a-card :bordered="false" class="aops-theme detail-card">
        <h3>{{ workflow.workflow_name }}</h3>
        <a-row :gutter="8">
          <a-col :span="6">
            主机组：<span v-if="workflow.input">{{ workflow.input.domain }}</span>
          </a-col>
          <a-col :span="6">
            主机数：<span v-if="workflow.input">{{ Object.keys(workflow.input.hosts).length }}</span>
          </a-col>
          <a-col :span="6">
            应用：{{ workflow.app_name }}
          </a-col>
          <a-col :span="6">
            状态：<span :style="activation()">{{ statusMap[workflow.status] }}</span>
          </a-col>
        </a-row>
        <a-row :gutter="8">
          <a-col :span="18" class="workflow-desc">
            描述：{{ workflow.description }}
          </a-col>
          <a-col :span="6" class="workflow-time">
            <div>
            创建时间：{{ dateFormat('YYYY-mm-dd HH:MM:SS', workflow.create_time * 1000) }}
            </div>
            <div class="control-btns">
              <a-button
                type="primary"
                @click="execute"
                :loading="excuteLoading"
                :disabled="workflow.status==='running'"
              >
                执行
              </a-button>
              <a-button
                @click="stop"
                :loading="stopLoading"
                :disabled="workflow.status==='hold'"
              >
                暂停
              </a-button>
              <a-popconfirm
                  title="确定删除本工作流吗?"
                  placement="topRight"
                  ok-text="确认"
                  cancel-text="取消"
                  @confirm="deleteWorkflow"
                  :disabled="workflow.status==='running'"
              >
                <a-button
                  type="danger"
                  :ghost="workflow.status!=='running'"
                  :disabled="workflow.status==='running'"
                >
                  删除
                </a-button>
              </a-popconfirm>
            </div>
          </a-col>
        </a-row>
        <a-row class="tab-container">
          <a-tabs default-active-key="1" @change="callback">
            <a-tab-pane key="singlecheck" tab="单指标检测">
            </a-tab-pane>
            <a-tab-pane key="multicheck" tab="多指标检测">
            </a-tab-pane>
            <a-tab-pane key="diag" tab="集群故障诊断">
            </a-tab-pane>
          </a-tabs>
        </a-row>
      </a-card>
      <a-card v-show="key == 'singlecheck'" :bordered="false" class="aops-theme">
        <div class="tableWidth">
            <a-table
              rowKey="host_ip"
              :columns="hostcheckColums"
              :data-source="singlecheck"
              :pagination="pagination"
              :loading="tableIsLoading"
              :expandedRowKeys.sync="expandedRowKeys"
            >
                <p slot="expandedRowRender" slot-scope="value" style="margin: 0">
                <a-table rowKey="single" :columns="singlecheckColumns" :data-source="value.model" :scroll="{ y: 240 }" :pagination="false">
                  <template slot="action" slot-scope="record">
                    <a slot="action" href="javascript:;" @click="showModal(record, 'singlecheck')">修改</a>
                  </template>
              </a-table>
            </p>
          </a-table>
        </div>
      </a-card>
      <a-card v-show="key == 'multicheck'" :bordered="false" class="aops-theme">
        <a-table
          :columns="multicheckColumns"
          :data-source="multicheck"
          rowKey="host_id"
          :pagination="pagination"
          :loading="tableIsLoading">
          <template slot="action" slot-scope="record">
            <a slot="action" href="javascript:;" @click="showModal(record, 'multicheck')">修改</a>
          </template>
          </a-table>
      </a-card>
      <a-card v-show="key == 'diag'" :bordered="false" class="aops-theme">
      <div class="tableWidth">
        <a-table
          :columns="diagColumns"
          rowKey="model_name"
          :data-source="diag"
          :pagination="false"
          :loading="tableIsLoading">
          <template slot="action" slot-scope="record">
            <a slot="action" href="javascript:;" @click="showModal(record, 'diag')">修改</a>
          </template>
          </a-table>
      </div>
      </a-card>
      <UpdateModel
        :workflow="workflow"
        :updateTarget="updateTarget"
        :visible="visible"
        @getWorkflowDatails="getWorkflowDatails"
        @changeVisible="changeVisible"
        ref="updateModel"
        ></UpdateModel>
    </div>
  </my-page-header-wrapper>
</template>

<script>
import router from '@/vendor/ant-design-pro/router'
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import UpdateModel from './components/UpdateModel.vue';
import { getWorkflowDatail, executeWorkflow, stopWorkflow, deleteWorkflow } from '@/api/check'
import { dateFormat } from '@/views/utils/Utils'

const hostcheckColums = [
  { title: '主机名', dataIndex: 'host_name', key: 'host_name' },
  { title: 'IP', dataIndex: 'host_ip', key: 'host_ip' },
  { title: '指标数', dataIndex: 'IndicatordNumber', key: 'IndicatordNumber' }
];
const singlecheckColumns = [
  { title: '单指标', dataIndex: 'single', key: 'single' },
  { title: '算法', dataIndex: 'algo_name', key: 'algo_name' },
  { title: '模型', dataIndex: 'model_name', key: 'model_name' },
  { title: '操作', dataIndex: '', key: 'x', scopedSlots: { customRender: 'action' } }
];
const multicheckColumns = [
  { title: '主机名', dataIndex: 'host_name', key: 'host_name' },
  { title: 'IP', dataIndex: 'host_ip', key: 'host_ip' },
  { title: '算法', dataIndex: 'algo_name', key: 'algo_name' },
  { title: '模型', dataIndex: 'model_name', key: 'model_name' },
  { title: '操作', dataIndex: '', key: 'x', scopedSlots: { customRender: 'action' } }
];
const diagColumns = [
  { title: '算法', dataIndex: 'algo_name', key: 'algo_name' },
  { title: '模型', dataIndex: 'model_name', key: 'model_name' },
  { title: '操作', dataIndex: '', key: 'x', scopedSlots: { customRender: 'action' } }
];
const defaultPagination = {
    current: 1,
    pageSize: 10,
    size: 'small',
    showSizeChanger: true,
    showQuickJumper: true
}
const statusMap = {
  'hold': '待运行',
  'recommending': '推荐中',
  'running': '运行中'
}
export default {
  name: 'WorkflowDetail',
  components: {
    MyPageHeaderWrapper,
    UpdateModel
},
  mounted: function () {
    this.workflow_id = this.$route.params.workflowId
    this.getWorkflowDatails()
  },
  data() {
    return {
      workflow: {},
      statusMap,
      hostcheckColums,
      singlecheckColumns,
      expandedRowKeys: [],
      diagColumns,
      multicheckColumns,
      pagination: defaultPagination,
      tableIsLoading: false,
      key: 'singlecheck',
      singlecheckModel: [],
      singlecheck: [],
      multicheck: [],
      diag: [],
      updateTarget: {},
      visible: false,
      excuteLoading: false,
      stopLoading: false,
      deleteLoading: false
    }
  },
  computed: {
    moduleListColumns () {
      let { sorter, filters } = this
      sorter = sorter || {}
      filters = filters || {}
      return [
        {
          title: '模型',
          dataIndex: 'model_name',
          key: 'model_name'
        },
        {
          title: '算法',
          dataIndex: 'algo_name',
          key: 'algo_name',
          filteredValue: filters.algo_name || null,
          filters: this.filterAlgos
        },
        {
          title: '精确度',
          dataIndex: 'precision',
          key: 'precision',
          sorter: true,
          sortOrder: sorter.columnKey === 'precision' && sorter.order
        },
        {
          title: '场景',
          dataIndex: 'tag',
          key: 'tag'
        },
        {
          title: '创建时间',
          dataIndex: 'create_time',
          key: 'create_time',
          customRender: (time) => time && dateFormat('YYYY-mm-dd HH:MM:SS', time * 1000)
          }
      ]
    },
    activation () {
      return () => {
        if (this.workflow.status === 'hold') {
          return {'color': 'blue'}
        } else if (this.workflow.status === 'running') {
          return {'color': 'rgb(124, 201, 135)'}
        } else {
          return {'color': 'rgb(254, 172, 70)'}
        }
      }
    }
  },
  methods: {
    dateFormat,
    getWorkflowDatails() {
      const _this = this
      this.tableIsLoading = true
      getWorkflowDatail(this.workflow_id)
        .then(function (res) {
          _this.workflow = res.result
          const tempArr = []
          for (const modelId in _this.workflow.model_info) {
            if (modelId === _this.workflow.detail.diag) {
              tempArr.push(_this.workflow.model_info[modelId])
            }
          }
          _this.diag = tempArr
          _this.buildSinglecheckData()
          _this.buildMulticheckData()
        }).catch(function (err) {
          _this.$message.error(err.response.msg)
        }).finally(function () {
          _this.tableIsLoading = false
        })
    },
    buildMulticheckData() {
      const tempArr = []
      for (const hostId in this.workflow.detail.multicheck) {
        const temp1 = {
          host_id: hostId
        }
        // 获取主机id对应的主机信息，模型id对应的模型信息，合并对象
        const temp = Object.assign(temp1, this.workflow.input.hosts[hostId], this.workflow.model_info[this.workflow.detail.multicheck[hostId]])
        tempArr.push(temp)
      }
      this.multicheck = tempArr
    },
    buildSinglecheckData() {
      const tempArr = []
      const tempModalArr = []
      for (const hostId in this.workflow.detail.singlecheck) {
            const temp1 = {
              // 指标数
              IndicatordNumber: Object.keys(this.workflow.detail.singlecheck[hostId]).length.toString()
            }
            // 获取主机id对应的主机信息，合并对象
            const temp = Object.assign(temp1, this.workflow.input.hosts[hostId])
            tempArr.push(temp);
      }
      this.singlecheck = tempArr
      // 获取每个主机对应的指标模型信息
      for (const hostId in this.workflow.detail.singlecheck) {
        for (const singleName in this.workflow.detail.singlecheck[hostId]) {
          const model = {
            host_id: hostId,
            single: singleName,
            model_name: this.workflow.model_info[this.workflow.detail.singlecheck[hostId][singleName]].model_name,
            algo_name: this.workflow.model_info[this.workflow.detail.singlecheck[hostId][singleName]].algo_name
          }
          tempModalArr.push(model);
        }
        this.singlecheckModel = tempModalArr
      }
      // 将每个主机对应的模型信息加入到singlecheck的表格数据(子表格)
      for (const key in this.singlecheck) {
        this.singlecheck[key].model = []
        for (let index = 0; index < this.singlecheck[key].IndicatordNumber; index++) {
          this.singlecheck[key].model.push(this.singlecheckModel[index])
        }
        this.singlecheckModel.splice(0, this.singlecheck[key].IndicatordNumber)
      }
    },
    execute() {
        this.excuteLoading = true
        executeWorkflow({
            workflowId: this.workflow_id
        }).then((res) => {
            this.$message.success(res.msg);
            this.getWorkflowDatails();
        }).catch((err) => {
            this.$message.error(err.response.data.msg);
        }).finally(() => {
          this.excuteLoading = false
        })
    },
    stop() {
        this.stopLoading = true
        stopWorkflow({
            workflowId: this.workflow_id
        }).then((res) => {
            this.$message.success(res.msg);
            this.getWorkflowDatails();
        }).catch((err) => {
            this.$message.error(err.response.data.msg);
        }).finally(() => {
          this.stopLoading = false
        })
    },
    deleteWorkflow() {
        this.deleteLoading = true
        deleteWorkflow({
            workflowId: this.workflow_id
        }).then((res) => {
            this.$message.success(res.msg);
            setTimeout(function() {
              router.push('/diagnosis/workflow')
            }, 500)
        }).catch((err) => {
            this.$message.error(err.response.data.msg);
        }).finally(() => {
            this.deleteLoading = false
        })
    },
    callback(key) {
      this.key = key
    },
    showModal(record, field) {
      // 需要修改模型的指标、host 或者 host的某single
      this.updateTarget.field = field
      if (field === 'singlecheck' || field === 'multicheck') {
        this.updateTarget.single = record.single
        this.updateTarget.host_id = record.host_id
      }
      this.visible = true
    },
    changeVisible() {
      this.visible = false
    }
  }
}
</script>
<style lang="less" scoped>
  .detail-card {
    padding-bottom: 20px;
  }
  .tab-container {
    position: absolute;
    bottom: -16px;
  }

  .detail-card {
    .ant-row:not(:last-child) {
      margin-bottom: 10px;
    }
    .workflow-desc {
      word-break: break-word;
    }
    .control-btns {
      margin-top: 10px;
      button:not(:last-child) {
        margin-bottom: 8px;
        margin-right:10px;
      }
    }
  }
</style>
