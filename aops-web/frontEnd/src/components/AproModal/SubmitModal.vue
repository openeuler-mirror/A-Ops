<template>
  <div>
    <a-button type="primary" @click="showModal">
      <slot name="buttonContent">
        提交
      </slot>
    </a-button>
    <a-modal
      :visible="visible"
      :confirm-loading="confirmLoading"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <slot name="modalContent">
        确认提交？
      </slot>
    </a-modal>
  </div>
</template>

<script>
import notification from 'ant-design-vue/es/notification'

export default {
  name: 'NormalModal',
  data () {
      return {
          visible: false,
          confirmLoading: false
      }
  },
  props: {
      // 此方法应返回一个promise对象，通常为异步请求调用后的promise对象.
      onOkPromise: {
          type: Function,
          required: true
      },
      // 请求成功外部处理函数
      onSuccess: {
          type: Function,
          default: null
      },
      // 请求失败外部处理函数
      onError: {
          type: Function,
          default: null
      }
  },
  methods: {
      showModal () {
          this.visible = true
      },
      handleOk () {
          this.confirmLoading = true
          this.onOkPromise()
          .then(res => {
              this.confirmLoading = false
              this.visible = false
              if (this.onSuccess) {
                this.onSuccess(res)
              } else {
                this.$message.success(res.message)
              }
          })
          .catch(err => {
              this.confirmLoading = false
              this.visible = false
              if (this.onError) {
                this.onError(err)
              } else {
                notification.error({
                  message: '错误',
                  description: err.response.data.message
                })
              }
          })
      },
      handleCancel () {
          this.visible = false
      }
  }
}
</script>
