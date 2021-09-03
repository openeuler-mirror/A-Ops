<template>
  <my-page-header-wrapper>
    <a-card>
      <div style="height: 110px;position: relative;">
        <img class="avatar-img" src="~@/assets/huawei_logo_h.png">
        <div class="content-div">
          <div class="title">
            <span style="padding-right: 5px">报告ID：{{report.id}}</span>
          </div>
          <div style="height: 60px;line-height: 28px">
            <a-row>
              <a-col :span="8">主机名称：{{report.hostName}}</a-col>
              <a-col :span="8">任务ID：{{report.taskId}}</a-col>
              <a-col :span="8">诊断时间：{{report.diagTime}}</a-col>
            </a-row>
            <a-row>
              <a-col :span="24">
                所用故障树：
                <a-tag v-for="(item,key) in report.faultTreeList" :key="key">{{item.tree_name}}</a-tag>
              </a-col>
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
          <span>树图...</span>
        </a-tab-pane>
        <a-tab-pane key="2" tab="文件" force-render>
          <p>1、文件1</p>
          <p>2、文件2</p>
          <p>2、文件...</p>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import { getdiagreport } from '@/api/diagnosis'

export default {
  name: 'NetworkTopoDiagram',
  components: {
    MyPageHeaderWrapper
  },
  created () {
    this.getDiagReport()
  },
  data () {
    return {
      task_id: this.$route.params.id,
      report: {},
      reportData: []
    }
  },
  methods: {
    getDiagReport () {
      const _this = this
      const reportList = []
      reportList.push(_this.task_id)
      getdiagreport(reportList).then(function (res) {
        if (res.code === 200) {
          _this.reportData = res.result
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
      })
      this.report = {
        id: '2349497',
        hostName: 'Host111',
        taskId: '1234123421',
        diagTime: '2021-08-20 12:32',
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
        faultTreeList: [{
          tree_name: '故障树2',
          avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
          content: '这里可以放一两项简单描述，仅可点击查看详情2'
        }, {
          tree_name: '故障树2',
          avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
          content: '这里可以放一两项简单描述，仅可点击查看详情2'
        }, {
          tree_name: '故障树2',
          avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
          content: '这里可以放一两项简单描述，仅可点击查看详情2'
        }]
      }
    },
    deleteReport () {
      // console.log('删除！')// 删除后当前页不存在，可能要跳回列表页
      this.$message.success('诊断报告已删除！')
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
