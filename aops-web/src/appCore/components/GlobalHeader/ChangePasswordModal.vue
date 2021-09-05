<template>
  <span>
    <slot name="button">
      <a-button type="primary">修改密码</a-button>
    </slot>
    <a-modal
      title="修改用户密码"
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
        <a-form-item label="新密码">
          <a-input-password
            placeholder="请输入新密码"
            v-decorator="['password', { rules: [{ required: true, message: '请输入新密码' }] }]"
          >
          </a-input-password>
        </a-form-item>
      </a-form>
    </a-modal>
  </span>
</template>

<script>
import { changePassword } from '@/api/login'
// 修改用户密码
export default {
    name: 'ChangePasswordModal',
    props: {
        visible: {
          type: Boolean,
          default: false
        }
    },
    data () {
        return {
            isLoading: false,
            form: this.$form.createForm(this, { name: 'changePW' })
        }
    },
    watch: {
      visible () {
        this.form.resetFields()
      }
    },
    methods: {
        handleCancel () {
            this.$emit('close')
        },
        handleOk () {
            this.form.validateFields((err, values) => {
                if (!err) {
                    const _this = this
                    this.isLoading = true
                    changePassword(values)
                    .then(function () {
                        _this.$message.success('修改成功')
                        _this.form.resetFields()
                        _this.$emit('close')
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
