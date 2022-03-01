<template>
  <div>
    <a-button :disabled="disabled" :loading="loading" @click="handleOpen" type="primary">
      {{ taskType === 'cve' ? `${text}` : '设置REPO' }}
    </a-button>
    <a-drawer
      :title="`生成任务${taskType === 'repo' ? ' 设置REPO' : ''}`"
      closable
      @close="handleCancel"
      :visible="visible"
      :body-style="{ paddingBottom: '80px' }"
      width="650"
      destroyOnClose
    >
      <div class="create-task-contenxt">
        <a-form :form="form" :label-col="{ span: 5 }" :wrapper-col="{ span: 16 }">
          <a-form-item label="任务类型">{{ taskTypsEnum[taskType] }}</a-form-item>
          <a-form-item label="任务名称">
            <a-input
              :maxLength="50"
              v-decorator="[
                'task_name',
                { rules: [
                    {required: true, message: '请输入任务名称' },
                  ],
                  initialValue: taskNameDefault
                }
              ]"
              placeholder="请输入任务名称，50个字符以内"
            />
          </a-form-item>
          <a-form-item label="任务描述">
            <a-textarea
              :maxLength="60"
              v-decorator="[
                'task_desc',
                { rules: [
                    {required: true, message: '请输入任务描述' },
                  ],
                  initialValue: taskDescDefault
                }
              ]"
              :rows="4"
              placeholder="请输入任务描述，60个字符以内"
            />
          </a-form-item>
          <a-form-item label="自动重启" v-if="taskType === 'cve'">
            <a-switch :checked="isResetChecked" @click="handleResetChanage">
              <a-icon slot="checkedChildren" type="check" />
              <a-icon slot="unCheckedChildren" type="close" />
            </a-switch>
          </a-form-item>
          <a-form-item label="选择REPO" v-if="taskType === 'repo'">
            <a-select
              v-decorator="[
                'repo',
                { rules: [
                  {required: true, message: '请选择REPO' },
                ]}
              ]"
              placeholder="请选择REPO"
            >
              <a-select-option
                v-for="repo in repoList"
                :value="repo.repo_name"
                :key="repo.repo_id"
              >
                {{ repo.repo_name }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </a-form>
        <div v-if="taskType === 'cve'">
          <a-table
            rowKey="cve_id"
            :columns="tableColumns"
            :data-source="cveList"
            :pagination="false"
          >
            <div slot="hostsList" slot-scope="hostsList">
              <a-spin v-if="hostUnderCveLoading" />
              <span v-else>
                {{ hostsList ? hostsList.length : 0 }}
              </span>
            </div>
            <div slot="packages" slot-scope="packages">
              <a-spin v-if="actionsIsLoading" />
              <span v-else>
                {{ packages }}
              </span>
            </div>
            <a-table
              rowKey="host_id"
              slot="expandedRowRender"
              slot-scope="record"
              :columns="innerColumns"
              :rowSelection="{
                selectedRowKeys: selectedRowKeyMaps[record.cve_id] || [],
                onChange: function(selectedRowKeys, selectedRows){ onSelectChange(selectedRowKeys, selectedRows, record.cve_id)}
              }"
              :data-source="record.hostsList || []"
              :pagination="false"
            >
            </a-table>
          </a-table>
        </div>
        <div v-if="taskType === 'repo' && dataType === 'all'" style="margin-bottom: 4px;">
          根据筛选条件获取到以下主机：
        </div>
        <div v-if="taskType === 'repo'">
          <a-table
            rowKey="host_id"
            :columns="tableColumnsRepo"
            :data-source="hostList"
            :rowSelection="repoRowSelection"
            :pagination="false"
          />
        </div>
        <div
          :style="{ position: 'absolute', right: 0, bottom: 0, width: '100%', borderTop: '1px solid #e9e9e9', padding: '10px 16px', background: '#fff', textAlign: 'right', zIndex: 1}"
        >
          <a-button :style="{ marginRight: '8px' }" @click="handleCancel">
            取消
          </a-button>
          <a-button
            :style="{ marginRight: '8px' }"
            type="primary"
            @click="handleSubmit(false)"
            :disabled="submitAndExecuteLoading || hostUnderCveLoading || actionsIsLoading"
            :loading="submitLoading"
          >
            创建
          </a-button>
          <a-button
            type="primary"
            @click="handleSubmit(true)"
            :disabled="submitLoading || hostUnderCveLoading || actionsIsLoading"
            :loading="submitAndExecuteLoading"
          >
            立即执行
          </a-button>
        </div>
      </div>
    </a-drawer>
    <a-modal
      :closable="false"
      :visible="jumpModalVisible"
      :footer="null"
      destroyOnClose
    >
      <div>
        <a-row type="flex" :gutter="12">
          <a-col>
            <a-icon type="check-circle" style="font-size: 32px;color: #52c41a"/>
          </a-col>
          <a-col>
            <h3>{{ jumpModalTitle || '成功' }}</h3>
            <p>
              <a @click="jumpToPage">点击跳转到该任务页面</a>
            </p>
            <p>{{ countDown }}秒后回到原页面</p>
          </a-col>
        </a-row>
        <a-row type="flex" justify="end">
          <a-button type="primary" @click="jumpModalClose">
            关闭
          </a-button>
        </a-row>
      </div>
    </a-modal>
  </div>
