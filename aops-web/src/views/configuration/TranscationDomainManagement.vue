
<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <div>
        <h3 class="card-title">业务域列表</h3>
        <span>共有业务域{{ domainData.length }}个</span>
      </div>
      <div>
        <a-list :loading="domainLoading" :data-source="cardListData" :grid="{ gutter: 24, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }" >
          <a-list-item slot="renderItem" slot-scope="domain, index">
            <a-card :bodyStyle="{ padding: 0 }" :bordered="false" :class="index !== 0 ? 'aops-theme-incard' : ''">
              <div class="aops-card-body">
                <router-link :to="`${domain.domainName || ''}`">
                  <div class="aops-card-content">
                    <h3>{{ `业务域 ${domain.domainName}` }}</h3>
                  </div>
                </router-link>
                <div class="aops-card-bottom">
                  <a-row type="flex" justify="space-between">
                    <a-col>priority</a-col>
                    <a-col>
                      <router-link :to="`/configuration/transcation-domain-configurations/${domain.domainName}`">查看域内配置</router-link>
                      <a-divider type="vertical" />
                      <a-dropdown>
                        <a class="ant-dropdown-link" @click="e => e.preventDefault()">
                          更多 <a-icon type="down" />
                        </a>
                        <a-menu slot="overlay">
                          <a-menu-item>
                            <a href="javascript:;" @click="showAddHostDrawer(domain.domainName)">添加主机</a>
                          </a-menu-item>
                          <a-menu-item>
                            <a href="javascript:;" @click="delDomain(domain.domainName)">删除</a>
                          </a-menu-item>
                        </a-menu>
                      </a-dropdown>
                    </a-col>
                  </a-row>
                </div>
              </div>
              <add-transcation-domain-modal :onSuccess="handleAddSuccess" v-if="index === 0" />
            </a-card>
          </a-list-item>
        </a-list>
        <a-row type="flex" justify="center" v-show="showNumber < domainData.length + 1">
          <a-col><a-button @click="showMore">加载更多</a-button></a-col>
        </a-row>
      </div>
    </a-card>
    <drawer-view title="添加主机" ref="addHostDrawer" :bodyStyle="{ paddingBottom: '80px' }">
      <template slot="drawerView">
        <add-host-drawer :domainName="domainName"></add-host-drawer>
      </template>
    </drawer-view>
  </page-header-wrapper>
</template>

<script>
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import { i18nRender } from '@/vendor/ant-design-pro/locales'

import DrawerView from '@/views/utils/DrawerView'
import AddHostDrawer from './components/AddHostDrawer'
import AddTranscationDomainModal from './components/AddTranscationDomainModal'

import { domainList, deleteDomain } from '@/api/configuration'

export default {
    name: 'TranscationDomainManagement',
    components: {
      PageHeaderWrapper,
      DrawerView,
      AddHostDrawer,
      AddTranscationDomainModal
    },
    data () {
        return {
          domainData: [],
          showNumber: 6,
          domainLoading: false,
          domainName: ''
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
      cardListData () {
        if (this.domainData.length > 0) {
          return [{}].concat(this.domainData).slice(0, this.showNumber)
        } else {
          return [{}]
        }
      }
    },
    methods: {
      getDomainList () {
        const _this = this
        this.domainLoading = true
        domainList().then(function (res) {
          // 特殊处理
          _this.domainData = res || []
        }).catch(function (err) {
          if (err.response.data.code === 400) return
          _this.$message.error(err.response.data.msg)
        }).finally(function () { _this.domainLoading = false })
      },
      showAddHostDrawer (domainName) {
        this.$refs.addHostDrawer.open(domainName)
      },
      handleAddSuccess () {
        // 添加完成后，清空table设置，刷新列表
        this.getDomainList()
      },
      showMore () {
        this.showNumber += 6
      },
      delDomain (domainName) {
        const _this = this
        this.$confirm({
            title: (<div><p>你确定要删除这个业务域吗？</p></div>),
            content: (<span>删除后业务域无法恢复</span>),
            icon: () => <a-icon type="exclamation-circle" />,
              okType: 'danger',
              okText: '删除',
              onOk: function () { return _this.handleDelDomain(domainName) },
            onCancel () {}
          })
      },
      handleDelDomain (domainName) {
        const domainNameArray = []
        domainNameArray.push(domainName)
        const _this = this
        return new Promise((resolve, reject) => {
          deleteDomain({
            domainNameArray
          }).then((res) => {
            _this.$message.success(res.msg)
            _this.getDomainList()
            resolve()
          })
            .catch((err) => {
              _this.$message.error(err.response.data.msg)
              reject(err)
            })
        })
      }
    },
    created: function () {
      this.getDomainList()
    }
}
</script>

<style lang="less" scoped>
.card-title {
  display: inline-block;
  margin-right: 10px;
}
.aops-card {
  &-content {
    padding: 12px;
    height: 100px;
  }
  &-bottom {
    padding: 12px;
    border-top: 1px solid #e8e8e8;
    font-size: 12px;
  }
}
</style>
