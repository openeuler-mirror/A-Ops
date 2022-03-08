<template>
  <div @click="showModal">
    <a-button type="primary">上传安全公告</a-button>
    <a-modal
      title="上传文件"
      :visible="visible"
      :footer="null"
      @cancel="closeModal"
    >
      <div>
        <a-upload :file-list="fileDataList" :remove="removeFile" :before-upload="preUpload">
          <div style="display:flex;">
            <div style="flex">
              <a-button> <a-icon type="upload" /> 选择文件 </a-button>
            </div>
            <div style="margin-left: 35px;margin-top: 3px;font-size:15px;">支持类型: xml、zip、tar.gz、tar.bz2</div>
          </div>
        </a-upload>
      </div>
      <a-button
          type="primary"
          :disabled="fileDataList.length === 0"
          :loading="uploading"
          style="margin-top: 16px;width: 111px;"
          @click="goUpload"
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
        fileDataList: [],
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
        this.fileDataList = []
      },
      removeFile(file) {
      const index = this.fileDataList.indexOf(file);
      const newfileDataList = this.fileDataList.slice();
      newfileDataList.splice(index, 1);
      this.fileDataList = newfileDataList;
      },
      preUpload(file) {
        this.fileDataList = [file];
        // 文件类型
        var suffix = file.name.substring(file.name.lastIndexOf('.') + 1)
        var arr = ['xml', 'zip', 'tar.gz', 'tar.bz2']
        if (!arr.includes(suffix)) {
          this.$message.error('文件类型不符合规定!')
          this.removeFile(file)
          return false;
        }

        // 读取文件大小
        var fileSize = file.size
        if (fileSize / 1024 / 1024 / 10 > 1) {
          this.$message.error('文件大于10M!')
          this.removeFile(file)
          return false
        }
      },
      goUpload() {
        const { fileDataList } = this;
        const formData = new FormData();
        fileDataList.forEach(file => {
          formData.append('file', file);
        });
        this.uploading = true
        const _this = this
        upload(formData).then(function (res) {
                 _this.$message.success(res.msg)
                 _this.$emit('addSuccess')
                 _this.fileDataList = []
                 _this.uploading = false
               }).catch(function (err) {
                 _this.uploading = false
                 _this.$message.error(err.response.data.msg || err.response.data.detail)
               }).finally(function () {
                 _this.visible = false
                 _this.fileDataList = []
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
