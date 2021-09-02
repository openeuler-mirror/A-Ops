<template>
  <a-form :form="form" layout="vertical" hide-required-mark>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="起始日期">
          <a-date-picker
            v-decorator="[
                  'startTime',
                  {
                    rules: [{ required: true, message: '请选择起始日期' }],
                  },
                ]"
            style="width: 100%"
            :get-popup-container="trigger => trigger.parentNode"
          />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="结束日期">
          <a-date-picker
            v-decorator="[
                  'endTime',
                  {
                    rules: [{ required: true, message: '请选择结束日期' }],
                  },
                ]"
            style="width: 100%"
            :get-popup-container="trigger => trigger.parentNode"
          />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="所用故障树">
          <a-select
            v-decorator="['tree_list',{rules: [{required: true,message: '请选择故障树'}]}]"
            mode="multiple"
            placeholder="请选择故障树"
            style="width: 100%"
            @change="handleChange">
            <a-select-option v-for="item in filteredOptions" :key="item" :value="item">
              {{ item }}
            </a-select-option>
          </a-select>
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="所需诊断主机">
          <a-textarea
            v-decorator="[
                  'host_list',
                  {
                    rules: [{ required: true, message: '请输入需要诊断的主机，主机间用;号隔开' }],
                  },
                ]"
            :rows="4"
            placeholder="请输入需要诊断的主机，主机间用;号隔开"
          />
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
import { executeDiag } from '@/api/diagnosis'

  export default {
    name: 'AddFaultTree',
    inject: ['setButtons', 'close'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        form: this.$form.createForm(this),
        selectedItems: []
      }
    },
    props: {
      faultTreeList: Array,
      saveSuccess: Function
    },
    mounted: function () {
      this.setButtons({ callBack: this.save, text: '保存' })
    },
    computed: {
      filteredOptions () {
        const OPTIONS = []
        this.faultTreeList.forEach(function (item) {
          if (item.tree_name !== '') {
            OPTIONS.push(item.tree_name)
          }
        })
        return OPTIONS.filter(o => !this.selectedItems.includes(o))
      }
    },
    methods: {
      save () {
        const that = this
        this.form.validateFields((err, values) => {
          if (!err) {
            console.log('Received values of form: ', values)
            const data = {}
            data.host_list = []
            data.time_range = []
            data.tree_list = []
            data.access_token = []
            executeDiag({
              uid: '123',
              data
            }).then(function (res) {
              that.$message.success(res.message)
              that.close()
              that.saveSuccess()
            }).catch(function (err) {
              that.$message.error(err.response.data.message)
            }).finally(function () {
            })
          }
        })
      },
      handleChange (selectedItems) {
        this.selectedItems = selectedItems
        this.form.setFieldsValue({ 'tree_list': selectedItems })
        console.log(selectedItems)
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
