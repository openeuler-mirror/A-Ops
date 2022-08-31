<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <h3 class="card-title">
        主机列表
        <a-icon
          :type="expandedStatus[0] ? 'caret-up' : 'caret-down'"
          @click="setExpandStatus(0, !expandedStatus[0])"
        />
      </h3>
      <host-table
        standalone
        v-show="expandedStatus[0]"
        :repoListProps="repoList"
      />
    </a-card>
    <a-card :bordered="false" class="aops-theme" style="margin-top: 20px">
      <h3>
        CVE REPO
        <a-icon
          :type="expandedStatus[1] ? 'caret-up' : 'caret-down'"
          @click="setExpandStatus(1, !expandedStatus[1])"
        />
      </h3>
      <div class="host-leaks-repo-list" v-show="expandedStatus[1]">
        <a-list :loading="repoLoading" :data-source="repoListData" :grid="{ gutter: 24, xl: 3, lg: 3, md: 2, sm: 1, xs: 1 }" >
          <a-list-item slot="renderItem" slot-scope="repo, index">
            <a-card :bodyStyle="{ padding: 0 }" :bordered="false" :class="index !== 0 ? 'aops-theme-incard' : ''">
              <div class="aops-card-body">
                <div class="aops-card-content" @click="checkRepoOpen(repo)">
                  <h3>{{ repo.repo_name }}</h3>
                </div>
                <div class="aops-card-bottom">
                  <a-row type="flex" justify="space-between">
                    <a-col>{{ repo.repo_attr }}</a-col>
                    <a-col>
                      <a @click="handleDeleteRepo(repo)">删除</a>
                      <a-divider type="vertical" />
                      <a-dropdown>
                        <a class="ant-dropdown-link" @click="e => e.preventDefault()">
                          更多 <a-icon type="down" />
                        </a>
                        <a-menu slot="overlay">
                          <a-menu-item key="1" disabled>
                            导出
                          </a-menu-item>
                          <a-menu-item key="2" disabled>
                            编辑
                          </a-menu-item>
                        </a-menu>
                      </a-dropdown>
                    </a-col>
                  </a-row>
                </div>
              </div>
              <add-repo-modal @addSuccess="handleAddSuccess" v-if="index === 0" />
            </a-card>
          </a-list-item>
        </a-list>
        <a-row type="flex" justify="center" v-show="showNumber < repoList.length + 1">
          <a-col><a-button @click="showMore">加载更多</a-button></a-col>
        </a-row>
        <check-repo-modal :visible="checkRepoVisible" :detailProps="checkRepo" @close="checkRepoClose" />
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
/****************
/* 主机列表页面
****************/

import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import HostTable from './components/HostTable'
import AddRepoModal from './components/AddRepoModal'
import CheckRepoModal from './components/CheckRepoModal.vue'

import { getRepoList, deleteRepo } from '@/api/leaks'

export default {
  name: 'HostLeakList',
  components: {
    PageHeaderWrapper,
    HostTable,
    AddRepoModal,
    CheckRepoModal
  },
  data () {
    return {
      expandedStatus: [true, true],
      repoList: [],
      repoLoading: false,
      // 首屏显示repo的数量
      showNumber: 6,
      // 查看repo数据弹窗控制
      checkRepo: {},
      checkRepoVisible: false
    }
  },
  computed: {
    repoListData () {
      if (this.repoList.length > 0) {
        return [{}].concat(this.repoList).slice(0, this.showNumber)
      } else {
        return [{}]
      }
    },
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
  methods: {
    setExpandStatus (idx, isExpaned) {
      const newStatuses = Object.assign({}, this.expandedStatus)
      newStatuses[idx] = isExpaned
      this.expandedStatus = newStatuses
    },
    showMore () {
      this.showNumber += 6
    },
    handleAddSuccess () {
      this.getRepoList()
    },
    getRepoList () {
      const _this = this
      this.repoLoading = true
      getRepoList().then(function (res) {
        _this.repoList = res.result || []
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.repoLoading = false
      })
    },
    exportRepo () {

    },
    handleDeleteRepo (repo) {
      const _this = this
      this.$confirm({
        content: () => `确认删除REPO：${repo.repo_name} 么?`,
        icon: () => <a-icon type="exclamation-circle" />,
        okType: 'danger',
        okText: '删除',
        onOk: function () {
          return deleteRepo({
            repoNameList: [repo.repo.name]
          }).then(function (res) {
            _this.$message.success(res.msg)
            _this.getRepoList()
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          })
        },
        onCancel () {}
      })
    },
    checkRepoOpen (repo) {
      this.checkRepo = repo
      this.checkRepoVisible = true
    },
    checkRepoClose () {
      this.checkRepoVisible = false
    }
  },
  mounted: function () {
    this.getRepoList()
  }
}
</script>

<style lang="less" scoped>
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
.aops-theme-incard {
  cursor: pointer;
}
</style>
