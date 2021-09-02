<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="故障树名称">
          <a-input placeholder="请输入故障树名称，不超过20个字符" v-decorator="['tree_name',{trigger:'blur',rules: [{ required: true, message: '请输入故障树名称' },{ max: 20, message: '故障树名称不能超过20个字符' }]}]" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="导入故障树文件">
          <a-upload
            name="file"
            :multiple="true"
            action="https://www.mocky.io/v2/5cc8019d300000980a055e76"
            v-decorator="['tree_content']"
          >
            <a-button> <a-icon type="upload" />上传文件</a-button>
          </a-upload>
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="故障树描述">
          <a-textarea
            v-decorator="['description',{rules: [{ required: true, message: '请输入故障树描述' },{ max: 100, message: '故障树描述不能超过100个字符' }]}]"
            :rows="4"
            placeholder="请输入故障树描述，不超过100个字符"
          />
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
import { importDiagTree } from '@/api/diagnosis'

  export default {
    name: 'AddFaultTree',
    inject: ['setButtons', 'close'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        appId: 'app' + (new Date().getTime()),
        form: this.$form.createForm(this)
      }
    },
    props: {
      saveSuccess: Function
    },
    mounted: function () {
      this.setButtons({ callBack: this.save, text: '保存' })
    },
    methods: {
      save () {
        const that = this
        this.form.validateFields((err, values) => {
          if (!err) { // 如果验证通过，err为null，否则有验证失败信息
            importDiagTree({ ...values, uid: '123' }).then(function (res) {
              that.$message.success(res.message)
              that.close()
              that.saveSuccess()
            }).catch(function (err) {
              console.log(err)
              that.$message.error(err.response.data.message)
            }).finally(function () {
            })
          }
        })
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
