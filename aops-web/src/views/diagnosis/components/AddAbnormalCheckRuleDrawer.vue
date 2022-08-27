<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-form-item label="导入异常检测规则文件：">
      <div style="border: 1px solid #ccc;border-radius: 3px;display: inline-block;cursor: pointer">
        <uploader hidefocus toJSON uid="luleUploader" fileType="json" v-decorator="['ruleList',{rules: [{ required: true, message: '请上传符合json格式的文件' }]}]" />
      </div>
      <div style="padding-left: 15px;color: #999;display: inline-block">支持文件扩展名：<span style="border-bottom: 1px solid;padding: 0 2px">.json</span> ...</div>
    </a-form-item>
    <div style="line-height: 28px;color: #000">规则样例：</div>
    <pre style="margin: 0;padding-top: 15px;border: 1px solid #ccc;background: #f5f5f5">
      {
        "check_items": [{
          "check_item": "check_item1",
          "data_list": [{
              "name": "node_cpu_seconds_total",
              "type": "kpi",
              "label": {
                "cpu": "1",
                "mode": "irq"
              }
          }],
          "condition": "$0>1",
          "plugin": "",
          "description": "aaa"
        },...]
      }
    </pre>
  </a-form>
</template>

<script>
// this component is abandoned
  import { importRule } from '@/api/check'
  import Uploader from '@/components/Uploader'
  // import {importDiagTree} from "@/api/diagnosis";

  export default {
    name: 'AddAbnormalCheckRuleDrawer',
    components: { Uploader },
    inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
    props: {
      addSuccess: {
        type: Function,
        default: function () {}
      }
    },
    data () {
      return {
        ruleList: [],
        form: this.$form.createForm(this),
        tags: [],
        inputVisible: false,
        inputValue: ''
      }
    },
    mounted: function () {
      this.setButtons({ callBack: this.handleSubmit, text: '保存' })
    },
    methods: {
      handleSubmit () {
        var that = this
        this.form.validateFields((err, values) => {
          if (!err) { // 如果验证通过，err为null，否则有验证失败信息
            const checkItems = values.ruleList ? values.ruleList.check_items : null
            that.showSpin()
            importRule(checkItems).then(function (data) {
              let msg = ''
              if (data.succeed_list && data.succeed_list.length > 0) {
                msg += '成功添加' + data.succeed_list.length + '条规则！'
              }
              if (data.update_list && data.update_list.length > 0) {
                msg += '成功更新' + data.update_list.length + '条规则！'
              }
              if (data.fail_list && data.fail_list.length > 0) {
                msg += '另有' + data.fail_list.length + '条规则添加失败！'
              }
              that.$message.success(msg)
              that.addSuccess()
            }).catch(function (err) {
              that.$message.error(err.response.data.msg)
            }).finally(function () {
              that.closeSpin()
              that.close()
            })
          }
        })
      }
    }
  }
</script>
<style>

  .dynamic-delete-button {
    cursor: pointer;
    position: relative;
    top: 4px;
    font-size: 24px;
    color: #999;
    transition: all 0.3s;
  }
  .dynamic-delete-button:hover {
    color: #777;
  }
  .dynamic-delete-button[disabled] {
    cursor: not-allowed;
    opacity: 0.5;
  }
  #luleUploader{padding: 2px;outline:none}
</style>
