<template>
  <page-header-wrapper>
    <a-card :border="false" class="aops-theme">
      <div class="header">
        <h4 v-show="graphIsDoingLayout">图形布局中，请稍等 <a-spin size="small" /></h4>
        <div class="level-controller">
          <div
            :class="`level-controller-btn${level.type === visibleLevel ? ' active' : ''}`"
            v-for="(level,idx) in levelOrders"
            :key="idx"
            @click="changeLevel(level.type)"
          >
            <img :src="level.src" alt="" style="width:18px;vertical-align:middle;"><span style="margin-left:5px;">{{ level.text }}</span>
          </div>
          <div><a-icon type="switcher" :rotate="90" style="margin-bottom:15px;" /> 层级</div>
        </div>
      </div>
      <a-spin :spinning="dataLoading" size="large">
        <div v-for="(level,idx) in levelOrders" :key="idx">
          <node-graph-container
            v-show="level.type === visibleLevel"
            :isShow="level.type === visibleLevel"
            :containerId="`graph-container-${level.type}`"
            :entitiesData="{
              nodes: entitiesListByLevel[level.type],
              edges: edgesListByLevel[level.type]
            }"
            :dataReady="dataReady"
            :selectedEntityId="selectedNodeId"
            :linkMap="edgesMapByLevel[level.type]"
            @nodeClicked="nodeClicked"
            @addResizeFunction="addResizeFunction"
            @showVerticalMap="showVerticalMap"
          />
        </div>
      </a-spin>
    </a-card>
    <vertical-map-drawer
      :selectedNodeId="selectedEntityId"
      :treeData="verticalTreeData"
      :visible="verticalDrawerVisible"
      @close="handleVerticalDrawerClose"
      @treeNodeClicked="treeNodeClicked"
    />
  </page-header-wrapper>
</template>

<script>
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
// 层级节点组件
import NodeGraphContainer from './components/NodeGraphContainer'
// 垂直层级抽屉组件
import VerticalMapDrawer from './components/VerticalMapDrawer'

import { getTopoData } from '@/api/topo'
// 测试时，打开一下测试数据注释
// import { testData } from '@/mock/topoTestJson'

import { levelOrders, relationTypes } from './config.js'
import { getParentId, gerChildrenIds, getRelatedEdges, getRoot, getTreeData } from './utils'

