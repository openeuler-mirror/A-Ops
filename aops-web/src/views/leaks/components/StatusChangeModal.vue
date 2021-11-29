<template>
  <div @click="showModal">
    <a-button
      :disabled="selectedRowsAll.length < 1"
      @click="showModal"
      type="primary"
    >
      修改状态
    </a-button>
    <a-modal
      :visible="visible"
      :confirm-loading="isLoading"
      @ok="handleOk"
      @cancel="handleCancel"
    >
      <h3>
        修改以下CVE
      </h3>
      <p>
        {{ `${selectedRowsAll.map(row => row.cve_id).join('、')}` }}
      </p>
      <p>的状态为：</p>
      <a-select default-value="in review" style="width: 120px" @change="handleChange" :value="value">
        <a-select-option value="not reviewed">
          未关注
        </a-select-option>
        <a-select-option value="in review">
          关注中
        </a-select-option>
        <a-select-option value="on-hold">
          挂起
        </a-select-option>
        <a-select-option value="resolved">
          已解决
        </a-select-option>
        <a-select-option value="no action">
          已忽略
        </a-select-option>
      </a-select>
    </a-modal>
  </div>
</template>

<script>
/****************
/* 修改cve状态弹窗组件
****************/
import { setCveStatus } from '@/api/leaks'
export default {
  name: 'StatushangeModal',
  props: {
    selectedRowsAll: {
      type: Array,
      default: () => []
    }
  },
  data () {
    return {
      visible: false,
      isLoading: false,
      value: 'in review'
    }
  },
  methods: {
    handleChange (value) {
      this.value = value
    },
    showModal () {
      this.visible = true
      this.value = 'in review'
    },
    handleCancel () {
      this.visible = false
    },
    handleOk () {
      const _this = this
      this.isLoading = true
      setCveStatus({
        cveList: _this.selectedRowsAll.map(row => row.cve_id),
        status: _this.value
      }).then(function (res) {
        _this.$message.success(res.msg)
        _this.$emit('statusUpdated')

        _this.visible = false
      }).catch(function (err) {
        _this.$message.error(err.response.data.msg)
      }).finally(function () {
        _this.isLoading = false
      })
    }
  }
}
</script>
<style lang="less" scoped>
</style>
