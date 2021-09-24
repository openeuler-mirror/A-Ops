<template>
  <div class="aops-add-domain" @click="showModal">
    <a-icon type="plus"/>
    <a-modal
      :visible="visible"
      title="创建业务域"
      :confirm-loading="isLoading"
      @cancel="handleCancel"
      @ok="handleOk"
    >
      <a-form
        :form="form"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 16 }"
      >
        <a-form-item label="业务域名称">
          <a-input
            :maxLength="50"
            placeholder="请输入"
            v-decorator="['domain_name', { rules: [{ required: true, message: '请输入名称' }] }]"
          />
        </a-form-item>
        <a-form-item label="优先级">
          <a-input disabled placeholder="未开放设置" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
import { addDomain } from '@/api/configuration'
// 添加业务域弹窗
export default {
    name: 'AddDomainModal',
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
          form: this.$form.createForm(this, { name: 'addDomain' })
        }
    },
    methods: {
      showModal () {
        this.form.resetFields()
        this.visible = true
      },
      handleOk () {
        this.form.validateFields((err, values) => {
          if (!err) {
            const _this = this
            this.isLoading = true
            addDomain(values)
            .then(function (res) {
                _this.$message.success(res.msg)
                _this.onSuccess && _this.onSuccess()
                _this.visible = false
                _this.form.resetFields()
            })
            .catch(function (err) {
                _this.$message.error(err.response.data.message)
            })
            .finally(function () {
                _this.isLoading = false
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
