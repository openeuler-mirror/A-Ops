<template>
    <div>
        <a-spin :spinning="isLoading">
            <div class="content">
                <div class="add-msg">
                    <div :class="{ 'host-msg': true, 'all-msg': true, 'reset-border': border_bool }">
                        <div class="host-img">
                            <img src="~@/assets/dash-host.png" alt="">
                        </div>

                        <div class="host-all">
                            <a-row class="host-occupation">
                                <a-col :span="12">
                                    <span class="bold">
                                        主机名：{{ host_name }}
                                    </span>
                                </a-col>
                                <a-col :span="12">
                                    <span class="bold">
                                        主机ip：{{ public_ip }}
                                    </span>
                                </a-col>
                            </a-row>

                            <a-row>
                                <span class="host-toggle" @click="hostDetailToggle">
                                    {{ detailTxt }}
                                    <a-icon :type="detailIcon" />
                                </span>
                            </a-row>

                            <a-row class="host-occupation">
                                <a-col :span="12">
                                    <span class="bold">
                                        主机组：{{ host_group_name }}
                                    </span>
                                </a-col>
                                <a-col :span="12" >
                                    <span class="bold">
                                        状态：{{ status }}
                                    </span>
                                </a-col>
                            </a-row>
                        </div>
                    </div>

                    <div v-show="detailToggle">
                        <div class="os_msg all-msg">
                            <span class="title bold">操作系统</span>

                            <div class="meg-row">
                                <a-row type="flex">
                                    <a-col :span="12" :order="1">
                                        <span class="bold">操作系统版本：
                                            <span>
                                                <CutText :text="os.os_version" :length="25"></CutText>
                                            </span>
                                        </span>
                                    </a-col>
                                    <a-col :span="12" :order="2">
                                        <span class="bold">内核版本：
                                            <span>
                                                <CutText :text="os.kernel" :length="25"></CutText>
                                            </span>
                                        </span>
                                    </a-col>
                                </a-row>
                            </div>

                            <div class="meg-row">
                                <a-row>
                                    <a-col :span="6" :order="1">
                                        <span class="bold">bios版本：
                                        <span>
                                            <CutText :text="os.bios_version" :length="14"></CutText>
                                        </span>
                                        </span>
                                    </a-col>
                                </a-row>
                            </div>
                        </div>

                <div class="cpu-msg all-msg">
                    <span class="title bold">CPU信息</span>
                        <div class="meg-row">
                            <a-row type="flex">
                                <a-col :span="6" :order="1">
                                    <span class="bold">架构：
                                        <span>
                                            <CutText :text="cpu.architecture" :length="14"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="2">
                                    <span class="bold">核数：
                                        <span>
                                            <CutText :text="cpu.core_count" :length="14"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="3">
                                    <span class="bold">厂商：
                                        <span>
                                            <CutText :text="cpu.vendor_id" :length="14"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="4">
                                    <span class="bold">处理器：
                                        <span>
                                            <CutText :text="cpu.model_name" :length="14"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                            </a-row>
                        </div>

                        <div class="meg-row">
                            <a-row type="flex">
                                <a-col :span="6" :order="1">
                                    <span class="bold">L1d cache：
                                        <span>
                                            <CutText :text="cpu.l1d_cache"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="2">
                                    <span class="bold">L1i cache：
                                        <span>
                                            <CutText :text="cpu.l1i_cache"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="3">
                                    <span class="bold">L2 cache：
                                        <span>
                                            <CutText :text="cpu.l2_cache"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="6" :order="4">
                                    <span class="bold">L3 cache：
                                        <span>
                                            <CutText :text="cpu.l3_cache"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                            </a-row>
                        </div>
                    </div>

                    <div class="memory-msg all-msg">
                        <span class="title bold">内存信息</span>
                    </div>
                        <div class="meg-row">
                            <a-row type="flex">
                                <a-col :span="12" :order="1">
                                    <span class="bold meg-row-left">内存大小：
                                        <span>
                                            <CutText :text="memory.size"></CutText>
                                        </span>
                                    </span>
                                </a-col>
                                <a-col :span="12" :order="2">
                                    <span class="bold">内存数量：
                                        <span>
                                            {{ memory.total }}
                                        </span>
                                    </span>
                                </a-col>
                            </a-row>
                        </div>
                        <a-collapse>
                            <a-collapse-panel :header="'详情'">
                                <div class="meg-row" v-for="(data, idx) in memory.info" :key="idx">
                                    <a-row type="flex">
                                        <a-col :span="6" :order="1">
                                            <span class="bold">大小：
                                                <span>
                                                    <CutText :text="data.size"></CutText>
                                             </span>
                                         </span>
                                     </a-col>
                                     <a-col :span="6" :order="2">
                                         <span class="bold">类型：
                                            <span>
                                                <CutText :text="data.type"></CutText>
                                            </span>
                                        </span>
                                        </a-col>
                                        <a-col :span="6" :order="3">
                                            <span class="bold">速度：
                                                <span>
                                                    <CutText :text="data.speed"></CutText>
                                                </span>
                                            </span>
                                        </a-col>
                                        <a-col :span="6" :order="4">
                                            <span class="bold">厂商：
                                                <span>
                                                    <CutText :text="data.manufacturer"></CutText>
                                                </span>
                                            </span>
                                        </a-col>
                                    </a-row>
                                </div>
                            </a-collapse-panel>
                        </a-collapse>
                    </div>
                </div>
            </div>
        </a-spin>
    </div>
