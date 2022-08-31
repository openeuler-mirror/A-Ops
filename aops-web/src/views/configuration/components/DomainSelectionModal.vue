<template>
  <a-modal
    :maskClosable="false"
    :visible="showDomainSelection"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <a-form
      :form="form"
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="业务域" extra="若未选择业务域，则将返回管理页面">
        <a-select
          placeholder="请选择需要进行配置管理的业务域..."
          style="width: 200px"
          v-decorator="['domainName', { rules: [{ required: true, message: '请选择业务域' }] }]"
        >
          <a-select-option
            v-for="(item, index) in domainNameList"
            :key="index"
            :value="item.domainName"
          >
            {{ item.domainName }}
          </a-select-option>
        </a-select>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script>
import router from '@/vendor/ant-design-pro/router'
import { domainList } from '@/api/configuration'
// 弹窗添加主机组
export default {
  name: 'DomainSelectionModal',
  props: {
    showDomainSelection: {
      type: Boolean,
      default: false
    }
  },
  data () {
    return {
      domainNameList: [],
      isLoading: false,
      form: this.$form.createForm(this, { name: 'domainSelection' })
    }
  },
  methods: {
    handleOk () {
      const _this = this
      this.$emit('ok')
      this.form.validateFields((err, values) => {
        if (!err) {
          router.replace(`${values.domainName}`)
          _this.form.resetFields()
        }
      })
    },
    handleCancel () {
      this.$emit('cancel')
      this.form.resetFields()
    }
  },
  mounted: function () {
    const _this = this
    domainList().then(function (res) {
      _this.domainNameList = res
    }).catch(function (err) {
      _this.$message.error(err.response.data.msg)
    })
  }
}
</script>
