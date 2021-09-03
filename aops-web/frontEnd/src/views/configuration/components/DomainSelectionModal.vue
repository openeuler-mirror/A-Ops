<template>
  <a-modal
    :visible="showDomainSelection"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <a-form
      :form="form"
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 16 }"
    >
      <a-form-item label="业务域">
        <a-select
          placeholder="请选择需要进行配置管理的业务域..."
          style="width: 200px"
          v-decorator="['domainName', { rules: [{ required: true, message: '请输入名称' }] }]"
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
import router from '@/router'
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
        console.log(values)
        if (!err) {
          router.replace(`transcation-domain-configurations/${values.domainName}`)
          _this.form.resetFields()
        }
      })
    },
    handleCancel () {
      router.push('transcation-domain-management')
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
