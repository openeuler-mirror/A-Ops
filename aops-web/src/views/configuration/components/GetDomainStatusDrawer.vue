
<template>
  <div>
    <a-row type="flex" justify="space-between">
      <a-col :span="22">
        <div style="float: left;margin-bottom: 10px">
          <span>主机：{{ host.hostId }}</span>
          <span class="ip-left">{{ host.ip }}</span>
        </div>
        <div style="float: right;margin-bottom: 10px">
          <a-popconfirm
            title="你确定要将当前业务域的配置同步到这台主机吗?"
            ok-text="确认"
            cancel-text="取消"
            @confirm="confirm"
            @cancel="cancel"
          >
            <a-button type="primary" size="small">
              <a-icon type="sync" />全部同步
            </a-button>
          </a-popconfirm>
        </div>
      </a-col>
    </a-row>
    <a-row type="flex" justify="space-between">
      <a-col :span="22">
        <a-table
          rowKey="file_path"
          :columns="columns"
          :data-source="syncStatusList"
          :pagination="false"
          size="small"
          :loading="domainStatusIsLoading"
        >
          <span slot="isSynced" slot-scope="isSynced">
            <span>
              <a-icon v-if="isSynced === statusEnum.sync" type="check-circle" theme="twoTone" two-tone-color="#52c41a"/>
              <a-icon v-if="isSynced === statusEnum.notSync" type="close-circle" theme="twoTone" two-tone-color="#f00"/>
              <a-icon v-if="isSynced === statusEnum.notFound" type="question-circle" theme="twoTone" two-tone-color="#ccc"/>
              {{ statusTitleEnum[isSynced] }}
            </span>
          </span>
        </a-table>
      </a-col>
    </a-row>
  </div>
</template>

<script>
  import { STATUS_ENUM } from '../utils/statusCheckTools'

  const STATUS_TITLE_ENUM = {}
  STATUS_TITLE_ENUM[STATUS_ENUM.sync] = '已同步'
  STATUS_TITLE_ENUM[STATUS_ENUM.notSync] = '未同步'
  STATUS_TITLE_ENUM[STATUS_ENUM.notFound] = '未找到'

  export default {
    name: 'GetDomainStatusDrawer',
    inject: ['onload'], // 来自祖辈们provide中声明的参数、方法
    components: {},
    data () {
      return {
        host: {},
        columns: [
          {
            title: '配置文件',
            dataIndex: 'file_path'
          },
          {
            title: '同步状态',
            dataIndex: 'isSynced',
            scopedSlots: { customRender: 'isSynced' }
          }
        ],
        statusEnum: STATUS_ENUM,
        statusTitleEnum: STATUS_TITLE_ENUM
      }
    },
    props: {
      tableData: {
        type: Array,
        default: () => { return [] }
      },
      domainStatusIsLoading: {
        type: Boolean,
        default: false
      }
    },
    computed: {
      syncStatusList () {
        const matchedHost = this.tableData.filter(hostInfo => hostInfo.hostId === this.host.hostId)[0] || {}
        console.log('list', matchedHost)
        return matchedHost.syncStatusList || []
      }
    },
    methods: {
      confirm (e) {
        this.$message.success('该功能暂未实现')
      },
      cancel (e) {
      }
    },
    mounted: function () {
      const _this = this
      this.onload(function (host) {
        _this.host = host
      })
    }
  }
</script>

<style>
  .ip-left{
    margin-left: 10px;
  }
</style>
