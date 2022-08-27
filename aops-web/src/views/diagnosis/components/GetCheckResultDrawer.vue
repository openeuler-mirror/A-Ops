<template>
  <div id="pageBox" style="width: 100%;height: 100%;overflow:hidden" @mousewheel="scrollEvent" @DOMMouseScroll="scrollEvent">
    <a-table
      rowKey="host_id"
      :bordered="true"
      :columns="columns"
      :data-source="hostList"
      :loading="isLoading"
      :scroll="{ y: scrollBoxHeight }"
      :pagination="false"></a-table>
    <div v-if="total === hostList.length" class="loadMsg">没有更多了...</div>
    <div v-else id="scrollDown">
      <div class="container">
        <div class="chevron"></div>
        <div class="chevron"></div>
        <div class="chevron"></div>
      </div>
    </div>
  </div>
</template>

<script>
// this component is abandoned
  import { getResultCount } from '@/api/check'

  export default {
    name: 'GetCheckResultDrawer',
    data () {
      return {
        columns,
        scrollBoxHeight: 240,
        isLoading: false,
        total: -1,
        currentPage: 1,
        pageSize: 10,
        hostList: []
     }
    },
    mounted: function () {
      const that = this
      this.loadHostList()
      this.scrollBox().onscroll = this.scrollEvent
      setTimeout(function () { // 重置表格最大显示高度，与页面高度匹配
        that.scrollBoxHeight = window.document.querySelector('#pageBox').offsetHeight - window.document.querySelector('#pageBox .ant-table-header').offsetHeight - 20
      })
    },
    methods: {
      scrollBox () {
        return window.document.querySelector('#pageBox .ant-table-body')
      },
      // 此方法兼容鼠标滚轮事件和滚动条事件
      scrollEvent (v1) {
        if (this.isLoading) return
        // 兼容火狐和其它浏览器，判断鼠标滚轮滚动方向
        if ((v1.detail || v1.wheelDelta) === 120 || (v1.detail || v1.wheelDelta) === -3) return
        const scrollBox = this.scrollBox()
        if (scrollBox.scrollTop + scrollBox.clientHeight === scrollBox.scrollHeight) {
          this.loadHostList()
        }
      },
      loadHostList () {
        if (this.total < 0 || this.total > this.hostList.length) {
          const that = this
          this.isLoading = true
          getResultCount({ sort: 'count', direction: 'desc', perPage: this.pageSize, page: this.currentPage++ }).then(function (data) {
            that.hostList.push(...data.results)
            that.total = data.total_count
          }).catch(function (err) {
            that.$message.error(err.response.data.msg)
          }).finally(function () { that.isLoading = false })
        }
      }
    }
  }

  const columns = [
    {
      title: '排名',
      align: 'center',
      width: 70,
      customRender: (text, record, index) => `${index + 1}`
    },
    {
      title: '主机名',
      dataIndex: 'hostName'
    },
    {
      title: 'IP地址',
      dataIndex: 'ip'
    },
    {
      title: '异常数',
      dataIndex: 'count'
    }
  ]
</script>

<style>
  .ant-drawer-body{height: calc(100% - 110px)!important;}
  .loadMsg{margin-top: 12px;width: 100%;text-align: center;color: #999;font-size: 12px}
  #scrollDown{
    display: flex;
    position: relative;
    width: 100%;
    margin-top: 5px;
  }
  .container {
    position: relative;
    width: 100%;
    height: 45px;
  }
  .chevron {
    position: absolute;
    left: calc(50% - 14px);
    width: 28px;
    height: 3px;
    opacity: 0;
    transform: scale3d(0.5, 0.5, 0.5);
    animation: move 3s ease-out infinite;
  }
  .chevron:first-child {
    animation: move 3s ease-out 1s infinite;
  }
  .chevron:nth-child(2) {
    animation: move 3s ease-out 2s infinite;
  }
  .chevron:before,
  .chevron:after {
    content: ' ';
    position: absolute;
    top: 0;
    height: 100%;
    width: 51%;
    background:#ccc;
  }
  .chevron:before {
    left: 0;
    transform: skew(0deg, 30deg);
  }
  .chevron:after {
    right: 0;
    width: 50%;
    transform: skew(0deg, -30deg);
  }
  @keyframes move {
    25% {
      opacity: 1;
    }
    33% {
      opacity: 1;
      transform: translateY(20px);
    }
    67% {
      opacity: 1;
      transform: translateY(25px);
    }
    100% {
      opacity: 0;
      transform: translateY(35px) scale3d(0.5, 0.5, 0.5);
    }
  }
</style>
