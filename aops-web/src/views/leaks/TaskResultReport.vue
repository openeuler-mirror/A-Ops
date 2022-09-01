<template>
  <page-header-wrapper :breadcrumb="breadcrumb">
    <a-card :bordered="false" class="aops-theme">
      <div>
        <a-spin :spinning="resultLoading">
          <div class="result-content">
            <a-descriptions :column="{ sm: 1 }">
              <a-descriptions-item label="任务类型">
                {{ resultData.task_type }}
              </a-descriptions-item>
              <a-descriptions-item label="上次执行时间">
                {{ resultData.latest_execute_time && dateFormat('YYYY-mm-dd HH:MM:SS', resultData.latest_execute_time * 1000) }}
              </a-descriptions-item>
            </a-descriptions>
            <p class="reuslt-item-title">任务结果: </p>
            <a-collapse defaultActiveKey="0">
              <a-collapse-panel
                v-for="(resultItem, riidx) in resultData.task_result"
                :key="riidx"
                :header="`主机: ${resultItem.host_name}`"
              >
                <a-descriptions :column="{ sm: 1 }">
                  <a-descriptions-item label="主机地址">
                    {{ resultItem.host_ip }}
                  </a-descriptions-item>
                  <a-descriptions-item label="状态" v-if="resultData.task_type === 'cve'">
                    {{ cveStatusTextMap[resultItem.status] }}
                  </a-descriptions-item>
                  <a-descriptions-item label="状态" v-if="resultData.task_type === 'repo'">
                    {{ repoStatusTextMap[resultItem.status] }}
                  </a-descriptions-item>
                  <a-descriptions-item label="REPO" v-if="taskType === 'repo'">
                    {{ resultItem.repo }}
                  </a-descriptions-item>
                </a-descriptions>
                <p class="reuslt-item-title">检查项: </p>
                <a-row>
                  <a-col span="8">
                    <a-descriptions :column="{ sm: 1 }" bordered size="small">
                      <a-descriptions-item :label="item.item" v-for="(item, rkidx) in resultItem.check_items" :key="rkidx">
                        <a-icon v-if="item.result" type="check" style="color: #52c41a"/>
                        <a-icon v-else type="close" style="color: #f5222d"/>
                      </a-descriptions-item>
                    </a-descriptions>
                  </a-col>
                </a-row>
                <div v-if="taskType === 'cve'">
                  <p class="reuslt-item-title" style="margin-top: 12px">CVE修复情况:</p>
                  <a-collapse :bordered="false">
                    <a-collapse-panel
                      v-for="(cve, rkidx) in resultItem.cves"
                      :key="rkidx"
                      :header="`${cve.cve_id}`"
                    >
                      <div class="cve-item">
                        <p class="reuslt-item-title">结果:</p>
                        {{ statusResultTextMap[cve.result] }}
                      </div>
                      <div class="cve-item">
                        <p class="reuslt-item-title" style="margin-top: 12px">Log:</p>
                        <p class="result-log">{{ cve.log }}</p>
                      </div>
                      <a-badge :status="statusResultValueMap[cve.result]" slot="extra"/>
                    </a-collapse-panel>
                  </a-collapse>
                </div>
                <div v-if="taskType === 'repo'">
                  <p class="reuslt-item-title" style="margin-top: 16px">Log: </p>
                  <p class="result-log">{{ resultItem.log }}</p>
                </div>
                <a-badge :status="statusValueMap[resultItem.status]" slot="extra"/>
              </a-collapse-panel>
            </a-collapse>
          </div>
        </a-spin>
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
/****************
/* 任务结果报告页面
****************/

import { i18nRender } from '@/vendor/ant-design-pro/locales'
import { getCveTaskResult, getRepoTaskResult } from '@/api/leaks'

import { dateFormat } from '@/views/utils/Utils'

const cveStatusTextMap = {
  'succeed': '修复成功',
  'fail': '待修复',
  'running': '运行中',
  'on standby': '等待',
  'set': '已设置'
}

const repoStatusTextMap = {
  'succeed': '设置成功',
  'fail': '设置失败',
  'running': '运行中',
  'on standby': '等待',
  'set': '已设置'
}

const statusValueMap = {
  'succeed': 'success',
  'fail': 'error',
  'running': 'processing',
  'on standby': 'default',
  'set': 'success'
}

const statusResultTextMap = {
  'fixed': '已修复',
  'unfixed': '未修复',
  'running': '运行中',
  'on standby': '等待'
}

const statusResultValueMap = {
  'fixed': 'success',
  'unfixed': 'error',
  'running': 'processing',
  'on standby': 'default'
}

export default {
  name: 'TaskResultReport',
  components: {
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
            return <router-link to={route.path}>{route.breadcrumbName}</router-link>
          }
        }
      }
    }
  },
  data () {
    return {
      taskId: this.$route.params.taskId,
      taskType: this.$route.params.taskType,
      resultLoading: false,
      resultData: {},
      repoStatusTextMap,
      cveStatusTextMap,
      statusValueMap,
      statusResultTextMap,
      statusResultValueMap
    }
  },
  methods: {
    dateFormat,
    getCheckResult () {
      const _this = this
      this.resultLoading = true
      switch (this.taskType) {
        case 'cve':
          getCveTaskResult({
            taskId: this.taskId,
            cveList: []
          }).then(function (res) {
            _this.resultData = Object.assign({}, res.result)
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          }).finally(function () {
            _this.resultLoading = false
          })
          break
        case 'repo':
          getRepoTaskResult({
            taskId: this.taskId,
            hostList: []
          }).then(function (res) {
            _this.resultData = Object.assign({}, res.result)
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          }).finally(function () {
            _this.resultLoading = false
          })
          break
      }
    }
  },
  mounted: function () {
    this.getCheckResult()
  }
}
</script>

<style lang="less" scoped>
.reuslt-item-title{
  font-weight: 500;
  color: rgba(0,0,0,.85)
}
/deep/ .ant-descriptions-item {
  .ant-descriptions-item-label {
    font-weight: 500;
  }
}
.result-log {
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 4px 6px 20px;
}
</style>
