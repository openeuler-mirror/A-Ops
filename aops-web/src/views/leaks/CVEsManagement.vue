<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <div>
        <cves-table
        standalone
         />
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
/****************
/* cve列表页
****************/

import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import CvesTable from './components/CvesTable'

export default {
  name: 'CVEsManagement',
  components: {
    PageHeaderWrapper,
    CvesTable
  },
  computed: {
    // 自定义面包屑
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
            return <router-link to={route.path}>{route.breadcrumbName}</router-link>
          }
        }
      }
    }
  },
  data () {
    return {
    }
  },
  methods: {
  },
  mounted: function () {
  }
}
</script>

<style lang="less" scoped>
</style>
