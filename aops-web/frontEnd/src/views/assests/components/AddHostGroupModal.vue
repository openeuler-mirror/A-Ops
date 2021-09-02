<template>
  <div>
    <div @click="showModal">
      <slot name="button">
        <a-button type="primary">添加主机组</a-button>
      </slot>
    </div>
    <a-modal
      title="添加主机组"
      :visible="visible"
      :confirm-loading="isLoading"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <a-form
        :form="form"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="主机组名称">
          <a-input
            :maxLength="50"
            placeholder="请输入"
            v-decorator="['name', { rules: [{ required: true, message: '请输入名称' }] }]"
          >
            <a-tooltip slot="suffix" title="最大长度50个字符，由数字、小写字母、英文下划线_组成。以小写字母开头，且结尾不能是英文下划线_">
              <a-icon type="info-circle" style="color: rgba(0,0,0,.45)" />
            </a-tooltip>
          </a-input>
        </a-form-item>
        <a-form-item label="主机组描述">
          <a-textarea
            placeholder="请输入描述"
            :rows="4"
            v-decorator="['description', { rules: [{ required: true, message: '请输人描述' }] }]"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { addHostGroup } from '@/api/assest'
// 弹窗添加主机组
export default {
    name: 'AddHostGroupModal',
    props: {
        onSuccess: {
          type: Function,
          default: null
        }
    },
    data () {
        return {
            visible: false,
            isLoading: false,
            form: this.$form.createForm(this, { name: 'addHostGroup' })
        }
    },
    methods: {
        showModal () {
            this.form.resetFields()
            this.visible = true
        },
        handleCancel () {
            this.visible = false
        },
        handleOk () {
            this.form.validateFields((err, values) => {
                if (!err) {
                    const _this = this
                    this.isLoading = true
                    console.log('Received values of form: ', values)
                    addHostGroup(values)
                    .then(function () {
                        _this.$message.success('添加成功')
                        _this.onSuccess && _this.onSuccess()
                        _this.visible = false
                        _this.form.resetFields()
                    })
                    .catch(function (err) {
                        _this.$message.error(err.response.data.msg)
                    })
                    .finally(function () {
                        _this.isLoading = false
                    })
                }
            })
        }
    }
}
</script>
