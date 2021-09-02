<template>
  <a-form :form="form" :label-col="{ span: 5 }" :wrapper-col="{ span: 12 }" :confirm-loading="isLoading" @submit="handleSubmit">
    <a-form-item label="归属业务域">
      <a-input
        :disabled="true"
        v-decorator="['domainName', { rules: [{ required: true, message: '请填写归属业务域!' }] }]"
      />
    </a-form-item>
    <a-form-item label="IP协议">
      <a-select
        v-decorator="[
          'ipv6',
          { rules: [{ required: true, message: '请选择IP协议!' }] },
        ]"
        placeholder="请选择"
      >
        <a-select-option value="IPv6">
          IPv6
        </a-select-option>
        <a-select-option value="IPv4">
          IPv4
        </a-select-option>
      </a-select>
    </a-form-item>
    <a-form-item label="IP">
      <a-input
        v-decorator="['ip', { rules: [{ required: true, message: '请填写IP!' }] }]"
      />
    </a-form-item>
    <a-form-item label="选择要添加的主机">
    </a-form-item>
    <div>
      <a-transfer
        :data-source="mockData"
        :target-keys="targetKeys"
        :show-search="showSearch"
        :filter-option="(inputValue, item) => item.hostId.indexOf(inputValue) !== -1"
        :show-select-all="false"
        @change="onChange"
      >
        <template
          slot="children"
          slot-scope="{
            props: { direction, filteredItems, selectedKeys, disabled: listDisabled },
            on: { itemSelectAll, itemSelect },
          }"
        >
          <a-table
            :pagination="false"
            :row-selection="getRowSelection({ disabled: listDisabled, selectedKeys, itemSelectAll, itemSelect })"
            :columns="direction === 'left' ? leftColumns : rightColumns"
            :data-source="filteredItems"
            size="small"
            :style="{ pointerEvents: listDisabled ? 'none' : null }"
            :custom-row="
              ({ key, disabled: itemDisabled }) => ({
                on: {
                  click: () => {
                    if (itemDisabled || listDisabled) return;
                    itemSelect(key, !selectedKeys.includes(key));
                  },
                },
              })
            "
          />
        </template>
      </a-transfer>
    </div>
  </a-form>
</template>

<script>
  import Vue from 'vue'
  import { Transfer } from 'ant-design-vue'
  import difference from 'lodash/difference'
  import { domainHostList, addHost } from '@/api/configuration'
  Vue.use(Transfer)
  const leftTableColumns = [
    {
      dataIndex: 'hostId',
      title: '主机名'
    },
    {
      dataIndex: 'ip',
      title: 'IP地址'
    }
  ]
  const rightTableColumns = [
    {
      dataIndex: 'hostId',
      title: '主机名'
    }
  ]
export default {
    name: 'AddHostDrawer',
    inject: ['setButtons', 'close', 'onload'], // 来自祖辈们provide中声明的参数、方法
    data () {
        return {
          form: this.$form.createForm(this),
          mockData: [],
          targetKeys: [],
          disabled: false,
          showSearch: true,
          leftColumns: leftTableColumns,
          rightColumns: rightTableColumns,
          domainName: '',
          isLoading: false
        }
    },
    computed: {
    },
    methods: {
      getHostList () {
        const _this = this
        domainHostList({
          uid: '123',
          domainName: _this.domainName
        }).then(function (res) {
          res.result.domainHostData.forEach(function (item) {
            _this.mockData.push({
              key: item.hostId,
              hostId: item.hostId,
              ip: item.ip
            })
          })
        }).catch(function (err) {
          _this.$message.error(err.response.data.message)
        }).finally(function () { _this.tableIsLoading = false })
      },
      handleSubmit (e) {
        const _this = this
        e.preventDefault()
        this.form.validateFields((err, values) => {
          if (!err) {
            console.log('Received values of form: ', values)
            console.log(_this.targetKeys)
            this.isLoading = true
            const hostInfos = []
            _this.targetKeys.forEach(function (hostId) {
              hostInfos.push({
                'ipv6': values.ipv6,
                'ip': values.ip,
                'hostId': hostId
              })
            })
            console.log(hostInfos)
            addHost(values.domainName, hostInfos)
              .then(function () {
                _this.$message.success('添加成功')
                _this.form.resetFields()
                _this.close()
              })
              .catch(function (err) {
                _this.$message.error(err.response.data.message)
              })
              .finally(function () {
                _this.isLoading = false
              })
          }
        })
      },
      onChange (nextTargetKeys) {
        this.targetKeys = nextTargetKeys
      },
      getRowSelection ({ disabled, selectedKeys, itemSelectAll, itemSelect }) {
        return {
          onSelectAll (selected, selectedRows) {
            const treeSelectedKeys = selectedRows
              .filter(item => !item.disabled)
              .map(({ key }) => key)
            const diffKeys = selected ? difference(treeSelectedKeys, selectedKeys) : difference(selectedKeys, treeSelectedKeys)
             itemSelectAll(diffKeys, selected)
          },
          onSelect ({ key }, selected) {
            itemSelect(key, selected)
          },
          selectedRowKeys: selectedKeys
        }
      }
    },
  mounted: function () {
    const that = this
    this.getHostList()
    this.onload(function (params) {
      that.domainName = params
      that.form.setFieldsValue({
        'domainName': that.domainName
      })
    })
    this.setButtons({ callBack: this.handleSubmit, text: '保存' })
  }
}
</script>
