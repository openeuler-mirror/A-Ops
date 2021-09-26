
<template>
  <a-spin :spinning="collapseIsLoading">
    <div class="conf-section">
      <h1>主机当前配置</h1>
      <div>主机：{{ host.hostId }}</div>
      <div>IP地址：{{ host.ip }}</div>
      <a-collapse>
        <a-collapse-panel v-for="(item) in confs" :key="item.filePath" :header="`配置项：${item.filePath}`">
          <div class="conf-description">
            <a-descriptions title="属性" :column="2">
              <a-descriptions-item label="fileAttr">
                {{ item.fileAttr }}
              </a-descriptions-item>
              <a-descriptions-item label="fileOwner">
                {{ item.fileOwner }}
              </a-descriptions-item>
              <a-descriptions-item label="rpmName">
                {{ item.rpmName }}
              </a-descriptions-item>
              <a-descriptions-item label="spacer">
                {{ item.spacer }}
              </a-descriptions-item>
              <a-descriptions-item label="rpmVersion">
                {{ item.rpmVersion }}
              </a-descriptions-item>
              <a-descriptions-item label="rpmRelease">
                {{ item.rpmRelease }}
              </a-descriptions-item>
            </a-descriptions>
          </div>
          <div class="conf-content">
            <a-row type="flex" justify="space-between" class="conf-content-header">
              <a-col>
                <div class="ant-descriptions-title">文本内容：</div>
              </a-col>
              <a-col v-if="item.syncStatus==='NOT SYNC'">
                <a-button type="primary" @click="showCompareDrawer(item)">
                  差异对比
                </a-button>
              </a-col>
            </a-row>
            <div class="text-container">
              {{ item.confContents }}
            </div>
          </div>
          <template slot="extra" v-if="item.syncStatus==='NOT SYNC'">
            <a-icon type="close-circle" theme="twoTone" two-tone-color="#ff0000" />
            <span style="color: #ff0000">&nbsp;与业务域配置不一致</span>
          </template>
          <template slot="extra" v-if="item.syncStatus==='SYNC'">
            <a-icon type="check-circle" theme="twoTone" two-tone-color="#52c41a" />
            <span>&nbsp;与业务域配置一致</span>
          </template>
        </a-collapse-panel>
      </a-collapse>
    </div>
    <div class="conf-section">
      <h1>主机缺失配置</h1>
      <a-collapse>
        <a-collapse-panel v-for="item in confsNotInHost" :key="item.filePath" :header="`配置项：${item.filePath}`">
          <div class="conf-content">
            <a-row type="flex" justify="space-between" class="conf-content-header">
              <a-col>
                <div class="ant-descriptions-title">文本内容：</div>
              </a-col>
            </a-row>
            <div class="text-container">
              {{ item.contents }}
            </div>
          </div>
          <template slot="extra">
            <a-icon type="exclamation-circle" theme="twoTone" two-tone-color="#f00" />
            <span style="color: #f00">&nbsp;主机中无该项配置</span>
          </template>
        </a-collapse-panel>
      </a-collapse>
    </div>
    <a-drawer
      width="800"
      :visible="compareDrawerVisible"
      @close="closeCompareDrawer"
    >
      <compare-diff-view :comparedConf="comparedConf"/>
    </a-drawer>
  </a-spin>
</template>

<script>
  import Vue from 'vue'
  import { Collapse } from 'ant-design-vue'
  import CompareDiffView from './CompareDiffView'
  import { checkIsDiff } from '../utils/compareContent'

  import { queryRealConfs } from '@/api/configuration'
  Vue.use(Collapse)

  const Diff = require('diff')

  export default {
    name: 'QueryRealConfsDrawer',
    inject: ['onload'], // 来自祖辈们provide中声明的参数、方法
    components: {
      Collapse,
      CompareDiffView
    },
    props: {
      confsOfDomain: {
        type: Array,
        default: () => []
      },
      confsOfDomainLoading: {
        type: Boolean,
        default: false
      }
    },
    data () {
      return {
        domainName: '',
        collapseIsLoading: false,
        confsOfHost: [],
        confs: [],
        confsNotInHost: [],
        host: {},
        compareDrawerVisible: false,
        comparedConf: {}
      }
    },
    watch: {
      confsOfDomainLoading: function () {
        this.compareDiff()
      },
      collapseIsLoading: function () {
        this.compareDiff()
      }
    },
    methods: {
      getRealConfsList (hostId) {
        const _this = this
        _this.collapseIsLoading = true
        queryRealConfs({
          domainName: _this.domainName,
          hostIds: [{ hostId }]
        }).then((res) => {
          _this.confsOfHost = (res && res[0] && res[0].confBaseInfos) || []
        }).catch((err) => {
          if (err.response.data.code !== 400) {
            _this.$message.error(err.response.data.msg)
          }
        }).finally(() => { _this.collapseIsLoading = false })
      },
      compareDiff () {
        const confs = []
        const confsNotInHost = []
        this.confsOfDomain.forEach((confOfDomain) => {
          let confTemp = confOfDomain
          // 域配置返回的filePath前会加‘openEuler：’
          const confOfHostMatched = this.confsOfHost.filter(conf => conf.filePath === confOfDomain.filePath.replace(/openEuler:/, ''))[0]
          if (!confOfHostMatched) {
            confTemp.syncStatus = 'NOT IN HOST'
            confsNotInHost.push(confTemp)
          } else {
            confTemp = {
              ...confOfDomain,
              ...confOfHostMatched
            }
            // 域配置返回的contents最后会多个\n，需要去掉
            const diffByLine = Diff.diffLines(confOfHostMatched.confContents, confOfDomain.contents.replace(/\n$/, ''))
            if (checkIsDiff(diffByLine)) {
              confTemp.syncStatus = 'NOT SYNC'
              confTemp.diffResult = diffByLine
            } else {
              confTemp.syncStatus = 'SYNC'
            }
            confs.push(confTemp)
          }
        })
        this.confs = confs
        this.confsNotInHost = confsNotInHost
      },
      showCompareDrawer (conf) {
        this.comparedConf = conf
        this.compareDrawerVisible = true
      },
      closeCompareDrawer () {
        this.compareDrawerVisible = false
      }
    },
    mounted: function () {
      const _this = this
      this.onload(function (params) {
        _this.domainName = params.domainName
        _this.host = params.host
      })
      this.getRealConfsList(this.host.hostId)
    }
  }
</script>

<style lang="less" scoped>
.conf-section:first-child {
  padding-bottom:20px;
  margin-bottom: 20px;
  border-bottom: 1px solid #eee;
}
.text-container {
  border: 1px solid #ccc;
  border-radius: 3px;
  padding: 10px;
}
.conf-description {
  border-bottom: 1px solid #ccc;
}
.conf-content {
  &-header {
    padding-top:10px;
  }
}
</style>
