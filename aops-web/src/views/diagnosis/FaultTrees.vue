<template>
  <my-page-header-wrapper>
    <a-card :bordered="false" class="aops-theme">
      <div style="height: 110px;position: relative;">
        <img class="avatar-img" src="~@/assets/dtree-icon.png">
        <div class="content-div">
          <div class="title">
            <span style="padding-right: 5px">{{ faultTree.tree_name }}</span>
            <a-tag>内核</a-tag>
            <a-tag>软件故障</a-tag>
            <a-tag>配置</a-tag>
          </div>
          <div class="remark">描述：{{ faultTree.description }}</div>
        </div>
        <div class="conotrl-box">
          <a-row type="flex" align="middle">
            <a-col>
              <div class="btn-box">
                <a-popconfirm
                  title="您确定要删除该故障树吗?"
                  ok-text="确认"
                  cancel-text="取消"
                  @confirm="deletediagtree(faultTree.tree_name)"
                >
                  <a href="javascript:;" >删除</a>
                </a-popconfirm>
              </div>
            </a-col>
            <a-col>
              <drawer-view title="新建故障诊断">
                <template slot="click">
                  <a-button type="primary">
                    故障诊断<a-icon type="plus"/>
                  </a-button>
                </template>
                <template slot="drawerView">
                  <add-fault-diagnosis
                    :saveSuccess="addFaultDiagnosisSuccess"
                    :faultTreeList="treeDataAll"
                  />
                </template>
              </drawer-view>
            </a-col>
          </a-row>
        </div>
      </div>
      <a-tabs default-active-key="1" style="min-height: 350px">
        <a-tab-pane key="1" tab="树图">
          <fault-tree
            :treeData="faultTree.tree_content || {}"
            :treeDataLoading="treeDataLoading"
          />
        </a-tab-pane>
        <a-tab-pane key="2" tab="文件" force-render>
          <a-card style="white-space: pre-wrap;">
            <div>{{ faultTree.tree_content }}</div>
          </a-card>
        </a-tab-pane>
      </a-tabs>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
// this component is abandoned
import { getDiagTree, delDiagTree } from '@/api/diagnosis'

import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import DrawerView from '@/views/utils/DrawerView'
import AddFaultDiagnosis from '@/views/diagnosis/components/AddFaultDiagnosis'
import FaultTree from './components/FaultTree.vue'

export default {
  name: 'FaultTrees',
  components: {
    MyPageHeaderWrapper,
    DrawerView,
    AddFaultDiagnosis,
    FaultTree
  },
  created () {
    this.getFaultTree()
  },
  data () {
    return {
      faultTreeId: this.$route.params.id,
      faultTree: {},
      treeDataLoading: false,
      treeDataAll: []
    }
  },
  mounted () {
    const _this = this
    getDiagTree({
      treeList: []
    }).then(function (res) {
      _this.treeDataAll = [{}].concat(res.trees)
    }).catch(function (err) {
      _this.$message.error(err.response.data.msg)
    }).finally(function () {
    })
  },
  methods: {
    getFaultTree () {
      const _this = this
      const treeList = []
      treeList.push(_this.faultTreeId)
      this.treeDataLoading = true
      getDiagTree({
        treeList
      }).then(function (res) {
        _this.faultTree = res.trees[0] || {}
        if (!_this.faultTree.tree_content || !_this.faultTree.tree_content['node name']) {
          console.warn('no data for tree')
        }
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.treeDataLoading = false
      })
    },
    deletediagtree (treeName) {
      const _this = this
      const treeList = []
      treeList.push(treeName)
      delDiagTree({
        treeList
      }).then(function (res) {
        _this.$message.success(res.msg)
        // 跳转回故障诊断页面
        _this.$router.push('/diagnosis/fault-diagnosis')
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
      })
    },
    addFaultDiagnosisSuccess () {
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
.conotrl-box {
  position: absolute;
  right:0;
  top: 0;
}
.btn-box a{
  margin-right: 20px;
  user-select: none;
}
</style>