</template>
<script>
import CutText from '@/components/CutText'

export default {
    name: 'AddHostDetail',
    components: {CutText},
  data () {
    return {
        detailToggle: true,
        detailTxt: '详情收起',
        detailIcon: 'up',
        border_bool: false,
        hostId: this.$route.params.hostId,
    //   host_id: undefined,
        agent_port: undefined,
        host_group_name: undefined,
        host_id: undefined,
        host_name: undefined,
        management: undefined,
        public_ip: undefined,
        scene: undefined,
        status: undefined,
        os: {
            kernel: '暂无',
            bios_version: '暂无',
            os_version: '暂无'
        },
        cpu: {
            architecture: '暂无',
            core_count: '暂无',
            model_name: '暂无',
            vendor_id: '暂无',
            l1d_cache: '暂无',
            l1i_cache: '暂无',
            l2_cache: '暂无',
            l3_cache: '暂无'
        },
        memory: {
            size: '暂无',
            total: '暂无',
            info: [
            {
                size: '暂无',
                type: '暂无',
                speed: '暂无',
                manufacturer: '暂无'
            }
            ]
        }
    }
  },
  props: {
    basicHostInfo: {
        type: Object,
        default: undefined
    },
    basicInfo: {
        type: Object,
        default: undefined
    },
    isLoading: {
        type: Boolean,
        default: false
    }
  },
  watch: {
      // 主机基本信息
      basicHostInfo: function () {
          this.getHostDetail()
      },
      // 主机下资源信息
      basicInfo: function () {
          this.getDetail()
      }
  },
  methods: {
    initHostDetail(data) {
        if (data) {
            return data
        } else {
            return '暂无'
        }
    },
    getHostDetail() {
        const data = this.basicHostInfo
        this.host_group_name = this.initHostDetail(data.host_group_name)
        this.public_ip = this.initHostDetail(data.public_ip)
        this.status = this.initHostDetail(data.status)
        this.host_name = this.initHostDetail(data.host_name)
        this.scene = this.initHostDetail(data.scene)
    },
    getDetail() {
        let data = this.basicInfo
        data = data.host_info
        for (const member in data.os) {
            this.os[member] = this.initHostDetail(data.os[member])
        }
        for (const member in data.cpu) {
            this.cpu[member] = this.initHostDetail(data.cpu[member])
        }
        for (const member in data.memory) {
            this.memory[member] = this.initHostDetail(data.memory[member])
        }
    },
    hostDetailToggle() {
        this.detailToggle = !this.detailToggle
        this.border_bool = !this.border_bool
        if (this.detailIcon === 'up') {
            this.detailTxt = '详情展开'
            this.detailIcon = 'down'
        } else {
            this.detailTxt = '详情收起'
            this.detailIcon = 'up'
        }
    }
  },
  mounted () {

  }
}
</script>
<style lang="less" scoped>

.add-msg {
  font-size:12px;
  position: relative;
  box-sizing: border-box;
}

.all-msg {
  display: block;
  width: 100%;
  /* margin-top:2px; */
  padding:12px 0;/* padding:12px 16px; */
  box-sizing: border-box;
  border-bottom: 2px solid rgba(240, 242, 245);
}

.reset-border {
    border-bottom: 2px solid transparent;
    padding-bottom: 9px!important;
}

.left-host-img {
  display: block;
  float: left;
}
.all-msg::after {
  content:"";
  display:block;
  clear:both;
}

.host-all {
    position: relative;
}

.host-img {
  display: block;
  width:75px;
  height:75px;
  border-radius: 50%;
  background-color:transparent;
  position: absolute;
}
.host-img img {
  width: 80%;
  height: 80%;
  border-radius: 50%;
  transform:translate(8px,8px)
}
.host-msg {
  position: relative;
  font-weight: bold;
  font-size:16px;
  padding-top:0;
  padding-bottom: 32px;
}

.os_msg {
  display: block;
  position: relative;
  padding-bottom: 16px;
}

.cpu-msg {
  position: relative;
  padding-bottom: 16px;
}

.memory-msg {
  position: relative;
  padding-bottom: 16px;
  padding-bottom:0;
  border:none;
}

.title {
  display: block;
  text-align:left;
  font-size:16px;
}

.bold {
  font-weight: bold;
}

.bold span {
  font-weight: 400;
}

.meg-row:not(:first-child) {
  display: block;
  position: relative;
  width: 100%;
  padding-top:16px;
}

.host-occupation {
  display: block;
  width: 100%;
  padding-top:9px;
  .ant-col:first-child {
    padding-left:100px;
  }
}

.host-toggle {
    position: absolute;
    white-space:nowrap;
    user-select: none;
    font-weight: normal;
    font-size: 14px;
    right:0;
    z-index: 1;
    cursor: pointer;
}
/deep/ .ant-collapse {
    background: #fff;
    border: 0;
    & > .ant-collapse-item {
        border-bottom: 0;
        & > .ant-collapse-header {
            padding-left: 0;
            font-size: 14px;
            color: rgba(0,0,0,0.65);
            .ant-collapse-arrow {
                left: 40px;
            }
        }
    }
}
/deep/ .ant-collapse-content {
    border-top: 0;
    .ant-collapse-content-box {
        padding-top: 8px;
    }
}
</style>
