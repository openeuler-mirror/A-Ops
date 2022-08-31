<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <div>
      <a-card :bordered="false" class="aops-theme">
        <a-form @submit="handleAddHost" :form="form" :label-col="{ span: 5 }" :wrapper-col="{ span: 10 }">
          <a-form-item label="主机名称">
            <a-input
              :maxLength="50"
              v-decorator="[
                'host_name',
                { rules: [
                  {required: true, message: '请输入主机名称' },
                  { validator: checkNameInput }
                ]}
              ]"
              placeholder="请输入主机名称,50个字符以内"
            >
              <a-tooltip slot="suffix" title="最大长度50个字符，由数字、小写字母、英文下划线_组成。以小写字母开头，且结尾不能是英文下划线_">
                <a-icon type="info-circle" style="color: rgba(0,0,0,.45)" />
              </a-tooltip>
            </a-input>
          </a-form-item>
          <a-form-item layout="inline" label="所属主机组">
            <a-row type="flex" :gutter="16">
              <a-col flex="5">
                <a-select
                  v-decorator="['host_group_name',{ rules: [{ required: true, message: '请选择所属主机组' }] }]"
                  placeholder="请选择"
                  :not-found-content="hostGroupIsLoading ? undefined : null"
                >
                  <a-spin v-if="hostGroupIsLoading" slot="notFoundContent" size="small" />
                  <a-select-option
                    v-for="hostGroup in hostGroupList"
                    :key="hostGroup.host_group_name"
                    :value="hostGroup.host_group_name"
                  >
                    {{ hostGroup.host_group_name }}
                  </a-select-option>
                </a-select>
              </a-col>
              <a-col flex="1">
                <add-host-group-modal :onSuccess="handleAddHostGroupSuccess">
                  <a-button type="primary" slot="button">
                    <a-icon type="plus" />添加主机组
                  </a-button>
                </add-host-group-modal>
              </a-col>
            </a-row>
          </a-form-item>
          <a-form-item label="IP地址">
            <a-input
              v-decorator="['public_ip',{ rules: [{ required: true,pattern:/^((2[0-4]\d|25[0-5]|[01]?\d\d?)\.){3}(2[0-4]\d|25[0-5]|[01]?\d\d?)$/,message: '请输入IP地址在 0.0.0.0~255.255.255.255 区间内' }] }]"
              placeholder="请输入有效ip地址，e.g. 192.168.0.1"/>
          </a-form-item>
          <a-form-item label="SSH登录端口">
            <a-input-number :min="0" :max="65535" v-decorator="['ssh_port', { initialValue: 22, rules: [{ required: true, message: '请输入 0~65535 内正整数' }] }]" placeholder="请输入"/>
          </a-form-item>
          <a-form-item label="管理/监控节点">
            <a-radio-group name="managementGroup" v-decorator="['management', { initialValue: true }]">
              <a-radio :value="true">管理节点</a-radio>
              <a-radio :value="false">监控节点</a-radio>
            </a-radio-group>
          </a-form-item>
          <a-form-item label="主机用户名">
            <a-input v-decorator="['username', { rules: [{ required: true, message: '请输入主机用户名' }, { validator: checkHostUserName }] }]" placeholder="请输入主机用户名，16个字符以内" :maxLength="16">
              <a-tooltip slot="suffix" title="登录主机时使用的用户名">
                <a-icon type="info-circle" style="color: rgba(0,0,0,.45)" />
              </a-tooltip>
            </a-input>
          </a-form-item>
          <a-form-item label="主机登录密码">
            <a-input-password v-decorator="['password', { rules: [{ required: true, message: '请输入主机登录密码' }, { validator: passwordCheck }] }]" placeholder="请设置登录密码，长度8-20个字符"></a-input-password>
          </a-form-item>
          <a-form-item label="主机sudo密码">
            <a-input-password v-decorator="['sudo_password', { rules: [{ required: true, message: '请输入主机sudo密码' }, { validator: passwordCheck }] }]" placeholder="请设置sudo密码，长度8-20个字符"/>
          </a-form-item>
          <a-form-item label="加密密钥">
            <a-input-password v-decorator="['key', { rules: [{ required: true, message: '请输入加密密钥' }, { validator: passwordCheck }] }]" placeholder="请设置用于给主机私密信息加密的密钥，长度8-20个字符"/>
          </a-form-item>
          <a-form-item :wrapper-col="{ span: 10, offset: 5 }">
            <a-button @click="handleCancel">取消</a-button>
            <a-button v-if="pageType==='create'" htmlType="submit" type="primary" :loading="submitLoading" style="margin-left: 8px" >添加</a-button>
            <a-button v-if="pageType==='edit'" htmlType="submit" type="primary" :loading="submitLoading" style="margin-left: 8px" >修改</a-button>
          </a-form-item>
        </a-form>
      </a-card>
    </div>
  </page-header-wrapper>
</template>

<script>
// 创建和编辑共用一个组件
import store from '@/store'
import { mapState } from 'vuex'
import router from '@/vendor/ant-design-pro/router'
import { i18nRender } from '@/vendor/ant-design-pro/locales'

import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import AddHostGroupModal from './components/AddHostGroupModal'

import { hostGroupList, addHost } from '@/api/assest'

