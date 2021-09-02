
<template>
  <my-page-header-wrapper>
    <div style="width: 100%;height: 180px">
      <div style="width: 220px;height:100%;float: left;background: #fff">
        <div style="width: 100%;height: calc(100% - 35px)">
          <div style="height: 100%;width: 75px;float: left;position:relative;">
            <a-avatar :size="64" icon="database" style="background: #1890ee;position: absolute;top: 50%;left: 50%;margin-top: -32px;margin-left: -32px"/>
          </div>
          <div style="height: 100%;width: calc(100% - 75px);float: left;position:relative;">
            <div class="content">
              <div style="color: #999;">异常检测规则数量</div>
              <div style="color: #333;font-size: 32px;line-height: 1em">{{ ('1345' || 0).toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,')}}</div>
            </div>
          </div>
        </div>
        <div style="width: 100%;height: 34px;line-height: 32px;color: #fff;padding: 0 2px">
          <drawer-view title="新建异常检测规则">
            <template slot="click">
              <div class="newRule" style="float: left">
                <a-icon type="file-add" style="margin-right: 5px"/>新建规则
              </div>
            </template>
            <template slot="drawerView">
              <add-abnormal-check-rule-drawer></add-abnormal-check-rule-drawer>
            </template>
          </drawer-view>
        </div>
      </div>
      <drawer-view title="异常检测结果统计">
        <template slot="click">
          <div class="showAllResult">查看全部结果</div>
        </template>
        <template slot="drawerView">
          <get-check-result-drawer></get-check-result-drawer>
        </template>
      </drawer-view>
      <div style="width: calc(100% - 275px);height: 100%;float: right;background: #fff;padding: 5px;padding-top: 10px">
        <a-row style="width: 100%;height: 100%">
          <a-col style="height: 100%;" :span="8">
            <div style="width: 100%;height: 50%;">
              <div style="padding-left: 20px;font-size: 18px;line-height: 40px;height: calc(100% - 30px);color: #000;font-weight: bold">异常检测结果统计</div>
              <a-row style="color: #999;line-height: 30px">
                <a-col :span="3" style="text-align: center">排名</a-col>
                <a-col :span="15">主机名IP地址</a-col>
                <a-col :span="6">异常数</a-col>
              </a-row>
            </div>
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(0, 2)" :key="index">
              <a-col :span="3"><a-tag style="background: #1890ee;color: #fff;border-color:#1890ee">{{ index+1 }}</a-tag></a-col>
              <a-col :span="15">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
          <a-col style="float: left;height: 100%;" :span="8">
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(2, 6)" :key="index">
              <a-col :span="3"><a-tag>{{ index+3 }}</a-tag></a-col>
              <a-col :span="15">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
          <a-col style="float: left;height: 100%;" :span="8">
            <a-row class="myRow" v-for="(item,index) in resultCountList.slice(6, 10)" :key="index">
              <a-col :span="3"><a-tag>{{ index+7 }}</a-tag></a-col>
              <a-col :span="15">
                <p style="margin: 0">{{ item.hostName }}</p>
                <p style="margin: 0">{{ item.ip }}</p>
              </a-col>
              <a-col :span="6">{{ item.count }}项</a-col>
            </a-row>
          </a-col>
        </a-row>
      </div>
    </div>
    <a-card style="width: 100%;float: left;margin-top: 10px">
      <div style="font-weight: bold;font-size: 18px;margin-top: -12px;margin-bottom: 10px">异常检测规则列表</div>
      <a-table
        :columns="columns"
        :data-source="resultList"
        :pagination="pagination"
        @change="handleTableChange"
        :loading="tableIsLoading"
        :expandIconAsCell="false"
        :expandIconColumnIndex="1">
        <span slot="action" slot-scope="result">
          <a @click="openEdit(result)">编辑</a>
          <a-divider type="vertical" />
          <a-popconfirm
            title="确认要删除这条异常检测记录?"
            ok-text="确认"
            cancel-text="取消"
            @confirm="deleteResult(result)"
          ><a href="#">删除</a></a-popconfirm>
          <a-divider type="vertical" />
          <a><a-icon type="down" /></a>
        </span>
        <p slot="expandedRowRender" slot-scope="result" style="margin: 0">
          {{ result }}
        </p>
      </a-table>
    </a-card>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import DrawerView from '@/views/utils/DrawerView'
import GetCheckResultDrawer from '@/views/diagnosis/components/GetCheckResultDrawer'
import AddAbnormalCheckRuleDrawer from '@/views/diagnosis/components/AddAbnormalCheckRuleDrawer'

export default {
  name: 'RuleManagement',
  components: {
    MyPageHeaderWrapper,
    DrawerView,
    AddAbnormalCheckRuleDrawer,
    GetCheckResultDrawer
  },
  mounted: function () {
    for (var i = 0; i < 10; i++) {
      this.resultCountList.push({
        hostName: 'Host' + new Date().getTime(),
        ip: '127.0.0.1',
        count: parseInt(Math.random() * 100)
      })
    }
    this.resultCountList.sort(function (a, b) { return a.count < b.count })
    this.getResultList({})
  },
  computed: {
    resultCountListPart_1 () {
      return ''
    }
  },
  data () {
    return {
      filters: null,
      sorter: null,
      tableIsLoading: false,
      columns,
      resultCountList: [],
      resultList: [],
      pagination: {
        current: 1,
        pageSize: 5,
        showSizeChanger: true,
        showQuickJumper: true,
        change: this.paginationChange
      }
    }
  },
  methods: {
    paginationChange (page, pageSize) {
      // this.getResultList({})
    },
    handleTableChange (pagination, filters, sorter) {
      // 存储翻页状态
      this.pagination = pagination
      this.filters = filters
      this.sorter = sorter
      // 出发排序、筛选、分页时，重新请求主机列表
      this.getResultList({})
    },
    getResultList ({ p, f, s }) {
      console.log(this.pagination.current)
      this.resultList = []
      for (var i = 0; i < 20; i++) {
        this.resultList.push({
          id: new Date().getTime(),
          hostName: 'Host' + new Date().getTime(),
          ip: '127.0.0.1',
          checkItems: 'checkItems TEST...',
          condition: 'condition TEST...',
          result: 'result TEST...',
          tags: '标签一、标签二、标签三'
        })
      }
    },
    deleteResult (result) {
      console.log('delete:' + JSON.stringify(result))
      this.$message.success('记录删除成功')
    }
  }
}

const columns = [
  {
    title: '序号',
    dataIndex: 'index',
    key: 'index',
    align: 'center',
    width: 70,
    customRender: (text, record, index) => `${index + 1}`
  },
  {
    dataIndex: 'checkItems',
    key: 'checkItems',
    title: '检测项'
  },
  {
    dataIndex: 'condition',
    key: 'condition',
    title: '检测条件'
  },
  {
    dataIndex: 'result',
    key: 'result',
    title: '检测结果描述'
  },
  {
    dataIndex: 'tags',
    key: 'tags',
    title: '数据标签'
  },
  {
    title: '操作',
    scopedSlots: { customRender: 'action' }
  }
]

</script>

<style lang="less" scoped>
.content{position: absolute;width: 100%;height: 60px;top: 50%;margin-top: -30px;padding-left: 5px}
.newRule{width: calc(100% - 2px);height: 100%;background:#1890ee;text-align: center;cursor: pointer}
.newRule:hover{background: #0075d0;}
.showAllResult{width: 35px;height: 100%;background:#1890ee;float: right;border: 1px solid #fff;color: #fff;padding: 15px 5px;text-align: center;cursor: pointer}
.showAllResult:hover{background: #0075d0;}
.myRow{height: calc(25% - 5px);width: 100%;margin-bottom:5px}
.myRow>.ant-col:nth-child(1){position: relative;height: 100%}
.myRow>.ant-col:nth-child(1) .ant-tag{border-radius: 50%;padding: 0 1px 0 0;width: 24px;height: 24px;line-height: 22px;text-align: center;position: absolute;top: 50%;left: 50%;margin-top: -12px;margin-left: -12px}
.myRow>.ant-col:nth-child(2){line-height: 1.2em!important;}
.myRow>.ant-col:nth-child(3){line-height: 30px}
</style>
