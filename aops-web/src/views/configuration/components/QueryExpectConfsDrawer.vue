
<template>
  <div>
    <div>主机：{{ host.hostId }}</div>
    <div>IP地址：{{ host.ip }}</div>
    <div>
      <a-collapse>
        <a-collapse-panel v-for="(item,index) in collapseData" :key="index" :header="'配置项：'+item.filePath">
          <a-row type="flex" justify="space-between">
            <a-col :span="22">
              <span class="sx-title">期望配置文本：</span>
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="22" >
            </a-col>
          </a-row>
          <a-row type="flex" justify="space-between">
            <a-col :span="22">
              <a-table :columns="columns" :data-source="item.changeLog" :pagination="false">
                <a slot="action" href="javascript:;">展开</a>
                <template slot="expandedRowRender" slot-scope="record" style="margin: 0">
                  <p>preValue：</p>
                  <p>{{ record.preValue }}</p>
                  <p>postValue：</p>
                  <p>{{ record.postValue }}</p>
                </template>
              </a-table>
            </a-col>
          </a-row>
        </a-collapse-panel>
      </a-collapse>
    </div>
  </div>
</template>

<script>
  import Vue from 'vue'
  import { Collapse } from 'ant-design-vue'
  import { queryExpectedConfs } from '@/api/configuration'
  Vue.use(Collapse)
  export default {
    name: 'QueryExpectConfsDrawer',
    inject: ['onload'], // 来自祖辈们provide中声明的参数、方法
    components: {
      Collapse
    },
    // props: {
    //   host: Object
    // },
    data () {
      return {
        columns: [
          { title: '变更ID', dataIndex: 'changeId', key: 'changeId' },
          { title: '变更时间', dataIndex: 'date', key: 'date' },
          { title: '变更人', dataIndex: 'author', key: 'author' },
          { title: '变更原因', dataIndex: 'changeReason', key: 'changeReason' }
        ],
        collapseIsLoading: false,
        collapseData: [],
        host: []
      }
    },
    watch: {
      activeKey (key) {
      }
    },
    methods: {
      getExpectedConfs (host) {
        const _this = this
        _this.collapseIsLoading = true
        queryExpectedConfs({
          domainName: _this.domainName,
          hostIds: [{ hostId: host.hostId }]
        }).then((res) => {
          _this.collapseData = res.result.expectedConfsData[0].confBaseInfos
          _this.collapseIsLoading = false
        }).catch((err) => {
          _this.$message.error(err.response.data.message)
          _this.collapseIsLoading = false
        })
      }
    },
    mounted: function () {
      const _this = this
      this.onload(function (params) {
        _this.host = params
      })
      this.getExpectedConfs(this.host)
    }
  }
</script>

<style>

</style>
