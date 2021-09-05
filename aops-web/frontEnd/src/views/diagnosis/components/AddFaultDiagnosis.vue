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
          <!------
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
          -------->
          <a-transfer
            :data-source="hostListAll"
            :titles="['源主机列表', '目标列表']"
            :target-keys="targetKeys"
            :render="item => item.host_name"
            @change="handleTransferChange"
          />
        </a-form-item>
      </a-col>
    </a-row>
  </a-form>
</template>

<script>
 import Vue from 'vue'
import { Transfer } from 'ant-design-vue'
import { executeDiag } from '@/api/diagnosis'
import { hostList } from '@/api/assest'
Vue.use(Transfer)

  export default {
    name: 'AddFaultTree',
    inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        form: this.$form.createForm(this),
        selectedItems: [],
        dateFormat: 'YYYY/MM/DD HH:mm',
        hostListAll: [],
        targetKeys: []
      }
    },
    props: {
      faultTreeList: {
        type: Array,
        default: function () {
          return []
        }
      },
      saveSuccess: {
        type: Function,
        default: function () {}
      }
    },
    mounted: function () {
      this.setButtons({ callBack: this.save, text: '执行诊断', type: 'primary' })
      this.getHostListAll()
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
            if (this.targetKeys.length < 1) {
              that.$notification.info({
                message: '没有添加主机',
                description: '请添加主机后再提交'
              })
                return
            }
            that.showSpin()
            const data = {}
            data.host_list = that.targetKeys
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
              that.close()
              that.$notification.info({
                message: '执行诊断任务',
                description: '已执行诊断任务'
              })
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
      },
      getHostListAll () {
        const _this = this
        hostList({
          tableInfo: {
            pagination: {},
            filters: {},
            sorter: {}
          }
        }).then(function (res) {
          _this.hostListAll = res.host_infos.map(host => {
            return {
              ...host,
              key: host.host_id
            }
          }) || []
        }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.tableIsLoading = false })
      },
      handleTransferChange (nextTargetKeys) {
        this.targetKeys = nextTargetKeys
      }
    }
  }
</script>

<style lang="less" scoped>
</style>