export default {
    name: 'HostEdition',
    components: {
        PageHeaderWrapper,
        AddHostGroupModal
    },
    data () {
        return {
          pageType: 'edit',
          hostGroupList: [],
          hostGroupIsLoading: false,
          form: this.$form.createForm(this),
          submitLoading: false
        }
    },
    computed: {
        // 自定义面包屑内容
        breadcrumb () {
            const routes = this.$route.meta.diyBreadcrumb.map((route) => {
                return {
                    path: route.path,
                    breadcrumbName: i18nRender(route.breadcrumbName)
                }
            })
            return {
                props: {
                    routes,
                    itemRender: ({ route, params, routes, paths, h }) => {
                        if (routes.indexOf(route) === routes.length - 1) {
                            return <span>{route.breadcrumbName}</span>
                        } else {
                            return <router-link to={route.path}>{route.breadcrumbName}</router-link>
                        }
                    }
                }
            }
        },
        ...mapState({
          hostInfo: state => state.host.hostInfo
        })
    },
    created () {
        // 判断是新建页面还是编辑页面
        if (this.$route.path.indexOf('edit') > -1) {
            this.pageType = 'edit'
            if (!this.hostInfo.host_id) {
              router.go(-1)
            }
            this.hostId = this.$route.params.hostId
        } else {
            this.pageType = 'create'
        }
    },
    methods: {
      // 获取主机组列表数据
      getHostGroupList () {
        const _this = this
        this.hostGroupIsLoading = true
        hostGroupList({
          tableInfo: {
                  pagination: {},
                  filters: {},
                  sorter: {}
              }
        }).then(function (res) {
          _this.hostGroupList = res.host_group_infos
        }).catch(function (err) {
          _this.$message.error(err.response.msg)
        }).finally(function () { _this.hostGroupIsLoading = false })
      },
      handleAddHost (e) {
        var _this = this
        e.preventDefault()
        this.form.validateFields((err, values) => {
          if (!err) {
            this.submitLoading = true
            // 后需调整：修改时传host_id, 新建时传host_name
            if (this.pageType === 'edit') {
              values.host_id = this.hostInfo.host_id
            }
            addHost(values).then(function (res) {
              _this.$message.success(res.msg)
              store.dispatch('resetHostInfo')
              router.push('/assests/hosts-management')
            }).catch(function (err) {
              _this.$message.error(err.response.data.msg)
            }).finally(function () { _this.submitLoading = false })
          }
        })
      },
      handleAddHostGroupSuccess () {
        // 添加完成后，刷新主机组列表
        this.getHostGroupList()
      },
      handleCancel () {
        store.dispatch('resetHostInfo')
        router.go(-1)
      },
      checkNameInput (rule, value, cb) {
        if (/[^0-9a-z_.]/.test(value)) {
          /* eslint-disable */
          cb('只能输入数字、小写字母和英文.和_')
          /* eslint-enable */
          return
        }
        if (/[_]$/.test(value)) {
          /* eslint-disable */
          cb('结尾不能是英文下划线')
          /* eslint-enable */
          return
        }
        cb()
      },
      checkHostUserName (rule, value, cb) {
        if (/[^0-9a-zA-Z_\-~`!?.;(){}[\]@#$^*+|=]/.test(value)) {
          /* eslint-disable */
          cb('用户名为数字、英文字母或特殊字符组成，不能包含空格和以下特殊字符：:<>&,\'"\\/%。')
          /* eslint-enable */
          return
        }
        if (/[<>\\]/.test(value)) {
          /* eslint-disable */
          cb('用户名为数字、英文字母或特殊字符组成，不能包含空格和以下特殊字符：:<>&,\'"\\/%。')
          /* eslint-enable */
          return
        }
        if (/^[#+-]/.test(value)) {
          /* eslint-disable */
          cb('首字符不能是“#”、“+”或“-”')
          /* eslint-enable */
          return
        }
        cb()
      },
      passwordCheck (rule, value, cb) {
        if (/[^0-9a-zA-Z_~`!?.:;\-'"(){}[\]/<>@#$%^&*+|\\=]/.test(value)) {
          /* eslint-disable */
          cb('只允许大小写字母、数字和特殊字符，不能有空格和逗号')
          /* eslint-enable */
          return
        }
        if (value && (value.length < 8 || value.length > 20)) {
          /* eslint-disable */
          cb('长度应为8-20字符')
          /* eslint-enable */
          return
        }
        if (!(/[_~`!?.:;\-'"(){}[\]/<>@#$%^&*+|\\=]/.test(value))) {
          /* eslint-disable */
          cb('请至少应包含一个特殊字符')
          /* eslint-enable */
          return
        }
        let count = 0
        if (/[a-z]/.test(value)) count += 1
        if (/[A-Z]/.test(value)) count += 1
        if (/[0-9]/.test(value)) count += 1
        if (count < 2) {
          /* eslint-disable */
          cb('至少包含大写字母、小写字母、数字中的两种')
          /* eslint-enable */
          return
        }
        cb()
      }
    },
    mounted: function () {
        this.getHostGroupList()
        if (this.pageType === 'edit') {
          this.form.setFieldsValue({
            host_name: this.hostInfo.host_name,
            host_group_id: this.hostInfo.host_group_id,
            public_ip: this.hostInfo.public_ip,
            ssh_port: this.hostInfo.ssh_port,
            management: (this.hostInfo.management || '').toLowerCase() === 'true' || false
          })
        }
    }
}
</script>
