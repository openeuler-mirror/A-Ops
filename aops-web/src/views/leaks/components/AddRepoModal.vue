<template>
  <div class="aops-add-repo" @click="showModal">
    <a-icon type="plus" />
    <a-modal
      centered
      title="新建REPO源"
      :visible="visible"
      :confirm-loading="isLoading"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <a-form
        :form="form"
        :label-col="{ span: 5 }"
        :wrapper-col="{ span: 19 }"
      >
        <a-form-item label="REPO源名称">
          <a-input
            :maxLength="19"
            placeholder="请输入REPO源名称，19个字符以内"
            v-decorator="['repoName', { rules: [{ required: true, message: '请输入REPO名称' }] }]"
          >
          </a-input>
        </a-form-item>
        <a-form-item label="REPO内容">
          <div>
            <a-textarea
              v-decorator="['repoData',{rules: [{ required: true, message: '请输入REPO描述' }]}]"
              :rows="16"
              placeholder="请输入REPO内容"
            />
            <a-button class="download-template" @click="handleGetTemplate">下载模板</a-button>
          </div>
        </a-form-item>
        <a-form-item label="上传模板文件" class="upload-row">
          <uploader
            toJSON
            uid="repoUploader"
            fileType="repo"
            @change="handleFileUpload"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script>
  /****************
  /* 添加repo弹窗
  ****************/

  import { addRepo, getRepoTemplate } from '@/api/leaks'

  import { downloadBlobFile } from '@/views/utils/downloadBlobFile'
  import Uploader from '@/components/Uploader/RepoUploader'

  export default {
    name: 'AddRepoModal',
    components: {
      Uploader
    },
    props: {
    },
    data () {
      return {
        visible: false,
        isLoading: false,
        form: this.$form.createForm(this, { name: 'addRepo' })
      }
    },
    methods: {
      showModal () {
        this.form.resetFields()
        this.visible = true
      },
      handleCancel () {
        this.visible = false
      },
      handleOk () {
        this.form.validateFields((err, values) => {
          if (!err) {
            const _this = this
            this.isLoading = true
            addRepo(values).then(function (res) {
              _this.$message.success(res.msg)
              _this.$emit('addSuccess')
              _this.visible = false
              _this.form.resetFields()
            }).catch(function (err) {
              _this.$message.error(err.response.data.msg || err.response.data.detail)
            }).finally(function () {
              _this.isLoading = false
            })
          }
        })
      },
      // 下载模板
      handleGetTemplate () {
        const _this = this
        getRepoTemplate().then(function (res) {
            // download files
            downloadBlobFile(res.data, res.fileName)
          }).catch(function (err) {
            _this.$message.error(err.response.data.msg)
          })
      },
      handleFileUpload (content) {
        content && this.form.setFieldsValue({ 'repoData': content })
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
    top: 35px;
    height: 24px;
    left: -80px;
}
</style>
