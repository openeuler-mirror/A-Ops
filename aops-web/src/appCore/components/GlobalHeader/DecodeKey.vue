<template>
  <span>
    <slot name="button">
      <a-button type="primary">解密密钥</a-button>
    </slot>
    <a-modal
      title="输入解密密钥"
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
        <a-form-item label="解密密钥">
          <a-input-password
            placeholder="请输入密钥"
            v-decorator="['key', { rules: [{ required: true, message: '请输入密钥' }] }]"
          >
          </a-input-password>
        </a-form-item>
      </a-form>
    </a-modal>
  </span>
</template>

<script>
import { certificateKey } from '@/api/login'
// 输入解密密码
export default {
    name: 'DecodeKey',
    props: {
        visible: {
          type: Boolean,
          default: false
        }
    },
    data () {
        return {
            isLoading: false,
            form: this.$form.createForm(this, { name: 'decodeKey' })
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
                    certificateKey(values)
                    .then(function () {
                        _this.$message.success('输入成功')
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
