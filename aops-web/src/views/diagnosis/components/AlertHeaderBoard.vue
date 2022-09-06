<template>
    <a-row :gutter="16">
      <a-col :xl="6" :lg="8" :md="24" v-if="!onlyInfo">
        <a-card :bordered="false" class="aops-theme alert-count-card">
          <a-row type="flex" align="middle" :gutter="16" class="count-container">
            <a-col>
              <div class="alert-logo">
                <img src="~@/assets/alertLogo.png" width="70">
              </div>
            </a-col>
            <a-col>
              <h3 class="theme-title">告警总数</h3>
              <p class="theme-number">
                <a-spin v-if="countIsLoading" />
                <span v-else>{{ alertCount.toString().replace(/(\d)(?=(?:\d{3})+$)/g, '$1,') }}</span>
              </p>
            </a-col>
          </a-row>
        </a-card>
      </a-col>
      <a-col :xl="onlyInfo? 24 :18" :lg="onlyInfo? 24 : 16" :md="24">
        <a-row>
          <a-col>
            <a-card :bordered="false" :class="`aops-theme alert-info-card${onlyInfo ? ' onlyInfo' : ''}`">
              <div class="alert-info-card-title">
                <span>告警信息统计</span>
                <a-tooltip>
                  <template slot="title">
                    {{ `展示告警信息最多的前${onlyInfo ? 5 : 3}个主机组` }}
                  </template>
                  <a-icon type="question-circle" />
                </a-tooltip>
              </div>
              <a-row :gutter="24" class="data-content">
                <a-col :span="12">
                  <a-table
                  class="alert-info-table"
                  :columns="alertInfoColumns"
                  :data-source="alertInfoResult.slice(0, onlyInfo ? 2 : 1)"
                  :pagination="false"
                  :loading="alertInfoLoading"
                  />
                </a-col>
                <a-col
                    :span="12"
                    :class="getRightTableClass()"
                    v-show="alertInfoResult.slice(onlyInfo ? 2 : 1, onlyInfo ? 5 : 3).length > 0"
                >
                  <a-table
                  class="alert-info-table"
                  :columns="alertInfoColumns"
                  :data-source="alertInfoResult.slice(onlyInfo ? 2 : 1, onlyInfo ? 5 : 3)"
                  :pagination="false"
                  :loading="alertInfoLoading"
                  />
                </a-col>
              </a-row>
              <drawer-view title="告警信息统计" :width="500" :hasButtonOnBottom="false">
                <template slot="click">
                  <div class="show-more-button">查看更多</div>
                </template>
                <template slot="drawerView">
                  <count-alert-info-drawer></count-alert-info-drawer>
                </template>
              </drawer-view>
            </a-card>
          </a-col>
        </a-row>
      </a-col>
    </a-row>
</template>

<script>
// 通过store更行异常告警count数据
import store from '@/store'
import { mapState } from 'vuex'
import CountAlertInfoDrawer from '@/views/diagnosis/components/CountAlertInfoDrawer'
import DrawerView from '@/views/utils/DrawerView'

export default {
    name: 'AlertHeaderBoard',
    components: {
        DrawerView,
        CountAlertInfoDrawer
    },
    props: {
        onlyInfo: {
            type: Boolean,
            default: false
        }
    },
    computed: {
        ...mapState({
          alertCount: state => state.abnormalAlert.alertCount,
          countIsLoading: state => state.abnormalAlert.alertCountLoading,
          alertInfoResult: state => state.abnormalAlert.alertInfoResult,
          alertInfoLoading: state => state.abnormalAlert.alertInfoResultLoading
        }),
        alertInfoColumns() {
            return [
                {
                  dataIndex: 'order',
                  title: '排名',
                  align: 'center',
                  customRender: (text) => {
                    if (text < 1) {
                      return <a-tag class="result-tag hight-light">{ text + 1 }</a-tag>
                    } else {
                      return <span class="result-tag">{ text + 1 }</span>
                    }
                  }
                },
                {
                  title: '主机组名称',
                  dataIndex: 'domain',
                  align: 'center'
                },
                {
                  title: '告警数',
                  dataIndex: 'count',
                  align: 'center',
                  customRender: (text, record, index) => {
                    if (index < 3) {
                      return <span class="result-count high-light">{text}</span>
                    } else {
                      return <span class="result-count">{text}</span>
                    }
                  }
                }
            ]
        }
    },
    methods: {
        getRightTableClass() {
            if (this.onlyInfo) {
                return this.alertInfoResult.slice(2, 5).length > 2 ? 'long-content' : ''
            } else {
                return this.alertInfoResult.slice(1, 3).length > 1 ? 'long-content' : ''
            }
        }
    },
    mounted() {
        // not loading count data if count part is hide.
        !this.onlyInfo && store.dispatch('updateCount')
        store.dispatch('getAlertInfoResult')
    }
}
</script>

<style lang="less" scoped>
.alert-count-card {
  height: 130px;
  margin-bottom: 20px;
  background: url(~@/assets/alertCountbgc.png);
  background-size: 115% auto;
  .count-container {
    margin-top: 4px;
  }
  .theme-title {
    color: #ffffff;
    margin-bottom: 10px;
    font-size: 18px;
    line-height: 18px;
  }
  .theme-number {
    color: #ffffff;
    font-size: 32px;
    font-weight: bold;
    line-height: 32px;
    margin-bottom: 8px;
  }
}
.alert-info-card {
  height: 130px;
  overflow:hidden;
  padding-right: 50px;
  margin-bottom: 20px;
  &.onlyInfo {
    height: 170px;
  }
  /deep/ .ant-card-body {
    padding-left: 15px;
    padding-right: 15px;
    padding-bottom: 0px;
    &>span {
      width: 100%;
    }
  }
  .alert-info-card-title {
    font-size: 18px;
    margin-top: -12px;
    margin-bottom: 6px;
    span {
      margin-right: 5px;
    }
  }
  /deep/ .alert-info-table {
    .ant-table-thead > tr > th {
      padding:5px 10px;
      background: #fff;
      &:first-child {
        padding:5px 0px;
      }
    }
    .ant-table-tbody > tr > td {
      padding:10px 10px;
      border-bottom: 0;
      &:first-child {
        padding:10px 0px;
        span {
          margin-right: 0px;
        }
      }
    }
    .result-tag {
      color: #002fa7;
      font-size: 16px;
      font-weight: 700;
      &.hight-light {
        background: #e0e8fc;
        border-radius: 50%;
      }
    }
    .result-count {
      &.high-light {
        color: #f84b4b;
        font-weight: 500;
      }
    }
    .ant-table-placeholder {
        height:42px;
        border-bottom: 0;
        .ant-empty {
          display: none;
        }
    }
  }
  .data-content {
      .ant-col:not(:first-child).long-content {
        top: -42px;
      }
  }
  .show-more-button{
    position: absolute;
    top: 0;
    right: 0;
    height: 100%;
    width: 40px;
    color: #fff;
    background: #0e41c3;
    line-height: 40px;
    writing-mode: vertical-lr;
    letter-spacing: 0.8em;
    text-align: center;
    border-radius: 0 8px 8px 0;
    cursor:pointer;
    &:hover {
      background: #1D4CB3;
    }
  }
}
</style>
