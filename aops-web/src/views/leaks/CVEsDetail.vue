<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <a-spin :spinning="infoLoading">
        <div class="detail-info-content">
          <a-row type="flex">
            <a-col :span="8">
              <h1>{{ detail.cve_id }}</h1>
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="8">
              {{ `发布时间： ${detail.publish_time || ''}` }}
            </a-col>
            <a-col :span="8">
              严重性:
              <span :style="`color: ${severityColorMap[detail.severity]}`">{{ severityMap[detail.severity] || '' }}</span>
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="8">
              {{ `CVSS 3.0 评分： ${detail.cvss_score || ''}` }}
            </a-col>
            <a-col :span="8">
              {{ `状态： ${statusMap[detail.status] || ''}` }}
              <a-dropdown :trigger="['click']">
                <a-icon type="edit" class="edit-icon"/>
                <a-menu slot="overlay">
                  <a-menu-item key="0">
                    <a @click="setStatus(statusMenuList[0].value)">{{ statusMenuList[0].text }}</a>
                  </a-menu-item>
                  <a-menu-item key="1">
                    <a @click="setStatus(statusMenuList[1].value)">{{ statusMenuList[1].text }}</a>
                  </a-menu-item>
                  <a-menu-item key="2">
                    <a @click="setStatus(statusMenuList[2].value)">{{ statusMenuList[2].text }}</a>
                  </a-menu-item>
                  <a-menu-item key="3">
                    <a @click="setStatus(statusMenuList[3].value)">{{ statusMenuList[3].text }}</a>
                  </a-menu-item>
                  <a-menu-item key="4">
                    <a @click="setStatus(statusMenuList[4].value)">{{ statusMenuList[4].text }}</a>
                  </a-menu-item>
                </a-menu>
              </a-dropdown>
            </a-col>
          </a-row>
          <a-row type="flex">
            <a-col :span="8">
              {{ `修复软件包： ${detail.package || ''}` }}
            </a-col>
            <a-col :span="8">
              关联CVE：
              <span v-if="detail.related_cve && detail.related_cve.length" ><a @click="relatedCveDrawerOpen">{{ detail.related_cve && detail.related_cve.length }}</a>个</span>
              <span v-else>无</span>
              <a-drawer
                title="关联CVE"
                :visible="relatedCveDrawerVisble"
                @close="relatedCveDrawerClose"
                width="400"
              >
                <table class="drawer-cve-table">
                  <tr v-for="(cve, index) in detail.related_cve" :key="index">
                    <td>{{ index + 1 }}</td>
                    <td>
                      <a @click="jumpToAnotherCVE(cve)">{{ cve }}</a>
                    </td>
                  </tr>
                </table>
              </a-drawer>
            </a-col>
          </a-row>
          <h4>cve描述：</h4>
          <p class="detail-description">{{ detail.description }}</p>
        </div>
      </a-spin>
    </a-card>
    <a-card :bordered="false" class="aops-theme">
      <h1>受影响主机</h1>
      <host-table
        :cveList="[detail]"
        :inputList="hostList"
        :inputLoading="hostIsLoading"
        @getTableData="getHostData"
        :paginationTotal="paginationTotal"
      />
    </a-card>
  </page-header-wrapper>
</template>

<script>
/****************
/* cve 详情页
****************/

import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import HostTable from './components/HostTable'

import { statusList, statusMap, severityMap, severityColorMap } from './config'
import { getCveInfo, getHostUnderCVE, setCveStatus } from '@/api/leaks'

export default {
  name: 'CVEsDetail',
  components: {
    PageHeaderWrapper,
    HostTable
  },
  computed: {
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
              return <span>{this.cve_id}</span>
            } else {
              return <router-link to={route.path}>{route.breadcrumbName}</router-link>
            }
          }
        }
      }
    }
  },
  data () {
    return {
      cve_id: this.$route.params.cve_id,
      detail: {},
      infoLoading: false,
      // 传给子组件的数据最大数量
      paginationTotal: undefined,
      // 装给子组件的cve下host数据
      hostList: [],
      hostIsLoading: false,
      // 设置状态loadiing
      setStatusLoading: false,
      statusMenuList: statusList,

      relatedCveDrawerVisble: false,
      // 数据展示映射
      statusMap,
      severityMap,
      severityColorMap
    }
  },
  methods: {
    getDetail () {
      const _this = this
      this.infoLoading = true
      getCveInfo({
        cve_id: this.cve_id
      }).then(function (res) {
        _this.detail = res.result || {}
      }).finally(function () {
        _this.infoLoading = false
      })
    },
    getHostData (data) {
      this.getHostList(this.cve_id, data)
    },
    getHostList (cveId, data) {
      const _this = this
      this.hostIsLoading = true
      getHostUnderCVE({
        ...data,
        cve_id: cveId
      }).then(function (res) {
        _this.hostList = res.result || []
        _this.paginationTotal = res.total_count || (res.total_count === 0 ? 0 : undefined)
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.hostIsLoading = false
      })
    },
    setStatus (status) {
      const _this = this
      this.setStatusLoading = true
      setCveStatus({
        cveList: [this.cve_id],
        status
      }).then(function (res) {
        _this.$message.success(res.msg)
        _this.getDetail()
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.setStatusLoading = false
      })
    },
    relatedCveDrawerOpen () {
      this.relatedCveDrawerVisble = true
    },
    relatedCveDrawerClose () {
      this.relatedCveDrawerVisble = false
    },
    jumpToAnotherCVE (cve) {
      const _this = this
      this.$router.push(cve)
      this.$router.push('/leaks/cves-management')
      setTimeout(function () {
        _this.$router.go(-1)
      }, 100)
    }
  },
  mounted: function () {
    this.getDetail()
  }
}
</script>

<style lang="less" scoped>
.detail-info-content {
  padding: 12px 12px 12px 50px;
  h1 {
    margin-bottom: 0;
  }
  .ant-row-flex {
    margin-bottom: 24px;
  }

  .edit-icon {
    &:hover {
      color: #3265F2;
      cursor: pointer;
    }
  }
  .detail-description {
    word-break: break-word;
  }
}
.drawer-cve-table {
  border: 1px solid #ccc;
  width: 100%;
  td {
    border: 1px solid #ccc;
    padding: 6px;
  }
}

</style>
