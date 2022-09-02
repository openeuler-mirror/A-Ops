<template>
  <div>
    <a-drawer
      title="主机详情"
      closable
      @close="handleCancel"
      :visible="visible"
      width="400"
    >
      <a-spin :spinning="hostInfoLoading">
        <a-descriptions title="操作系统" layout="vertical" :column="1">
          <a-descriptions-item label="系统名">
            {{ os.name }}
          </a-descriptions-item>
          <a-descriptions-item label="内核版本">
            {{ os.kernel_version }}
          </a-descriptions-item>
          <a-descriptions-item label="bios版本">
            {{ os.bios_verison }}
          </a-descriptions-item>
        </a-descriptions>
        <a-descriptions title="CPU信息" layout="vertical" :column="2">
          <a-descriptions-item label="架构">
            {{ cpu.architecture }}
          </a-descriptions-item>
          <a-descriptions-item label="内核数">
            {{ cpu.core_count }}
          </a-descriptions-item>
          <a-descriptions-item label="modal名称">
            {{ cpu.model_name }}
          </a-descriptions-item>
          <a-descriptions-item label="verdorId">
            {{ cpu.verdor_id }}
          </a-descriptions-item>
          <a-descriptions-item label="L1 iCache">
            {{ cpu.l1d_cache }}
          </a-descriptions-item>
          <a-descriptions-item label="L2 dCache">
            {{ cpu.l1i_cache }}
          </a-descriptions-item>
          <a-descriptions-item label="L3 cache">
            {{ cpu.l2_cache }}
          </a-descriptions-item>
          <a-descriptions-item label="L3 cache">
            {{ cpu.l3_cache }}
          </a-descriptions-item>
        </a-descriptions>
        <a-descriptions title="内存信息" layout="vertical" :column="2">
          <a-descriptions-item label="内存大小">
            {{ memory.size }}
          </a-descriptions-item>
          <a-descriptions-item label="内存数量">
            {{ memory.total }}
          </a-descriptions-item>
          <a-descriptions-item label="详情">
            <div v-for="(m, idx) in (memory.info || [])" :key="idx">
              <p>{{ `${idx+1}号` }}</p>
              <p>容量{{ m.size }}</p>
              <p>类型{{ m.type }}</p>
              <p>速度{{ m.speed }}</p>
              <p>制造商{{ m.manufacturer }}</p>
            </div>
          </a-descriptions-item>
        </a-descriptions>
      </a-spin>
    </a-drawer>
  </div>
</template>

<script>
// this component is abendoned
import { hostInfo } from '@/api/assest'

export default {
    name: 'HostDetailDrawer',
    props: {
        visible: {
          type: Boolean,
          default: false
        },
        hostId: {
          type: String,
          default: undefined
        }
    },
    data () {
        return {
          hostInfoLoading: false,
          hostInfo: {}
        }
    },
    computed: {
      os () {
        return this.hostInfo.os || {}
      },
      cpu () {
        return this.hostInfo.cpu || {}
      },
      memory () {
        return this.hostInfo.memory || {}
      }
    },
    watch: {
      hostId: function () {
        this.hostInfo = []
        this.getHostInfo()
      }
    },
    methods: {
        handleCancel () {
          this.$emit('close')
        },
        getHostInfo () {
          const _this = this
          this.hostInfoLoading = true
          hostInfo({
            host_list: [this.hostId]
          }).then(function (res) {
            _this.hostInfo = (res.host_infos && res.host_infos[0]) || {}
          }).catch(function (err) {
            _this.$message.error(err.response.msg)
          }).finally(function () { _this.hostInfoLoading = false })
        }
    }
}
</script>
