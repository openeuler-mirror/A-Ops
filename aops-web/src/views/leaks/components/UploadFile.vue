<template>
  <div @click="showModal">
    <a-button type="primary">上传安全公告</a-button>
    <a-modal
      title="上传文件"
      :visible="visible"
      :footer="null"
      @cancel="closeModal"
    >
      <a-upload :file-list="fileList" :remove="handleRemove" :before-upload="beforeUpload">
         <a-button> <a-icon type="upload" /> 选择文件 </a-button>
      </a-upload>
       <a-button
           type="primary"
           :disabled="fileList.length === 0"
           :loading="uploading"
           style="margin-top: 16px;width: 111px;"
           @click="handleUpload"
       >
          {{ uploading ? '上传中' : '开始上传' }}
       </a-button>
    </a-modal>
  </div>
</template>

<script>

  import { upload } from '@/api/leaks'

  export default {
    name: 'AddRepoModal',
    components: {
    },
    props: {
    },
    data () {
      return {
        fileList: [],
        visible: false,
        uploading: false
      }
    },
    methods: {
      showModal () {
        this.visible = true
      },
      closeModal () {
        this.visible = false
        this.fileList = []
      },
      handleRemove(file) {
      const index = this.fileList.indexOf(file);
      const newFileList = this.fileList.slice();
      newFileList.splice(index, 1);
      this.fileList = newFileList;
      },
      beforeUpload(file) {
        this.fileList = [...this.fileList, file];
        // 文件类型
        var suffix = file.name.substring(file.name.lastIndexOf('.') + 1)
        var arr = ['xml', 'zip', 'tar.gz', 'tar.bz2']
        if (!arr.includes(suffix)) {
          this.$message.error('文件类型不符合规定!')
          this.handleRemove(file)
        }
        return false;
      },
      handleUpload() {
        const { fileList } = this;
        const formData = new FormData();
        fileList.forEach(file => {
          formData.append('file', file);
        });
        this.uploading = true
        const _this = this
        upload(formData).then(function (res) {
                 _this.$message.success(res.msg)
                 _this.$emit('addSuccess')
                 _this.fileList = []
                 _this.uploading = false
                 _this.visible = false
               }).catch(function (err) {
                 _this.uploading = false
                 _this.$message.error(err.response.data.msg || err.response.data.detail)
               })
      }
    }
  }
</script>
<style lang="less" scoped>
.upload-row {
  /deep/ .ant-form-item-label {
    line-height: 22px;
  }
  /deep/ .ant-form-item-control{
    line-height: 16px;
  }
}

.download-template {
    position: absolute;
    width: 70px;
    padding: 0 4px;
    bottom: 270px;
    height: 24px;
    left: -80px;
}
</style>
