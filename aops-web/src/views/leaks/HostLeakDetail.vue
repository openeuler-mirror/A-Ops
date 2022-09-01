<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <a-spin :spinning="infoLoading">
        <div class="detail-info-content">
          <h1>{{ detail.host_name }}</h1>
          <a-row type="flex">
            <a-col span="8">
              <p>{{ `主机组： ${detail.host_group || ''}` }}</p>
            </a-col>
            <a-col span="8">
              <p>{{ `IP： ${detail.host_ip || ''}` }}</p>
            </a-col>
            <a-col span="8">
              <p>{{ `上次扫描： ${detail.last_scan && dateFormat('YYYY-mm-dd HH:MM:SS', detail.last_scan * 1000) || ''}` }}</p>
            </a-col>
            <a-col span="8">
              <p>{{ `CVE REPO： ${detail.repo || ''}` }}</p>
            </a-col>
            <a-col span="8">
              <p>{{ `CVE 数量： ${detail.cve_num}` }}</p>
            </a-col>
            <a-col span="8">
              <a-button type="primary" @click="sacnHost" :loading="scanloading || scanStatus === 'scanning'">
                {{ scanStatus === 'scanning' ? '扫描中' : '漏洞扫描' }}
              </a-button>
            </a-col>
          </a-row>
        </div>
      </a-spin>
    </a-card>
    <a-card :bordered="false" class="aops-theme">
      <h1>CVEs</h1>
      <cves-table
        :inputList="cveList"
        :inputLoading="cveIsLoading"
        :hostList="[detail]"
        @statusUpdated="handleStatusUpdated"
        @getTableData="getCveData"
        :paginationTotal="paginationTotal"
        @getCveAll="getCveAllList"
        :cveAllIsLoadingProp="cveAllIsLoading"
        :cveAllListProp="cveAllList"
      />
    </a-card>
  </page-header-wrapper>
</template>

<script>
/****************
/* 主机详情页面
****************/

import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import CvesTable from './components/CvesTable'

import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { dateFormat } from '@/views/utils/Utils'
import { getHostInfo, getCveUnderHost, scanHost, getHostScanStatus } from '@/api/leaks'
import configs from '@/config/defaultSettings'

export default {
  name: 'HostLeakDetail',
  components: {
    PageHeaderWrapper,
    CvesTable
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
            // 若为路由diyBreadcrumb数组的最后一个元素，替换标题文本为其对应的主机名称
            if (routes.indexOf(route) === routes.length - 1) {
              return <span>{this.detail.host_name}</span>
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
      host_id: this.$route.params.host_id,
      detail: {},
      infoLoading: false,
      // 需要传给子组件的数据
      cveList: [],
      cveIsLoading: false,
      paginationTotal: undefined,

      cveAllList: [],
      cveAllIsLoading: false,
      // 主机扫描状态数据
      scanloading: false,
      scanStatusloading: false,
      scanStatus: '',
      getScanStatusTimeout: null
    }
  },
  methods: {
    dateFormat,
    getDetail () {
      const _this = this
      this.infoLoading = true
      getHostInfo({
        host_id: this.host_id
      }).then(function (res) {
        const resultObj = res.result || {}
        resultObj.host_id = _this.host_id
        _this.detail = resultObj
        // _this.getCVEList(res.info && res.info.cveList)
      }).finally(function () {
        _this.infoLoading = false
      })
    },
    getCveData (data) {
      this.getCVEList(this.host_id, data)
    },
    getCVEList (hostId, data) {
      const _this = this
      this.cveIsLoading = true
      getCveUnderHost({
        ...data,
        host_id: hostId
      }).then(function (res) {
        _this.cveList = res.result
        _this.paginationTotal = res.total_count || (res.total_count === 0 ? 0 : undefined)
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.cveIsLoading = false
      })
    },
    getCveAllList (data) {
      const _this = this
      this.cveAllIsLoading = true
      getCveUnderHost({
        ...data,
        host_id: this.host_id
      }).then(function (res) {
        _this.cveAllList = res.result
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.cveAllIsLoading = false
      })
    },
    handleStatusUpdated (data) {
      this.getCVEList(this.host_id, data)
    },
    sacnHost () {
      const _this = this
      this.scanloading = true
      scanHost({
        hostList: [_this.host_id]
      }).then(function (res) {
        _this.$message.success(res.msg)
        _this.scanStatus = 'scanning'
        _this.getScanStatue()
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.scanloading = false
      })
    },
    // 轮训查询当前主机的扫描状态
    getScanStatue () {
      const _this = this
      this.scanStatusloading = true
      clearTimeout(this.getScanStatusTimeout)
      getHostScanStatus({
        hostList: [_this.host_id]
      }).then(function (res) {
        _this.scanStatus = res.result[_this.host_id]
        if (_this.scanStatus === 'scanning') {
          _this.getScanStatusTimeout = setTimeout(function () {
            _this.getScanStatue()
          }, configs.scanProgressInterval)
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.scanStatusloading = false
      })
    }
  },
  mounted: function () {
    this.getDetail()
    this.getScanStatue()
  }
}
</script>

<style lang="less" scoped>
.detail-info-content{
  h1 {
    font-size: 24px;
    font-weight: bold;
    color: rgba(0,0,0,.65);
  }
  padding: 12px 12px 12px 24px;
}
.scan-text {
  margin-left: 6px;
  font-size: 14px;
}
</style>
