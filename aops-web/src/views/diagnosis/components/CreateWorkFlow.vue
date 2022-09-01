<template>
    <a-form :form="form" layout="vertical" hide-required-mark class="create-work-flow">
        <a-row :gutter="10">
            <a-col :span="28">
                <span class="ant-form-text">
                    应用名称：{{ appInfo.app_name }}
                </span>
                是否推荐:
                <a-switch
                  :disabled="true"
                  checked-children="开"
                  un-checked-children="关"
                  v-decorator="['recommmand',
                    { rules: [{ required: true, messip: '是否推荐' }]}
                  ]"
                />
                <a-form-item class="a-form-item">
                    工作流名称：
                    <a-input
                        placeholder="请输入工作流名称，50个字符以内"
                        v-decorator="['workflow_name',
                            { rules: [{ required: true, message: '请输入工作流名称' }, { validator: checkWorkflowName }]}
                        ]"
                    />
                </a-form-item>
            </a-col>
        </a-row>
        <a-row :gutter="6">
            <a-col :span="26">
                <a-form-item>
                    工作流描述：
                    <a-textarea
                        placeholder="请输入工作流描述，100个字符以内"
                        :rows="2"
                        v-decorator="[
                            'description',
                            { rules: [{ required: true, message: '请输入工作流描述' }, { validator: checkWorkflowDesc }]}
                        ]"
                    />
                </a-form-item>
            </a-col>
            <a-col :span="26">
                <a-form-item>
                    主机组：
                    <div class="selectHostGroup">
                        <a-select
                            v-decorator="['selectHostGroup',
                              {
                                rules: [{ required: true, message: '请选择主机组' }],
                                getValueFromEvent:(e)=> this.onSelectedChange(e)
                              }
                            ]"
                            show-search
                            placeholder="请输入主机组名进行搜索"
                            :filter-option="filterOption"
                        >
                            <a-spin slot="notFoundContent" size="small" />
                            <a-select-option v-for="item in selectedGroupList" :key="item" :value="item">
                                {{ item }}
                            </a-select-option>
                        </a-select>
                    </div>
                </a-form-item>
            </a-col>
        </a-row>
        <a-row>
            主机：
            <a-form-item class="selectHostFrom">
                <a-transfer
                    :titles="['待选择主机', '已选主机']"
                    :show-select-all="false"
                    :data-source="hostList"
                    :target-keys="targetKeys"
                    :selected-keys="transferSelectedKeys"
                    show-search
                    :filter-option="transferFilterOption"
                    @selectChange="handleSelectChange"
                    @change="handleTransferChange"
                >
                    <template
                        slot="children"
                        slot-scope="{
                          props: { direction, filteredItems, selectedKeys, disabled: listDisabled },
                          on: { itemSelectAll, itemSelect },
                        }"
                    >
                        <a-table
                            :row-selection="
                              getRowSelection({ disabled: listDisabled, selectedKeys, itemSelectAll, itemSelect })
                            "
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
            </a-form-item>
        </a-row>
    </a-form>
