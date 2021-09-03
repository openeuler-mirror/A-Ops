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
            show-time
            format="YYYY-MM-DD HH:mm:ss"
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
            show-time
            format="YYYY-MM-DD HH:mm:ss"
          />
        </a-form-item>
      </a-col>
    </a-row>
    <a-row :gutter="16">
      <a-col :span="24">
        <a-form-item label="区间间隔">
          <a-input
            v-decorator="['interval', { rules: [{ required: true, message: '请输入区间间隔(单位：秒),只能输入数字!',pattern: new RegExp(/^[1-9]\d*$/, 'g') }] }]"
            placeholder="请输入区间间隔(单位：秒)"
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
    inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        form: this.$form.createForm(this),
        selectedItems: [],
        dateFormat: 'YYYY/MM/DD HH:mm'
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
        // 数组第一项为空(父页面用于放置新增故障树按钮)
        return this.faultTreeList.slice(1).map(item => item.tree_name).filter(o => !this.selectedItems.includes(o))
      }
    },
    methods: {
      save () {
        const that = this
        this.form.validateFields((err, values) => {
          if (!err) {
            that.showSpin()
            const data = {}
            data.host_list = []
            values.host_list.split(',').forEach(function (host) {
              data.host_list.push(host)
            })
            data.time_range = []
            data.time_range.push(that.getUnixTime(values['startTime'].format('YYYY-MM-DD HH:mm:ss')))
            data.time_range.push(that.getUnixTime(values['endTime'].format('YYYY-MM-DD HH:mm:ss')))
            data.tree_list = that.selectedItems
            data.interval = parseInt(values.interval)
            executeDiag(data).then(function (res) {
              that.$message.success(res.msg)
              that.closeSpin()
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
      getUnixTime (dateStr) {
        const newStr = dateStr.replace(/-/g, '/')
        const date = new Date(newStr)
        return date.getTime()
      },
      handleChange (selectedItems) {
        this.selectedItems = selectedItems
        this.form.setFieldsValue({ 'tree_list': selectedItems })
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
