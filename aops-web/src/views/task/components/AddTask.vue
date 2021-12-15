<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="任务名称">
          <a-input placeholder="请输入任务名称，不超过50个字符" v-decorator="['task_name',{rules: [{ required: true, message: '请输入任务名称' },{ max: 50, message: '任务名称不能超过50个字符' },{ validator: checkTaskName }]}]" />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="所用playbook">
          <a-select
            v-decorator="['template_name',{rules: [{required: true,message: '请选择playbook'}]}]"
            mode="multiple"
            placeholder="请选择playbook"
            style="width: 100%"
            @change="handleChange">
            <a-spin v-if="templateListIsLoading" slot="notFoundContent" size="small" />
            <a-select-option v-for="item in filteredOptions" :key="item" :value="item">
              {{ item }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="任务描述">
          <a-textarea
            v-decorator="['description',{rules: [{ required: true, message: '请输入该配置任务的描述' }, { validator: checkTaskdesc }]}]"
            :rows="4"
            placeholder="请输入该配置任务的描述, 100字以内"
          />
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
import { getTemplateList, generateTask } from '@/api/task'

  export default {
    name: 'AddTask',
    inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        form: this.$form.createForm(this),
        selectedItems: [],
        templateList: [],
        templateListIsLoading: false
      }
    },
    props: {
      saveSuccess: {
        type: Function,
        default: null
      }
    },
    mounted: function () {
      this.getTemplateList()
      this.setButtons({ callBack: this.save, text: '生成', type: 'primary' })
    },
    computed: {
      filteredOptions () {
        const OPTIONS = []
        this.templateList.forEach(function (item) {
          if (item.template_name !== '') {
            OPTIONS.push(item.template_name)
          }
        })
        return OPTIONS.filter(o => !this.selectedItems.includes(o))
      }
    },
    methods: {
      // 获取列表数据
      getTemplateList () {
        const _this = this
        this.templateListIsLoading = true

        getTemplateList({})
          .then(function (res) {
            _this.templateList = res.template_infos
          }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.templateListIsLoading = false })
      },
      save () {
        const _this = this
        this.form.validateFields((err, values) => {
          if (!err) {
            _this.showSpin()
            generateTask({
              ...values
            }).then(function (res) {
              _this.$message.success(res.msg)
              _this.close()
              _this.saveSuccess()
            }).catch(function (err) {
              _this.$message.error(err.response.data.msg)
            }).finally(function () {
              _this.closeSpin()
            })
          }
        })
      },
      handleChange (selectedItems) {
        this.selectedItems = selectedItems
        this.form.setFieldsValue({ 'template_name': selectedItems })
      },
      checkTaskName (rule, value, cb) {
          if (/[^0-9a-z_]/.test(value)) {
            /* eslint-disable */
            cb('名称应由数字、小写字母、英文下划线组成')
            /* eslint-enable */
            return
          }
          if (/^[^a-z]/.test(value)) {
            /* eslint-disable */
            cb('以小写字母开头，且结尾不能是英文下划线')
            /* eslint-enable */
            return
          }
          if (/[_]$/.test(value)) {
            /* eslint-disable */
            cb('以小写字母开头，且结尾不能是英文下划线')
            /* eslint-enable */
            return
          }
          cb()
        },
        checkTaskdesc (rule, value, cb) {
          if (value && value.length > 100) {
            /* eslint-disable */
            cb('长度不超过100个字符')
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