</template>
<script>
import Vue from 'vue'
import router from '@/vendor/ant-design-pro/router'
import { Transfer } from 'ant-design-vue'
import { hostGroupList, hostList } from '@/api/assest'
import { createWorkFlow } from '@/api/check'
import difference from 'lodash/difference';
Vue.use(Transfer)
const leftTableColumns = [
  {
    title: '主机名称',
    dataIndex: 'host_name'
  },
  {
    title: 'ip地址',
    dataIndex: 'public_ip'
  },
  {
    title: '场景',
    dataIndex: 'scene'
  }
];
const rightTableColumns = [
  {
    title: '主机名称',
    dataIndex: 'host_name'
  }
];
export default {
  name: 'CreateWorkFlow',
  inject: ['setButtons', 'close', 'showSpin', 'closeSpin'], // 来自祖辈们provide中声明的参数、方法
  props: {
    appInfo: {
      type: Object,
      default: () => {}
    }
  },
  data() {
    return {
      form: this.$form.createForm(this),
      selectedGroupList: [],
      hostGroup: [],
      selectOpen: false,
      SearchValue: '',
      // 穿梭框
      hostList: [],
      targetKeys: [],
      transferSelectedKeys: [],
      pagination: {
        current: 1,
        pageSize: 6,
        total: 0,
        showSizeChanger: true,
        showQuickJumper: true
      },
      leftColumns: leftTableColumns,
      rightColumns: rightTableColumns,
      transfer: null
    };
  },
  mounted() {
    this.setButtons({ callBack: this.create, text: '创建', type: 'primary' })
    this.getHostGroup()
    this.replaceTransferSearchPlaceHolder()
  },
  methods: {
    create() {
        const _this = this
        this.form.validateFields((err, values) => {
          if (!err) {
              if (_this.targetKeys.length < 1) {
                _this.$notification.info({
                  message: '没有添加主机',
                  description: '请添加主机后再提交创建'
                })
                return
              }
            _this.showSpin()
            createWorkFlow({
                workflow_name: values.workflow_name,
                description: values.description,
                app_name: this.appInfo.app_name,
                app_id: this.appInfo.app_id,
                input: {
                  domain: values.selectHostGroup,
                  hosts: _this.targetKeys
                }
            })
            .then(function (res) {
                _this.$message.success(res.msg)
                _this.closeSpin()
                _this.close()
                router.push('/diagnosis/workflow')
            }).catch(function (err) {
                _this.$message.error(err.response.data.msg)
            }).finally(function () {
                _this.closeSpin()
            })
          }
        })
    },
    getHostGroup () {
        const _this = this
        hostGroupList({
          tableInfo: {
            pagination: {},
            filters: {},
            sorter: {}
          }
        })
        .then(function (res) {
            _this.hostGroup = res.host_group_infos
            _this.hostGroup.forEach(element => {
                _this.selectedGroupList.push(element.host_group_name)
            });
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
    },
    onSelectedChange(value) {
        // reset selected host when change host group
        this.targetKeys = []
        const _this = this
        hostList({
          tableInfo: {
              pagination: {},
              filters: {
                host_group_name: [value]
              },
              sorter: {}
          }
        })
        .then(function (res) {
            _this.hostList = res.host_infos.map(host => {
              return {
                ...host,
                key: host.host_id
              }
            }) || []
            _this.pagination.total = res.total_count
            // 设置默认全选
            const tempArr = []
            _this.hostList.forEach(item => {
              tempArr.push(item.key)
            });
            _this.transferSelectedKeys = tempArr
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
        return value
    },
    filterOption(input, option) {
      return (
        option.componentOptions.children[0].text.toLowerCase().indexOf(input.toLowerCase()) >= 0
      );
    },
    // 穿梭框
    handleSelectChange (sourceSelectedKeys, targetSelectedKeys) {
      this.transferSelectedKeys = [...sourceSelectedKeys, ...targetSelectedKeys];
    },
    handleTransferChange(nextTargetKeys) {
      this.targetKeys = nextTargetKeys;
    },
    transferFilterOption(inputValue, option) {
      return option.host_name.indexOf(inputValue) > -1;
    },
    getRowSelection({ disabled, selectedKeys, itemSelectAll, itemSelect }) {
      return {
        getCheckboxProps: item => ({ props: { disabled: disabled || item.disabled } }),
        onSelectAll(selected, selectedRows) {
          const treeSelectedKeys = selectedRows
            .filter(item => !item.disabled)
            .map(({ key }) => key);
          const diffKeys = selected
            ? difference(treeSelectedKeys, selectedKeys)
            : difference(selectedKeys, treeSelectedKeys);
          itemSelectAll(diffKeys, selected);
        },
        onSelect({ key }, selected) {
          itemSelect(key, selected);
        },
        selectedRowKeys: selectedKeys
      };
    },
    replaceTransferSearchPlaceHolder() {
      document.getElementsByClassName('create-work-flow')[0]
        .getElementsByClassName('ant-transfer-list-search').forEach(item => {
        item.setAttribute('placeholder', '搜索主机名')
      })
    },
    checkWorkflowName (rule, value, cb) {
        if (value && value.length > 50) {
            /* eslint-disable */
            cb('长度不超过50个字符')
            /* eslint-enable */
            return
        }
        cb()
    },
    checkWorkflowDesc (rule, value, cb) {
        if (value && value.length > 100) {
            /* eslint-disable */
            cb('长度不超过100个字符')
            /* eslint-enable */
            return
        }
        cb()
    }
  }
};
</script>
<style lang="less" scoped>
.ant-form-text {
    padding-right: 130px;
}
.ant-input {
    width: 87%;
}
.selectHostGroup {
  width: 87%;
}
.ant-form-item {
    margin: 8px 0;
}
</style>
