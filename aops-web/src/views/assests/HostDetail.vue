<template>
    <page-header-wrapper>
        <a-card :bordered="false" class="aops-theme">
            <HostBasicInfo
                :basicHostInfo="basicHostInfo"
                :basicInfo="basicInfo"
                :isLoading="basicHostInfoIsLoading || basicInfoIsLoading">
            </HostBasicInfo>
        </a-card>
        <a-card :bordered="false" class="aops-theme">
            <HostPluginInfo :scene="scene" @reFetchHostInfo="reFetchHostInfo"></HostPluginInfo>
        </a-card>
    </page-header-wrapper>
</template>

<script>
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import HostPluginInfo from './components/HostPluginInfo.vue'
import HostBasicInfo from '@/views/assests/components/HostBasicInfo.vue'
import { getHostDetail } from '@/api/assest'

export default {
    name: 'HostDetail',
    components: {
        PageHeaderWrapper,
        HostPluginInfo,
        HostBasicInfo
    },
    data() {
        return {
            hostId: this.$route.params.hostId,
            basicHostInfo: {},
            basicHostInfoIsLoading: false,
            basicInfo: {},
            basicInfoIsLoading: false,
            scene: undefined
        }
    },
    methods: {
        fetchHostInfo(This) {
            const _this = This
            This.basicHostInfoIsLoading = true
            getHostDetail(This.hostId, true).then((res) => {
                _this.basicHostInfo = res.host_infos[0]
                _this.scene = This.basicHostInfo.scene
            }).catch(err => {
                _this.$message.error(err.response.data.msg)
            }).finally(() => {
                _this.basicHostInfoIsLoading = false
            })
            This.basicInfoIsLoading = true
            getHostDetail(This.hostId, false).then((res) => {
                _this.basicInfo = res.host_infos[0]
            }).catch(err => {
                _this.$message.error(err.response.data.msg)
            }).finally(() => {
                _this.basicInfoIsLoading = false
            })
        },
        reFetchHostInfo() {
            this.$options.methods.fetchHostInfo(this)
        }
    },
    mounted: function () {
        this.$options.methods.fetchHostInfo(this)
    }
}
</script>

<style lang="less" scoped>
</style>
