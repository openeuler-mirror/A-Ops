<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="playbook名称">
          <a-input placeholder="请输入playbook名称，不超过64个字符" v-decorator="['template_name',{rules: [{ required: true, message: '请输入playbook名称' },{ max: 64, message: 'playbook名称不能超过64个字符' }, { validator: checkTemplateName}]}]" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="导入playbook文件">
          <uploader
            toJSON
            uid="treeUploader"
            fileType="yaml"
            v-decorator="['template_content',{rules: [{ required: true, message: '请上传YAML类型文件，并确保格式符合要求' }]}]"
          />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="playbook描述">
          <a-textarea
            v-decorator="['description',{rules: [{ required: true, message: '请输入playbook描述' },{ max: 256, message: 'playbook描述不能超过256个字符' }, { validator: checkTemplatedesc }]}]"
            :rows="4"
            placeholder="请输入playbook描述，不超过256个字符"
          />
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
  /* eslint-disable */
import { imporTemplate } from '@/api/task'
import Uploader from '@/components/Uploader'

  export default {
    name: 'AddTemplate',
    inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
    components: {
      Uploader
    },
    data () {
      return {
        appId: 'app' + (new Date().getTime()),
        form: this.$form.createForm(this)
      }
    },
    props: {
      saveSuccess: {
        type: Function,
        default: null
      }
    },
    mounted: function () {
      this.setButtons({ callBack: this.save, text: '新增', type: 'primary' })
    },
    methods: {
      save () {
        const that = this
        this.form.validateFields((err, values) => {
          if (!err) { // 如果验证通过，err为null，否则有验证失败信息
            that.showSpin()
            imporTemplate({
              ...values
            }).then(function (res) {
              that.$message.success(res.msg)
              that.close()
              that.saveSuccess()
            }).catch(function (err) {
              that.$message.error(err.response.data.msg)
            }).finally(function () {
              that.closeSpin()
            })
          }
        })
      },
      checkTemplateName (rule, value, cb) {
        if (value && value.length > 64) {
          /* eslint-disable */
          cb('长度不超过64个字符')
          /* eslint-enable */
          return
        }
        if (/[<>]/.test(value)) {
          /* eslint-disable */
          cb('不能有><符号')
          /* eslint-enable */
          return
        }
        cb()
      },
      checkTemplatedesc (rule, value, cb) {
        if (value && value.length > 256) {
          /* eslint-disable */
          cb('长度不超过256个字符')
          /* eslint-enable */
          return
        }
        if (/[<>]/.test(value)) {
          /* eslint-disable */
          cb('不能有><符号')
          /* eslint-enable */
          return
        }
        cb()
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
