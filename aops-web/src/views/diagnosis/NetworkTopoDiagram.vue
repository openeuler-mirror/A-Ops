<template>
  <my-page-header-wrapper>
    架构感知
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
        tree_name: 'netWork',
        avatar: '',
        content: ''
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