export default {
  name: 'NetworkTopoDiagram',
  components: {
    PageHeaderWrapper,
    NodeGraphContainer,
    VerticalMapDrawer
  },
  data () {
    return {
      levelOrders,
      // 当前展示的层级
      visibleLevel: 'PROCESS',

      graphData: {},
      dataLoading: false,
      graphIsDoingLayout: false,
      dataReady: false,

      // hashMap for all entities
      nodeMap: {},
      edgeMap: {},
      // enities list and map in each level
      entitiesMapByLevel: {},
      entitiesListByLevel: {},
      edgesMapByLevel: {},
      edgesListByLevel: {},

      // set id when change level by click pannel item
      selectedEntityId: '',
      // resize events
      resizeFuncs: [],

      // verticalDataDisplay
      verticalDrawerVisible: false,
      verticalTreeData: {},
      selectedNodeId: null,

      iconsrc: ''
    }
  },
  methods: {
    // 准备数据
    setGraphData (dataList) {
      const _this = this
      // put entity data to nodeMap and entitiesListByLevel/ entitiesMapByLevel
      dataList.forEach(function (entity) {
        if (!entity.entityid) {
          return
        }
        const tempNode = entity
        // id和label是绘图时需要使用的
        tempNode.id = entity.entityid
        // tempNode.label = entity.name
        tempNode._label = entity.name
        tempNode.label = undefined
        tempNode.type = entity.type
        if (tempNode.type === 'host') {
          _this.iconsrc = '/主机.png'
        } else if (tempNode.type === 'container') {
          _this.iconsrc = '/容器.png'
        } else if (tempNode.type === 'task') {
          _this.iconsrc = '/进程.png'
        } else if (tempNode.type === 'tcp_link') {
          _this.iconsrc = '/TCP连接.png'
        } else if (tempNode.type === 'ipvs_link') {
          _this.iconsrc = '/IPVS连接.png'
        }
        // tempNode._type = entity.type
        tempNode.icon = {
          show: true,
          img: _this.iconsrc,
          width: 40,
          height: 40
        }
        // tempNode.type = undefined
        _this.nodeMap[entity.entityid] = tempNode

        const eLevel = entity.level
        if (eLevel) {
          if (!_this.entitiesListByLevel[eLevel]) {
            _this.entitiesListByLevel[eLevel] = []
            _this.entitiesMapByLevel[eLevel] = {}
          }

          _this.entitiesListByLevel[eLevel].push(tempNode)
          _this.entitiesMapByLevel[eLevel][tempNode.id] = tempNode
        }
      })
      // deal data in order by level
      levelOrders.forEach(function (levelInfo) {
        _this.entitiesListByLevel[levelInfo.type].forEach(function (entity) {
          // set parent and children of each entity
          const parentId = getParentId(entity)
          if (parentId) {
            entity.parentId = parentId
          }
          const childrenIds = gerChildrenIds(entity)
          if (childrenIds.length > 0) {
            entity.children = []
            childrenIds.forEach(function (childId) {
              _this.nodeMap[childId] && entity.children.push(_this.nodeMap[childId])
            })
          }

          // get edge on each level
          const relatedEdgeList = getRelatedEdges(entity)
          if (!_this.edgesListByLevel[levelInfo.type]) {
            _this.edgesListByLevel[levelInfo.type] = []
            _this.edgesMapByLevel[levelInfo.type] = {}
          }
          entity.startOfLinks = []
          entity.endOfLinks = []
          relatedEdgeList.forEach(function (edgeInfo) {
            // set related edge id to entity
            if (edgeInfo.source === entity.entityid) {
              entity.startOfLinks.push(edgeInfo.id)
            } else {
              entity.endOfLinks.push(edgeInfo.id)
            }
            // add edge info to edgeMap and edgesListByLevel/edgesMapByLevel
            if (_this.edgeMap[edgeInfo.id]) return
            // if the type of link is 'peer', then only put one direction of link in graph
            if (edgeInfo.relation_id === relationTypes.peer) {
              if (_this.edgeMap[`peer$${edgeInfo.target}$${edgeInfo.source}`]) return
            }
            _this.edgeMap[edgeInfo.id] = edgeInfo
            _this.edgesListByLevel[levelInfo.type].push(edgeInfo)
            _this.edgesMapByLevel[levelInfo.type][edgeInfo.id] = edgeInfo
          })
        })
      })
      this.dataReady = true
    },
    getGraphDataFromRemote () {
      const _this = this
      this.dataLoading = true
      // 测试时，打开下方注释。
      // _this.setGraphData(testData.entities)
      getTopoData().then(res => {
        _this.setGraphData(res.entities || [])
      }).catch(err => {
        if (err.response && err.response.data && err.response.data.status === 500) {
          _this.$message.error('服务器错误，请稍后再试')
        }
        console.warn(err)
        _this.$message.error(err.response.data.msg || err.response.data.title || '获取架构数据失败，请稍后再试')
      }).finally(() => {
        _this.dataLoading = false
      })
    },
    addResizeFunction (func) {
      this.resizeFuncs.push(func)
    },
    setResizeFunciton () {
      if (typeof window !== 'undefined') {
        const _this = this
        window.onresize = () => {
          _this.resizeFuncs.forEach(funcs => {
            funcs()
          })
        }
      }
    },
    changeLevel (level) {
      this.visibleLevel = level
    },
    nodeClicked (entityInfo) {
    },
    showVerticalMap (nodeId) {
      const root = getRoot(this.nodeMap[nodeId], this.nodeMap)
      this.selectedEntityId = nodeId
      this.verticalTreeData = getTreeData(root)
      this.verticalDrawerVisible = true
    },
    // verticalDrawerControl
    handleVerticalDrawerClose () {
      this.verticalDrawerVisible = false
    },
    treeNodeClicked (nodeId) {
      if (!this.nodeMap[nodeId]) {
        return
      }
      this.selectedNodeId = nodeId
      this.verticalDrawerVisible = false
      this.changeLevel(this.nodeMap[nodeId].level)
    }
  },
  mounted: function () {
    this.getGraphDataFromRemote()
    this.setResizeFunciton()
  }
}
</script>

<style lang="less" scoped>
  .header {
    height: 24px;
    line-height: 24px;
  }
  .container {
    min-height: 500px;
  }
  .level-control-pannel {
    position: absolute;
    top: 20px;
    right: 20px;
  }

  .level-controller {
    z-index: 99;
    position: absolute;
    left: 20px;
    right: 20px;
    width: 100px;
    text-align: center;
    background: #fff;
    display: flex;
    flex-direction: column-reverse;
    &-btn {
      cursor: pointer;
      height: 30px;
      margin-bottom:4px;
      &:hover {
        font-weight: bold;
      }
      &.active {
        color: #3265F2;
      }
    }
  }
</style>
