
<template>
  <div>
    <div>主机：{{host.hostId}}</div>
    <div>IP地址：{{host.ip}}</div>
    <div>
      <a-collapse
        :loading="collapseIsLoading"
      >
        <a-collapse-panel v-for="(item,index) in collapseData" :key="index" :header="'配置项：'+item.path">
          <a-row type="flex" justify="space-between">
            <a-col :span="22">
              <span class="sx-title">属性：</span>
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="11">
              fileAttr：{{item.fileAttr}}
            </a-col>
            <a-col :span="11">
              fileOwner：{{item.fileOwner}}
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="11">
              rpmName：{{item.rpmName}}
            </a-col>
            <a-col :span="11">
              spacer：{{item.spacer}}
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="11">
              rpmVersion：{{item.rpmVersion}}
            </a-col>
            <a-col :span="11">
              rpmRelease：{{item.rpmRelease}}
            </a-col>
          </a-row>
          <hr style="border-color: #fafafa;border-top:1px;" size="1px" noshade=true >
          <a-row type="flex" justify="space-between">
            <a-col :span="22">
              <div style="float: left">
                <span class="sx-title">文本内容：</span>
              </div>
              <div style="float: right;">
                <a href="/configuration/diff-test" target="_blank">
                  <a-button type="primary" size="small">
                    差异对比
                  </a-button>
                </a>
              </div>
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="22" >
              {{item.confContents}}
            </a-col>
          </a-row>
          <template slot="extra" v-if="'1'==item.diff">
            <a-icon type="close-circle" theme="twoTone" two-tone-color="#ff0000" />
            <span style="color: #ff0000">&nbsp;与业务域配置不一致</span>
          </template>
          <template slot="extra" v-if="'2'==item.diff">
            <a-icon type="check-circle" theme="twoTone" two-tone-color="#52c41a" />
            <span>&nbsp;与业务域配置一致</span>
          </template>
          <template slot="extra" v-if="'3'==item.diff">
            <a-icon type="exclamation-circle" theme="twoTone" two-tone-color="#52c41a" />
            <span>&nbsp;业务域中无该项配置</span>
          </template>
        </a-collapse-panel>
      </a-collapse>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue'
  import { Collapse } from 'ant-design-vue'
  import { queryRealConfs } from '@/api/configuration'
  Vue.use(Collapse)
  export default {
    name: 'QueryRealConfsDrawer',
    inject: ['onload'], // 来自祖辈们provide中声明的参数、方法
    components: {
      Collapse
    },
    // props: {
    //   host: Object
    // },
    data () {
      return {
        collapseIsLoading: false,
        collapseData: [],
        host: []
      }
    },
    watch: {
      activeKey (key) {
        console.log(key)
      }
    },
    methods: {
      getRealConfsList (record) {
        const _this = this
        _this.collapseIsLoading = true
        queryRealConfs({
          uid: '123',
          domainName: _this.domainName,
          hostIds: [{ hostId: record.hostId }]
        }).then((res) => {
          _this.collapseData = res.result.realConfsData[0].confBaseInfos
          _this.collapseIsLoading = false
        }).catch((err) => {
          _this.$message.error(err.response.data.message)
          _this.collapseIsLoading = false
        })
      },
      setDiff () {
        const _this = this
        _this.collapseData.forEach(function (item) {
            item.diff = false
        })
        console.log(_this.collapseData)
      }
    },
    mounted: function () {
      const _this = this
      this.onload(function (params) {
        console.log(params)
        _this.host = params
      })
      this.getRealConfsList(this.host)
    }
  }
</script>

<style>
.sx-title{
  font-weight: 700;
}
.sx-div{
  float:left;
  width: 45%;
  margin-bottom: 8px;
  margin-left: 14px;
}
</style>
