<template>
  <my-page-header-wrapper>
    <a-card>
      <div style="height: 110px;position: relative;">
        <img class="avatar-img" src="~@/assets/vertical-left.png">
        <div class="content-div">
          <div class="title">
            <span style="padding-right: 5px">报告ID：{{ reportData.report_id }}</span>
          </div>
          <div style="height: 60px;line-height: 28px">
            <a-row>
              <a-col :span="10">主机名称：{{ reportData.host_id }}</a-col>
              <a-col :span="10">任务ID：{{ reportData.task_id }}</a-col>
              <a-col :span="10">诊断时间：{{ reportData.timeRange }}</a-col>
            </a-row>
          </div>
          <div class="btn-box">
            <a-popconfirm
              title="你确定要删除这份报告吗?"
              ok-text="确定"
              cancel-text="取消"
              @confirm="deleteReport"
            >
              <a href="#">删除</a>
            </a-popconfirm>
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
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import { getdiagreport, delDiagReport } from '@/api/diagnosis'
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
      reportLoading: false
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
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.reportLoading = false
      })
    },
    deleteReport () {
      // console.log('删除！')// 删除后当前页不存在，可能要跳回列表页
      const _this = this
      const reportList = []
      reportList.push(_this.reportData.report_id)
      delDiagReport(reportList).then(function (res) {
        if (res.code === 200) {
          _this.$message.success('诊断报告已删除！')
          _this.$router.push('/diagnosis/fault-diagnosis')
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
      })
    }
  }
}
</script>
<style lang="less" scoped>
.avatar-img {
  width: 110px;
  height: 110px;
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
