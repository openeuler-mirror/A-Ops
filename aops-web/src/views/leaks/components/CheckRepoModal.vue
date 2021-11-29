<template>
  <a-modal
    centered
    title="查看REPO源"
    :visible="visible"
    :footer="null"
    @cancel="handleCancel"
    destroyOnClose
  >
    <a-form
      :label-col="{ span: 5 }"
      :wrapper-col="{ span: 19 }"
    >
      <a-form-item label="REPO源名称">
        {{ detailProps.repo_name }}
      </a-form-item>
      <a-form-item label="适用版本">
        {{ detailProps.repo_attr }}
      </a-form-item>
      <a-form-item label="REPO内容">
        <div class="repo-content">{{ detailProps.repo_data }}</div>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script>
  /****************
  /* 查看repo信息弹窗
  ****************/

  export default {
    name: 'CheckRepoModal',
    components: {
    },
    props: {
      visible: {
        type: Boolean,
        default: false
      },
      repoId: {
        type: String,
        default: ''
      },
      detailProps: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {
        isLoading: false,
        repoData: {}
      }
    },
    watch: {
      visible () {
        if (this.visible) {
          this.handleOepn()
        }
      }
    },
    methods: {
      handleOepn () {
      },
      handleCancel () {
        this.$emit('close')
      }
    }
  }
</script>
<style lang="less" scoped>
.aops-add-repo {
  position: absolute;
  width: 100%;
  height: 100%;
  top: 0;
  left: 0;
  background: #fff;
  display: flex;
  justify-content: center;
  align-items: center;
  font-size: 36px;
  cursor: pointer;
  border: 1px dashed #d9d9d9;
  &:hover {
    border-color: #3265F2;
  }
}
/deep/ .ant-form-item-label {
  line-height: 1.5em !important
}
/deep/ .ant-form-item-control {
  line-height: 1.5em !important
}
.repo-content {
  white-space: pre-wrap;
  border: 1px solid #ddd;
  border-radius: 3px;
  padding: 4px 6px;
  max-height: 300px;
  overflow-y: scroll;
}
</style>
