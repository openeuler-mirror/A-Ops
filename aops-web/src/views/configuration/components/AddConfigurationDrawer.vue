<template>
  <div>
    <div @click="showModal" v-if="!isEdit">
      <slot name="button">
        <a-button type="primary">新增配置</a-button>
      </slot>
    </div>
    <a-drawer
      :title="isEdit ? '编辑配置' : '新增配置'"
      :width="720"
      :visible="isEdit ? visibleControl : visible"
      :body-style="{ paddingBottom: '80px' }"
      @close="handleCancel"
    >
      <a-form
        :form="form"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 18 }"
      >
        <a-form-item label="所属业务域">
          <a-input
            disabled
            v-decorator="['domainName', { initialValue: domainName }]"
          />
        </a-form-item>
        <div class="conf-form-item" v-for="(key, index) in formList" :key="key">
          <span v-if="!isEdit">
            <a-icon
              class="dynamic-delete-button"
              type="minus-circle-o"
              @click="removeConfForm(index)"
              v-if="formList.length > 1"
            />
            新增配置{{ index+1 }}
          </span>
          <a-form-item label="配置路径">
            <a-input
              v-decorator="[
                `confFiles[${key}].filePath`,
                { rules: [{ required: true, message: '请输入配置路径' }] }
              ]"
              placeholder="请输入配置路径"
              :disabled="isEdit"
            />
          </a-form-item>
          <a-form-item>
            <span slot="label">
              <a-tooltip title="配置来源二选一，推荐使用手动输入">
                <a-icon type="question-circle-o" />
              </a-tooltip>
              &nbsp;配置来源
            </span>
            <a-select
              :value="formSelections[key]"
              placeholder="请选择来源"
              @change="(value) => {
                formSelectionChange(key, value)
              }"
            >
              <a-select-option value="manuel">手动输入</a-select-option>
              <a-select-option value="auto">从主机导入</a-select-option>
            </a-select>
          </a-form-item>
          <a-form-item label="配置内容" v-if="formSelections[key]==='manuel'">
            <a-textarea
              placeholder="请输入配置内容"
              :rows="8"
              v-decorator="[
                `confFiles[${key}].contents`,
                { rules: [{ required: true, message: '请输入内容' }] }
              ]"
            />
          </a-form-item>
          <a-form-item label="选择主机" v-else-if="formSelections[key]==='auto'">
            <a-select
              placeholder="请选择文件所在主机"
              v-decorator="[
                `confFiles[${key}].hostId`,
                { rules: [{ required: true, message: '请选择主机' }] }
              ]"
            >
              <a-spin v-if="hostListLoading" slot="notFoundContent" size="small" />
              <a-select-option
                v-for="host in hostList"
                :value="host.hostId"
                :key="host.hostId"
              >
                {{ host.ip }}
              </a-select-option>
            </a-select>
          </a-form-item>
        </div>
      </a-form>
      <a-button type="dashed" style="width: 100%" @click="addConfForm()" v-if="!isEdit">
        <a-icon type="plus" /> 新增配置
      </a-button>
      <div class="areaButton">
        <a-button :style="{ marginRight: '8px' }" @click="handleCancel">取消</a-button>
        <a-button type="primary" @click="handleOk" :loading="submitIsLoading">确定</a-button>
      </div>
    </a-drawer>
  </div>
</template>

<script>
import { addManagementConf } from '@/api/management'
 import { domainHostList } from '@/api/configuration'
// 弹窗添加主机组
export default {
  name: 'AddConfigurationDrawer',
  props: {
    isEdit: {
      type: Boolean,
      default: false
    },
    showButton: {
      type: Boolean,
      default: true
    },
    visibleControl: {
      // only use when porps.isEdit = true
      type: Boolean,
      default: false
    },
    domainName: {
      type: String,
      default: ''
    },
    editFilePath: {
      type: String,
      default: undefined
    },
    onSuccess: {
      type: Function,
      default: null
    }
  },
  data () {
    return {
      visible: false,
      isLoading: false,
      hostListLoading: false,
      hostList: [],
      form: this.$form.createForm(this, { name: 'addConfigs' }),
      formKey: 0,
      formList: [0],
      formSelections: { 0: 'manuel' },
      submitIsLoading: false
    }
  },
  watch: {
    visibleControl: function () {
      const _this = this
      if (this.isEdit && this.visibleControl === true) {
        this.getHostList()
        this.resetData()
        setTimeout(function () {
          _this.form.setFieldsValue({ confFiles: [{ filePath: _this.editFilePath }] })
        }, 100)
      }
    }
  },
  methods: {
    addConfForm () {
      this.formKey += 1
      this.formList.push(this.formKey)
      this.formSelections[this.formKey] = 'manuel'
    },
    removeConfForm (idx) {
      const listTemp = this.formList
      listTemp.splice(idx, 1)
      this.formList = listTemp
    },
    formSelectionChange (key, value) {
      const temp = this.formSelections
      temp[key] = value
      this.formSelections = Object.assign({}, temp)
    },
    resetData () {
      this.form.resetFields()
      this.formKey = 0
      this.formList = [0]
      this.formSelections = { 0: 'manuel' }
    },
    showModal () {
      this.resetData()
      this.getHostList()
      this.visible = true
    },
    handleCancel () {
      this.visible = false
      this.$emit('cancel')
    },
    handleOk () {
      const _this = this
      this.form.validateFields((err, values) => {
        if (!err) {
          console.log(values)
          const params = {
            domainName: _this.domainName,
            confFiles: values.confFiles
            .filter(conf => conf)
          }
          this.submitIsLoading = true
          addManagementConf(params).then(function (res) {
            _this.$message.success(res.msg)
            _this.visible = false
            _this.$emit('ok')
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg || err.response.data.detail)
          }).finally(function () { _this.submitIsLoading = false })
        }
      })
    },
    getHostList () {
      const _this = this
      this.hostListLoading = true
      domainHostList(this.domainName)
      .then(function (res) {
        _this.hostList = res
        }).catch(function (err) {
          if (err.response.data.code !== 400) {
          _this.$message.error(err.response.data.msg || err.response.data.detail)
        } else {
          _this.hostList = []
        }
      }).finally(function () { _this.hostListLoading = false })
    }
  }
}
</script>

<style lang="less" scoped>
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
