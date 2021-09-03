<template>
  <my-page-header-wrapper>
    <div style="height: 110px;position: relative;">
      <img class="avatar-img" :src="faultTree.avatar">
      <div class="content-div">
        <div class="title">
          <span style="padding-right: 5px">{{faultTree.tree_name}}</span>
          <a-tag>内核</a-tag>
          <a-tag>软件故障</a-tag>
          <a-tag>配置</a-tag>
        </div>
        <div class="remark">描述：{{faultTree.content}}</div>
        <div class="btn-box">
          <a>编辑</a>
          <a>导出</a>
          <a>删除</a>
        </div>
      </div>
      <a-button type="primary" style="position: absolute;right: 0;top: -8px">
        故障诊断<a-icon type="plus"/>
      </a-button>
    </div>
    <a-tabs default-active-key="1">
      <a-tab-pane key="1" tab="树图">
        <span>树图...</span>
      </a-tab-pane>
      <a-tab-pane key="2" tab="文件" force-render>
        <p>1、文件1</p>
        <p>2、文件2</p>
        <p>2、文件...</p>
      </a-tab-pane>
    </a-tabs>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'

export default {
  name: 'NetworkTopoDiagram',
  components: {
    MyPageHeaderWrapper
  },
  created () {
    this.getFaultTree()
  },
  data () {
    return {
      faultTreeId: this.$route.params.id,
      faultTree: {}
    }
  },
  methods: {
    getFaultTree () {
      this.faultTree = {
        tree_name: '故障树2',
        avatar: 'https://gw.alipayobjects.com/zos/rmsportal/WdGqmHpayyMjiEhcKoVE.png',
        content: '这里可以放一两项简单描述，仅可点击查看详情2'
      }
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
