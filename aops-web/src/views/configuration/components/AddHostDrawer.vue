<template>
  <a-form :form="form" :label-col="{ span: 5 }" :wrapper-col="{ span: 12 }" :confirm-loading="isLoading" @submit="handleSubmit">
    <a-form-item label="归属业务域">
      <a-input
        :disabled="true"
        v-decorator="['domainName', { rules: [{ required: true, message: '请填写归属业务域!' }] }]"
      />
    </a-form-item>
    <a-form-item label="选择要添加的主机">
    </a-form-item>
    <div>
      <a-transfer
        :rowKey="host => host.host_id"
        :data-source="hostListTransfer"
        :target-keys="targetKeys"
        :show-search="showSearch"
        :filter-option="(inputValue, item) => item.host_name.indexOf(inputValue) !== -1"
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
            :row-key="rowKey"
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
  import { hostList } from '@/api/assest'
  import { domainHostList, addHost } from '@/api/configuration'
  Vue.use(Transfer)
  const leftTableColumns = [
    {
      dataIndex: 'host_name',
      key: 'host_name',
      title: '主机名'
    },
    {
      dataIndex: 'public_ip',
      key: 'public_ip',
      title: 'IP地址'
    }
  ]
  const rightTableColumns = [
    {
      dataIndex: 'host_name',
      key: 'host_name',
      title: '主机名'
    }
  ]
export default {
    name: 'AddHostDrawer',
    inject: ['setButtons', 'close', 'onload'], // 来自祖辈们provide中声明的参数、方法
    data () {
        return {
          rowKey: 'host_id',
          form: this.$form.createForm(this),
          hostListAll: [],
          oldTargetKeys: [],
          targetKeys: [],
          showSearch: true,
          leftColumns: leftTableColumns,
          rightColumns: rightTableColumns,
          domainName: '',
          isLoading: false
        }
    },
    computed: {
      hostListTransfer () {
        return this.hostListAll.map(host => {
          const hostT = host
          if (this.oldTargetKeys.indexOf(host.host_id) !== -1) {
            hostT.disabled = true
          }
          return hostT
        })
      }
    },
    methods: {
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
      getHostInDomainList (domainName) {
        const _this = this
        domainHostList(domainName)
        .then(function (res) {
          _this.targetKeys = res.map(host => host.hostId)
          _this.oldTargetKeys = res.map(host => host.hostId)
        }).catch(function (err) {
          // code == 400时，为域内未添加主机，不报错
          if (err.response.data.code !== 400) {
            _this.$message.error(err.response.data.msg || err.response.data.detail)
          }
        }).finally(function () { _this.tableIsLoading = false })
      },
      handleSubmit (e) {
        const _this = this
        e.preventDefault()
        this.form.validateFields((err, values) => {
          if (!err) {
            this.isLoading = true
            const hostInfos = []
            const newTargetKeys = _this.targetKeys.filter(targetKey => _this.oldTargetKeys.indexOf(targetKey) === -1)
              if (newTargetKeys.length < 1) {
                _this.$notification.info({
                  message: '没有添加新的主机',
                  description: '请选择新的主机后再尝试提交'
              })
              return
            }
            newTargetKeys.forEach(function (hostId) {
              const matchedHost = _this.hostListAll.filter(host => host.host_id === hostId)[0] || {}
              hostInfos.push({
                // 只传hostId
                'hostId': hostId,
                'ipv6': 'ipv4',
                'ip': matchedHost.public_ip
              })
            })
            addHost(values.domainName, hostInfos)
              .then(function (res) {
                _this.$message.success(res.msg)
                _this.form.resetFields()
                _this.close()
                _this.$emit('addHostSuccess')
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
          getCheckboxProps: item => ({ props: { disabled: disabled || item.disabled } }),
          onSelectAll (selected, selectedRows) {
            const treeSelectedKeys = selectedRows
              .filter(item => !item.disabled)
              .map((row) => row.host_id)
            const diffKeys = selected ? difference(treeSelectedKeys, selectedKeys) : difference(selectedKeys, treeSelectedKeys)
             itemSelectAll(diffKeys, selected)
          },
          onSelect (row, selected) {
            itemSelect(row.host_id, selected)
          },
          selectedRowKeys: selectedKeys
        }
      }
    },
  mounted: function () {
    const that = this
    this.onload(function (params) {
      // 抽屉展开，进行初始化
      that.domainName = params
      that.targetKeys = []
      that.oldTargetKeys = []
      that.form.setFieldsValue({
        'domainName': that.domainName
      })
    })
    that.getHostInDomainList(that.domainName)
    that.getHostListAll()
    this.setButtons({ callBack: this.handleSubmit, text: '添加' })
  }
}
</script>