</template>

<script>
/****************
/* 新建修复任务/repo设置任务弹窗
****************/

import {
  getHostUnderMultipleCVE,
  getActionUnderMultipleCVE,
  generateTask,
  executeTask,
  generateRepoTask
} from '@/api/leaks'

const taskTypes = ['cve', 'repo']
const dataTypes = ['selected', 'all']
const taskTypsEnum = {
  'cve': 'cve修复',
  'repo': 'repo设置'
}
const hostListTypes = ['byLoading', 'bySelection', 'byOneHost']
const restartTypesEnum = {
  'true': '是',
  'false': '否'
}

export default {
    name: 'CreateRepairTaskDrawer',
    props: {
      // 基本控制信息
      text: {
        type: String,
        default: '生成修复任务'
      },
      disabled: {
        type: Boolean,
        default: false
      },
      taskType: {
        type: String,
        default: taskTypes[0]
      },
      dataType: {
        type: String,
        default: dataTypes[0]
      },
      // 要修复的cve列表
      cveListProps: {
        type: Array,
        default: () => []
      },
      // cve下主机数据的获取方式：byLoading自行加载、bySelection和byOneHost都由外部传入
      hostListType: {
        type: String,
        default: hostListTypes[0]
      },
      // hostListType为bySelection和byOneHost时，使用此数据
      hostList: {
        type: Array,
        default: () => []
      },
      // 设置repo时，使用此属性进行选择
      repoList: {
        type: Array,
        default: () => []
      },
      loading: {
        type: Boolean,
        default: false
      }
    },
    data () {
        return {
          visible: false,
          taskTypsEnum,
          form: this.$form.createForm(this),
          // cve列表，包含开展开的host数据
          cveList: [],
          selectedRowKeyMaps: {},
          selectedRowsAllMaps: {},
          submitLoading: false,
          submitAndExecuteLoading: false,
          // 是否重启按钮数据
          isResetChecked: true,
          // 自动生成的任务名称和描述，初始化为空
          taskNameDefault: '',
          taskDescDefault: '',
          // 创建任务时，cve下action数据
          hostUnderCveLoading: false,
          actionsIsLoading: false,

          selectedRepoKeys: [],
          selectedRepoRows: [],
          // 创建完成后跳转控制
          jumpTaskId: '',
          jumpModalTitle: '',
          jumpModalVisible: false,
          countDown: 5,
          jumpModalInterval: null
        }
    },
    computed: {
      tableColumns () {
        return [
          {
            dataIndex: 'cve_id',
            key: 'cve_id',
            title: 'CVE_ID',
            scopedSlots: { customRender: 'cve_id' },
            width: 180
          },
          {
            dataIndex: 'hostsList',
            key: 'hostsList',
            title: '主机',
             width: 60,
            scopedSlots: { customRender: 'hostsList' }
          },
          {
            dataIndex: 'package',
            key: 'package',
            title: '修复软件包',
             width: 100,
            scopedSlots: { customRender: 'packages' }
          },
          {
            dataIndex: 'reboot',
            key: 'reboot',
            width: 120,
            title: <span>重启后生效</span>,
            customRender: (reboot) => restartTypesEnum[reboot]
          }
        ]
      },
      innerColumns () {
        return [
          {
            dataIndex: 'host_name',
            key: 'host_name',
            title: '主机'
          },
          {
            dataIndex: 'host_ip',
            key: 'host_ip',
            title: 'ip地址'
          }
        ]
      },
      tableColumnsRepo () {
        return [
          {
            dataIndex: 'host_name',
            key: 'host_name',
            title: '主机名称'
          },
          {
            dataIndex: 'host_ip',
            key: 'host_ip',
            title: 'ip地址'
          }
        ]
      },
      repoRowSelection () {
        return {
        selectedRowKeys: this.selectedRepoKeys,
        onChange: this.onRepoSelectChange
      }
      }
    },
    watch: {
    },
    methods: {
      jumpToPage () {
        clearTimeout(this.jumpModalInterval)
        this.jumpModalVisible = false
        this.$emit('createSuccess')
        this.$router.push(`/leaks/task/${this.taskType}/${this.jumpTaskId}`)
      },
      handleCancel () {
        this.$emit('close')
        // clear status
        this.visible = false
        this.cveList = []
        this.form.resetFields()
      },
      // 每次展开抽屉时触发，替代mounted
      handleOpen () {
        // inital defualt data
        this.visible = true
        this.cveList = this.cveListProps
        this.isResetChecked = true
        this.selectedRowKeyMaps = {}
        this.selectedRowsAllMaps = {}
        this.setDefaultInfo()
        // 设置repo任务时，直接使用传入的host数据
        if (this.taskType === 'repo') {
          this.selectedRepoKeys = this.hostList.map(host => host.host_id)
          this.selectedRepoRows = this.hostList
          return
        }

        const _this = this
        this.actionsIsLoading = true
        getActionUnderMultipleCVE({
          cveList: this.cveList.map(cve => cve.cve_id)
        }).then(function (res) {
          const cveMap = res.result || {}
          _this.addActionsToCVEData(cveMap)
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.actionsIsLoading = false
        })
        // 根据主机数据获取类型，自行或cve下的主机数据或者使用外部输入的主机数据更行talbe数据
        switch (this.hostListType) {
          case hostListTypes[0]:
            _this.hostUnderCveLoading = true
            getHostUnderMultipleCVE({
              cveList: this.cveList.map(cve => cve.cve_id)
            }).then(function (res) {
              // hostlists are contained in cveMap
              const cveMap = res.result || {}
              _this.addHostListToCVEData(cveMap)
            }).catch(function (err) {
              _this.$message.error(err.response.data.msg)
            }).finally(function () {
              _this.hostUnderCveLoading = false
            })
            break
          case hostListTypes[1]:
          case hostListTypes[2]:
            const tempObj2 = {}
            this.cveList.forEach(cve => {
              tempObj2[cve.cve_id] = this.hostList.map(host => {
                return {
                  host_id: host.host_id,
                  host_name: host.host_name,
                  host_ip: host.host_ip
                }
              })
            })
            this.addHostListToCVEData(tempObj2)
            break
        }
      },
      handleSubmit (excuteASAP = false) {
        const _this = this
        this.form.validateFields((err, values) => {
          if (!err) {
            if (!excuteASAP) {
              this.submitLoading = true
            } else {
              this.submitAndExecuteLoading = true
            }

            switch (this.taskType) {
              case 'cve':
                // prepare data
                const params = {
                  ...values,
                  auto_reboot: this.isResetChecked,
                  info: this.cveList.map(cveInfo => {
                    return {
                      cve_id: cveInfo.cve_id,
                      host_info: this.selectedRowsAllMaps[cveInfo.cve_id],
                      reboot: cveInfo.reboot
                    }
                  }).filter(item => item.host_info && item.host_info.length > 0)
                }
                // make request
                generateTask(params).then(function (res) {
                  _this.$message.success(res.msg)
                  if (excuteASAP) {
                    _this.handleExcuteASAP(res.task_id, res)
                  } else {
                    _this.visible = false
                    _this.handleGenerateSuccess(res, 'CVE修复', 'normal')
                  }
                }).catch(function (err) {
                  _this.$message.error(err.response.data.msg)
                }).finally(function () {
                  if (!excuteASAP) {
                    _this.submitLoading = false
                  }
                })
                break
              case 'repo':
                // prepare data
                const repoParams = {
                  ...values,
                  info: this.hostList.map(host => {
                    return {
                      host_id: host.host_id,
                      host_name: host.host_name,
                      host_ip: host.host_ip
                    }
                  })
                }
                // make request
                generateRepoTask(repoParams).then(function (res) {
                  _this.$message.success(res.msg)
                  if (excuteASAP) {
                    _this.handleExcuteASAP(res.task_id, res)
                  } else {
                    _this.visible = false
                    _this.handleGenerateSuccess(res, 'REPO设置', 'normal')
                  }
                }).catch(function (err) {
                  _this.$message.error(err.response.data.msg)
                }).finally(function () {
                  if (!excuteASAP) {
                    _this.submitLoading = false
                  }
                })
                break
            }
          }
        })
      },
      // 立即执行任务
      handleExcuteASAP (taskId, data) {
        const _this = this
        executeTask(taskId).then(function (res) {
          let text = ''
          switch (data.type) {
            case 'cve':
              text = 'CVE修复'
              break
            case 'repo':
              text = 'REPO设置'
              break
          }

          _this.visible = false
          _this.handleGenerateSuccess(data, text, 'asap')
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
          _this.submitAndExecuteLoading = false
        })
      },
      handleResetChanage (checked) {
        this.isResetChecked = checked
      },
      onSelectChange (selectedRowKeys, selectedRows, cid) {
        this.selectedRowKeyMaps[cid] = selectedRowKeys
        this.selectedRowsAllMaps[cid] = selectedRows
        this.selectedRowKeyMaps = Object.assign({}, this.selectedRowKeyMaps)
        this.selectedRowsAllMaps = Object.assign({}, this.selectedRowsAllMaps)
      },
      // 工具方法，将主机信息更新进cve数据中
      addHostListToCVEData (cveMap) {
        this.cveList.forEach(cveInfo => {
          const hostListUnderCve = cveMap[cveInfo.cve_id]
          cveInfo.hostsList = hostListUnderCve || []

          if (hostListUnderCve && hostListUnderCve.length > 0) {
            this.selectedRowKeyMaps[cveInfo.cve_id] = hostListUnderCve.map(host => host.host_id)
            this.selectedRowsAllMaps[cveInfo.cve_id] = hostListUnderCve
          } else {
            this.selectedRowKeyMaps[cveInfo.cve_id] = []
            this.selectedRowsAllMaps[cveInfo.cve_id] = []
          }
        })
        // forced refresh
        this.cveList = Object.assign([], this.cveList)
      },
      addActionsToCVEData (cveMap) {
        const tempArr = this.cveList.map(cveInfo => {
          const actionsUnderCve = cveMap[cveInfo.cve_id] || {}
          const infoTemp = {
            ...cveInfo,
            ...actionsUnderCve
          }
          return infoTemp
        })
        this.cveList = tempArr
      },
      // repo
      onRepoSelectChange (selectedRowKeys, selectedRows) {
        this.selectedRepoKeys = selectedRowKeys
        this.selectedRepoRows = selectedRows
      },
      // 当创建任务成功或执行任务成功后，弹窗提示用户是否跳转
      handleGenerateSuccess (res, type, modalType) {
        const _this = this
        this.jumpTaskId = res.task_id
        this.jumpModalVisible = true
        let text = ''
        switch (modalType) {
          case 'normal':
            text = `${type}任务创建成功`
            break
          case 'asap':
            text = `${type}任务创建成功，正在执行中...`
            break
        }
        this.jumpModalTitle = text
        this.countDown = 5
        this.jumpModalInterval = setInterval(function () {
          _this.countDown = _this.countDown - 1
          if (_this.countDown === 0) {
            clearTimeout(_this.jumpModalInterval)
            _this.jumpModalClose()
          }
        }, 1000)
      },
      jumpModalClose () {
        clearTimeout(this.jumpModalInterval)
        this.jumpModalVisible = false
        this.$emit('createSuccess')
      },
      // 自动填写任务信息
      setDefaultInfo () {
        this.taskNameDefault = `${this.taskType === 'cve' ? 'CVE修复任务' : 'REPO设置任务'}`
        switch (this.taskType) {
          case 'cve':
            this.taskDescDefault = `修复以下${this.cveListProps.length}个CVE：${this.cveListProps.map(cve => cve.cve_id).join('、')}`
            break
          case 'repo':
            this.taskDescDefault = `为以下${this.hostList.length}个主机设置Repo：${this.hostList.map(host => host.host_name).join('、')}`
            break
        }
        if (this.taskDescDefault.length > 60) {
          this.taskDescDefault = this.taskDescDefault.slice(0, 60) + '...'
        }
      }
    }
}
</script>
