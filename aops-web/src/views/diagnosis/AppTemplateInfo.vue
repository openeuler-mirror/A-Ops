<template>
  <my-page-header-wrapper>
    <div class="diagnosis-app-template-info">
      <a-card :bordered="false" class="aops-theme">
        <a-row class="app-info-container" type="flex" justify="space-between" align="middle">
          <p class="app-info-icon height-100">
              <img src="~@/assets/app_logo.png">
          </p>
          <a-col :span="16">
            <div class="height-50">
              <h2>{{ appInfo.app_name }}</h2>
              <div>描述：{{ appInfo.description }}</div>
            </div>
          </a-col>
        </a-row>
        <a-row type="flex" justify="end">
            <drawer-view title="创建工作流" :body-style="{ paddingBottom: '80px' }">
              <template slot="click">
                <a-button type="primary">
                  创建工作流
                </a-button>
              </template>
              <template slot="drawerView">
                <create-work-flow :appInfo="appInfo"></create-work-flow>
              </template>
            </drawer-view>
        </a-row>
      </a-card>
      <a-card :bordered="false" class="aops-theme">
        <div id="mountNode"></div>
      </a-card>
    </div>
  </my-page-header-wrapper>
</template>

<script>
import MyPageHeaderWrapper from '@/views/utils/MyPageHeaderWrapper'
import CreateWorkFlow from '@/views/diagnosis/components/CreateWorkFlow'
import G6 from '@antv/g6';
import { getWorkflowAppExtraInfo } from '@/api/check';
import DrawerView from '@/views/utils/DrawerView'
// g6画图数据，自行编写的
const NodeData = {
  nodes: [
    {
      id: 'node1',
      label: '单指标检测',
      x: 150,
      y: 200
    },
    {
      id: 'node2',
      label: '多指标检测',
      x: 450,
      y: 200
    },
    {
      id: 'node3',
      label: '集群故障诊断',
      x: 750,
      y: 200
    }
  ],
  edges: [
    {
      source: 'node1',
      target: 'node2'
    },
    {
      source: 'node2',
      target: 'node3'
    }
  ]
};
const singleItemCheckColum = [
  {
    title: '指标名',
    dataIndex: 'name',
    key: 'name'
  },
  {
    title: '算法',
    dataIndex: 'algorithm',
    key: 'algorithm'
  },
  {
    title: '模型',
    dataIndex: 'model',
    key: 'model'
  }
]
const multiItemCheckColum = [
  {
    title: '算法',
    dataIndex: 'algorithm',
    key: 'algorithm'
  },
  {
    title: '模型',
    dataIndex: 'model',
    key: 'model'
  }
]
export default {
  name: 'AppTemplateInfo',
  components: {
    MyPageHeaderWrapper,
    CreateWorkFlow,
    DrawerView
},
  data() {
    return {
      appInfo: '',
      singleItemCheckColum,
      multiItemCheckColum,
      label: '',
      detail: []
    }
  },
  created() {
      this.app_id = this.$route.params.appId
  },
  mounted: function () {
    this.drawMap()
    this.getAppInformation()
  },
  methods: {
    getAppInformation() {
      const _this = this
      getWorkflowAppExtraInfo(this.app_id)
        .then(function (res) {
          _this.appInfo = res.result
        }).catch(function (err) {
          _this.$message.error(err.response.data.msg)
        }).finally(function () {
        })
    },
    drawMap() {
      const graph = new G6.Graph({
        container: 'mountNode',
        width: 911,
        height: 500,
        defaultNode: {
          type: 'rect',
          size: [120, 50],
          style: {
            fill: '#ffff',
            strokeStyle: '#dadada',
            radius: 3
          }
        },
        defaultEdge: {
          style: {
            stroke: 'black',
            endArrow: {
              path: G6.Arrow.triangle(5, 10, 10),
              d: 10,
              fill: 'black'
            }
          }
        },
        nodeStateStyles: {
          hover: {
            cursor: 'pointer'
          }
        }
      });
      graph.data(NodeData);
      graph.render();
    }
  }
}
</script>
<style lang="less" scoped>
#mountNode {
  width: 100%;
}

/deep/.ant-descriptions-item-colon::after {
  content: '';
}

.label span {
  padding-left: 60px;
}

.app-info-container {
  padding-left: 80px;
  .app-info-icon {
    position: absolute;
    left: 24px;
    top: 24px;
  }
}
</style>
