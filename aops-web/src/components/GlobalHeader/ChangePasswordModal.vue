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
            v-decorator="['password', { rules: [{ required: true, message: '请输入新密码' }, { validator: passwordCheck }] }]"
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
        },
        passwordCheck (rule, value, cb) {
          if (/[^0-9a-zA-Z_~`!?,.:;\-'"(){}[\]/<>@#$%^&*+|\\=\s]/.test(value)) {
            /* eslint-disable */
            cb('只允许大小写字母、数字、空格和特殊字符')
            /* eslint-enable */
            return
          }
          if (value.length < 8 || value.length > 20) {
            /* eslint-disable */
            cb('长度应为8-20字符')
            /* eslint-enable */
            return
          }
          if (!(/[_~`!?,.:;\-'"(){}[\]/<>@#$%^&*+|\\=\s]/.test(value))) {
            /* eslint-disable */
            cb('至少应包含一个空格和特殊字符')
            /* eslint-enable */
            return
          }
          let count = 0
          if (/[a-z]/.test(value)) count += 1
          if (/[A-Z]/.test(value)) count += 1
          if (/[0-9]/.test(value)) count += 1
          if (count < 2) {
            /* eslint-disable */
            cb('至少包含大写字母、小写字母、数字中的两种')
            /* eslint-enable */
            return
          }
          cb()
        }
      }
}
</script>
