<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="故障树名称">
          <a-input placeholder="请输入故障树名称，不超过20个字符" v-decorator="['tree_name',{rules: [{ required: true, message: '请输入故障树名称' },{ max: 20, message: '故障树名称不能超过20个字符' }]}]" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="导入故障树文件">
          <uploader
            toJSON
            uid="treeUploader"
            fileType="json"
            v-decorator="['tree_content',{rules: [{ required: true, message: '请上传文件JSON类型文件，并确保格式符合要求' }]}]"
          />
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
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="故障树样例">
          <pre style="margin: 0;padding-top: 15px;border: 1px solid #ccc;background: #f5f5f5">
            {
              "node name":"重启类故障树",
              "value":null,
              "condition":"硬件问题 || 软件问题 || 内核问题",
              "description":"",
              "advice":"",
              "children": [
                {
                  "node name":"硬件问题",
                  "value":null,
                  "condition":"硬件问题1 &amp;&amp; 硬件问题2",
                  "description":"出现硬件问题",
                  "advice":"ccc ddd",
                  "children": [...]
                },
                ...
              ]
            }
          </pre>
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
// this component is abandoned
/* eslint-disable */
import { importDiagTree } from '@/api/diagnosis'
import Uploader from '@/components/Uploader'

  export default {
    name: 'AddFaultTree',
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
            importDiagTree({ ...values }).then(function (res) {
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
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
