
<template>
  <div>
    <a-row type="flex" justify="space-between">
      <a-col :span="22">
        <div style="float: left;margin-bottom: 10px">
          <span>主机：{{host.hostId}}</span>
          <span class="ip-left">{{host.ip}}</span>
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
        <a-table :columns="columns" :data-source="data" :pagination="false" size="small" >
          <span slot="action">
            <span>
              <a-icon type="close-circle" theme="twoTone" two-tone-color="#ff0000" />
              未同步
            </span>
          </span>
        </a-table>
      </a-col>
    </a-row>
  </div>
</template>

<script>

  export default {
    name: 'GetDomainStatusDrawer',
    inject: ['onload'], // 来自祖辈们provide中声明的参数、方法
    components: {},
    data () {
      return {
        host: [],
        columns: [
          {
            title: '编号',
            dataIndex: 'key'
          },
          {
            title: '同步状态',
            scopedSlots: { customRender: 'action' }
          },
          {
            title: '配置项',
            dataIndex: 'name'
          },
          {
            title: '配置文件',
            dataIndex: 'address'
          }
        ],
        data: [
          {
            key: '1',
            name: 'John Brown',
            address: '/ete/yum.repos.d/openEuler.repo'
          },
          {
            key: '2',
            name: 'Jim Green',
            address: '/ete/yum.repos.d/openEuler.repo'
          },
          {
            key: '3',
            name: 'Joe Black',
            address: '/ete/yum.repos.d/openEuler.repo'
          }
        ]
      }
    },
    methods: {
      confirm (e) {
        console.log(e)
        this.$message.success('Click on Yes')
      },
      cancel (e) {
      }
    },
    mounted: function () {
      const _this = this
      this.onload(function (params) {
        console.log(params)
        _this.host = params
      })
    }
  }
</script>

<style>
  .ip-left{
    margin-left: 10px;
  }
  .sync-button{
  }
</style>
