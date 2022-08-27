<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div style="height: 110px;position: relative;">
        <img class="avatar-img" src="~@/assets/dtree-icon.png">
        <div class="content-div">
          <div class="title">
            <span style="padding-right: 5px">报告ID：{{ reportData.report_id }}</span>
          </div>
          <div style="height: 60px;line-height: 28px">
            <a-row>
              <a-col :span="10">
                主机名称：
                <a-spin v-if="hostInfoLoading" />
                <span v-else>{{ hostInfo.host_name }}</span>
              </a-col>
              <a-col :span="10">任务ID：{{ reportData.task_id }}</a-col>
              <a-col :span="10">诊断时间：{{ reportData.timeRange }}</a-col>
            </a-row>
          </div>
        </div>
      </div>
      <a-tabs default-active-key="1" style="min-height: 350px">
        <a-tab-pane key="1" tab="树图">
          <fault-tree
            :treeData="reportData.report || {}"
            :treeDataLoading="reportLoading"
            :highLightError="true"
          />
        </a-tab-pane>
        <a-tab-pane key="2" tab="文件" force-render>
          <a-card style="white-space: pre-wrap;">
            <div>{{ reportData.report }}</div>
          </a-card>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
// this component is abandoned
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import { getdiagreport } from '@/api/diagnosis'
import { hostInfo } from '@/api/assest'
import { dateFormat } from '@/views/utils/Utils'
import FaultTree from './components/FaultTree.vue'

export default {
  name: 'DiagReport',
  components: {
    MyPageHeaderWrapper,
    FaultTree
  },
  created () {
    this.getDiagReport()
  },
  data () {
    return {
      task_id: this.$route.params.id,
      report: {},
      reportData: [],
      reportLoading: false,
      hostInfo: {},
      hostInfoLoading: false
    }
  },
  methods: {
    getDiagReport () {
      const _this = this
      const reportList = []
      reportList.push(_this.task_id)
      this.reportLoading = true
      getdiagreport(reportList).then(function (res) {
        if (res.code === 200) {
          const temp = res.result[0] || {}
          _this.reportData = {
            ...temp,
            timeRange: `${dateFormat('YYYY-mm-dd HH:MM:SS', temp.start * 1000)} - ${dateFormat('YYYY-mm-dd HH:MM:SS', temp.end * 1000)}`
          }
          if (!_this.reportData.report || !_this.reportData.report['node name']) {
            console.warn('no data for tree')
          }
          _this.getHostInfo(temp && temp.host_id)
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.reportLoading = false
      })
    },
    getHostInfo (id) {
      const _this = this
      this.hostInfoLoading = true
      hostInfo({
        basic: true,
        host_list: [id]
      }).then(function (res) {
        _this.hostInfo = res.host_infos && res.host_infos[0] || {}
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.hostInfoLoading = false
      })
    }
  }
}
</script>
<style lang="less" scoped>
.avatar-img {
  width: 84px;
  height: 84px;
  float: left;
  border-radius: 5px;
  margin-right: 10px;
}
.content-div {
  width: calc(100% - 120px);
  height: 100%;
  float: left;
}
.title {
  font-weight: 600;
  width: calc(100% - 115px);
  white-space: nowrap;
  text-overflow: ellipsis;
  overflow: hidden;
  word-break: break-all;
  font-size: 22px;
  line-height: 1em;
  padding-bottom: 5px;
}
.remark {
  height: 60px;
  text-overflow: -o-ellipsis-lastline;
  overflow: hidden;
  text-overflow: ellipsis;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
}
.btn-box a{
  margin-right: 20px;
  user-select: none;
}
</style>
