<template>
  <a-spin :spinning="dataLoading || graphIsDoingLayout" size="large">
    <div :id="containerId" class="container" />
    <div class="controller">
      <a-row type="flex" justify="center">
        <a-button @click="control('fitview')"><a-icon type="border-outer" /></a-button>
        <a-button @click="control('zoomin')"><a-icon type="zoom-in" /></a-button>
        <a-button @click="control('zoomout')"><a-icon type="zoom-out" /></a-button>
        <a-button @click="control('focus')"><a-icon type="border-inner" /></a-button>
        <a-button @click="control('showVerticalMap')" :disabled="!selectedNodeCache"><a-icon type="branches" /></a-button>
      </a-row>
    </div>
  </a-spin>
</template>

<script>
import G6 from '@antv/g6'
import { getRemoteNodeIds } from '../utils'

const subjectColors = [
  '#5F95FF', // blue，for normal node and link
  '#61DDAA', // light green, for link
  '#78D3F8', // light blue, for current node
  '#F08BB4' // red, for Error state
]
const backColor = '#fff'
const theme = 'default'
const disableColor = '#777'
const colorSets = G6.Util.getColorSetsBySubjectColors(
  subjectColors,
  backColor,
  theme,
  disableColor
)

export default {
  name: 'NodeGraphContainer',
  components: {
  },
  data () {
    return {
      nodes: [],
      edges: [],
      graph: {},
      graphIsDoingLayout: false,

      // data for dispaly
      displayInfo: {},
      // chache of selected node
      selectedNodeCache: null,
      selectedLinkCache: [],
      selectedRemoteNodesCache: [],
      toggleNodeCache: null,
      initailized: false, // 是否经过初始化了数据的变量
      addSizeEvents: false,
      btnfit: false // 是否开启了
    }
  },
  props: {
    containerId: {
      type: String,
      default: 'graph-container'
    },
    isShow: {
      type: Boolean,
      default: true
    },
    entitiesData: {
      type: Object,
      default: () => {
        return {
          nodes: [],
          edges: []
        }
      }
    },
    dataReady: {
      type: Boolean,
      default: false
    },
    dataLoading: {
      type: Boolean,
      default: false
    },
    linkMap: {
      type: Object,
      default: () => {}
    },
    selectedEntityId: {
      type: String,
      default: ''
    }
  },
  watch: {
    // 第一次加载时，需要准备好数据后触发绘图。
    dataReady: function () {
      const _this = this
      if (!this.dataReady) return
      if (!this.isShow) return
      this.nodes = this.entitiesData.nodes || []
      this.edges = this.entitiesData.edges || []
      if (!this.initailized) {
        setTimeout(function () {
          _this.initialGraph()
        }, 100)
      }
    },
    // 当当前层级组件显示时触发
    isShow () {
      if (this.isShow) {
        if (!this.initailized) {
          this.nodes = this.entitiesData.nodes || []
          this.edges = this.entitiesData.edges || []
          this.initialGraph()
        }
        // adjust container size when current level is showed
        const container = document.getElementById(this.containerId)
        if (!this.graph || this.graph.get('destroyed')) return
        if (!container || !container.clientWidth || !container.clientHeight) return
        this.graph.changeSize(container.clientWidth, container.clientHeight)
        // 点亮当前已选择的节点
        if (this.selectedEntityId) {
          const node = this.graph.findById(this.selectedEntityId)
          if (!node) return
          this.highlightNodeWithConnections(node)
        }
      }
    }
  },
  methods: {
    onLayoutEnd () {
      this.graphIsDoingLayout = false
      // 讲画布中的节点与画布进行自适应占满画布
      // this.graph.fitView()
      // add default state to avoid edge state bug
      this.graph.getEdges().forEach(edge => {
        this.graph.setItemState(edge, 'defaultState', true)
      })
      this.setErrorStateForAllEntity()
    },
    nodeClicked (entityInfo) {
      this.$emit('nodeClicked', entityInfo)
    },
    // 为当前节点和与其链接的节点设置选中状态
    highlightNodeWithConnections (node) {
      const model = node.getModel()
      this.clearSelectedStateByCache()
      // set select node state
      if (!node.hasState('error')) {
        this.graph.setItemState(node, 'nodeClickSelected', true)
      }
      this.selectedNodeCache = node

      // set remote node and link state
      const endOfLinks = model.endOfLinks || []
      const startOfLinks = model.startOfLinks || []
      const links = startOfLinks.concat(endOfLinks)
      const highLightEdgeList = this.graph.findAll('edge', edge => {
        return links.indexOf(edge.get('model').id) > -1
      })
      const nodes = getRemoteNodeIds(startOfLinks, endOfLinks, this.linkMap)
      const highLightNodeList = this.graph.findAll('node', node => {
        return nodes.indexOf(node.get('model').id) > -1
      })

      highLightEdgeList.forEach(edge => {
        if (!edge.hasState('error')) {
          this.graph.setItemState(edge, 'nodeClickSelectedHighLight', true)
        } else {
          this.graph.setItemState(edge, 'errorSelected', true)
        }
      })
      highLightNodeList.forEach(node => {
        if (!node.hasState('error')) {
          this.graph.setItemState(node, 'nodeClickSelectedRemote', true)
        }
      })
      this.selectedLinkCache = highLightEdgeList
      this.selectedRemoteNodesCache = highLightNodeList
    },
    // 清除选择节点和相关节点的选择状态
    clearSelectedStateByCache () {
      if (this.selectedNodeCache) {
        this.graph.clearItemStates(this.selectedNodeCache, 'nodeClickSelected')
        this.selectedNodeCache = null
      }
      if (this.selectedLinkCache) {
        this.selectedLinkCache.forEach(edge => {
          this.graph.clearItemStates(edge, ['nodeClickSelectedHighLight', 'edgeClickSelectedHighLight', 'errorSelected'])
        })
        this.selectedLinkCache = []
      }
      if (this.selectedRemoteNodesCache) {
        this.selectedRemoteNodesCache.forEach(node => {
          this.graph.clearItemStates(node, 'nodeClickSelectedRemote')
        })
        this.selectedRemoteNodesCache = []
      }
    },
    // 为错误状态的节点设置error状态（暂未使用，根据实际提供的数据情况修改）
    setErrorStateForAllEntity () {
      const edgesWithError = this.graph.findAll('edge', edge => {
        return edge.get('model').anomaly && edge.get('model').anomaly.status === 'ANOMALY_YES'
      })
      edgesWithError.forEach(edge => {
        this.graph.setItemState(edge, 'error', true)
      })
    },
    // 工具栏控制方法
    control (operat) {
      switch (operat) {
        case 'fitview':
          this.graph.fitView()
          break
        case 'zoomin':
          this.graph.zoom(1.15, { x: document.getElementById(this.containerId).scrollHeight, y: document.getElementById(this.containerId).scrollHeight })
          break
        case 'zoomout':
          this.graph.zoom(0.85, { x: document.getElementById(this.containerId).scrollHeight, y: document.getElementById(this.containerId).scrollHeight })
          break
        case 'focus':
          const item = this.selectedNodeCache || this.selectedLinkCache[0]
          this.graph.focusItem(item, true, {
            easing: 'easeCubic',
            duration: 400
          })
          break
        case 'showVerticalMap':
          this.$emit('showVerticalMap', this.selectedNodeCache.get('model').id)
          break
      }
    },
    initialGraph () {
      const tooltip = new G6.Tooltip({
        itemTypes: ['node'],
        getContent(e) {
           const outDiv = document.createElement('div');
           outDiv.style.width = 'fit-content';
           outDiv.innerHTML = `
             <h4>节点名称: ${e.item.getModel().name}</h4>
             <li>属性名: ${e.item.getModel().attrs[0].key}</li>
             <li>属性值: ${e.item.getModel().attrs[0].value}</li>
             <li>属性类型: ${e.item.getModel().attrs[0].vtype}</li>`
           return outDiv
        }
      })

      const _this = this
      const container = document.getElementById(this.containerId)
      const width = container.clientWidth
      const height = (container.clientHeight || 500) - 20
      this.graph = new G6.Graph({
        container: container,
        width: width,
        height: height,
        layout: {
          type: 'force',
          preventOverlap: true,
          linkDistance: 160,
          nodeStrength: 1,
          edgeStrength: 1,
          nodeSpacing: 40,
          alphaMin: 0.08,
          onLayoutEnd: this.onLayoutEnd
        },
        defaultNode: {
          // type: 'diamond',
          size: 80,
          style: {
            fill: colorSets[0].mainFill,
            stroke: colorSets[0].mainStroke,
            shadowBlur: 10,
            cursor: 'pointer'
          },
          labelCfg: {
            style: {
              fill: '#000'
            }
          }
        },
        defaultEdge: {
          style: {
            endArrow: true,
            stroke: colorSets[0].mainStroke,
            shadowBlur: 10,
            cursor: 'pointer'
          }
        },
        fitView: this.btnfit,
        modes: {
          default: ['drag-canvas', 'zoom-canvas',
            {
              type: 'drag-node',
              onlyChangeComboSize: false
            }
          ]
        },
        plugins: [tooltip],
        nodeStateStyles: {
          hoverFocus: {
            fill: colorSets[2].activeFill,
            stroke: colorSets[2].activeStroke,
            shadowColor: colorSets[2].activeStroke
          },
          hoverRemote: {
            fill: colorSets[0].activeFill,
            stroke: colorSets[0].activeStroke,
            shadowColor: colorSets[0].activeStroke
          },
          nodeClickSelected: {
            fill: colorSets[2].selectedFill,
            stroke: colorSets[2].selectedStroke,
            shadowColor: colorSets[2].selectedStroke
          },
          nodeClickSelectedRemote: {
            fill: colorSets[0].selectedFill,
            stroke: colorSets[0].selectedStroke,
            shadowColor: colorSets[0].selectedStroke
          }
        },
        edgeStateStyles: {
          hoverHighLight: {
            stroke: colorSets[1].activeStroke,
            shadowColor: colorSets[1].activeStroke
          },
          edgeClickSelectedHighLight: {
            stroke: colorSets[1].selectedStroke,
            shadowColor: colorSets[1].selectedStroke
          },
          nodeClickSelectedHighLight: {
            stroke: colorSets[1].selectedStroke,
            shadowColor: colorSets[1].selectedStroke
          },
          error: {
            stroke: colorSets[3].mainStroke,
            lineDash: 5
          },
          errorHover: {
            stroke: colorSets[3].activeStroke,
            shadowColor: colorSets[3].activeStroke
          },
          errorSelected: {
            stroke: colorSets[3].selectedStroke,
            shadowColor: colorSets[3].selectedStroke
          }
        }
      })
      // 配置事件
      this.graph.on('node:mouseenter', function (evt) {
        const node = evt.item
        const model = node.getModel()

        const endOfLinks = model.endOfLinks || []
        const startOfLinks = model.startOfLinks || []
        const links = startOfLinks.concat(endOfLinks)
        const highLightEdgeList = _this.graph.findAll('edge', edge => {
          return links.indexOf(edge.get('model').id) > -1
        })
        const nodes = getRemoteNodeIds(startOfLinks, endOfLinks, _this.linkMap)
        const highLightNodeList = _this.graph.findAll('node', node => {
          return nodes.indexOf(node.get('model').id) > -1
        })

        highLightEdgeList.forEach(edge => {
          _this.graph.setItemState(edge, 'hoverHighLight', true)
        })
        _this.graph.setItemState(node, 'hoverFocus', true)
        highLightNodeList.forEach(node => {
          _this.graph.setItemState(node, 'hoverRemote', true)
        })
      })
      this.graph.on('node:mouseleave', function (evt) {
        const node = evt.item
        const model = node.getModel()
        // set remote and link state
        const endOfLinks = model.endOfLinks || []
        const startOfLinks = model.startOfLinks || []
        const links = startOfLinks.concat(endOfLinks)
        const highLightEdgeList = _this.graph.findAll('edge', edge => {
          return links.indexOf(edge.get('model').id) > -1
        })
        const nodes = getRemoteNodeIds(startOfLinks, endOfLinks, _this.linkMap)
        const highLightNodeList = _this.graph.findAll('node', node => {
          return nodes.indexOf(node.get('model').id) > -1
        })

        highLightEdgeList.forEach(edge => {
          _this.graph.setItemState(edge, 'hoverHighLight', false)
        })
        _this.graph.setItemState(node, 'hoverFocus', false)
        highLightNodeList.forEach(node => {
          _this.graph.setItemState(node, 'hoverRemote', false)
        })
      })
      this.graph.on('edge:mouseenter', function (evt) {
        const edge = evt.item
        if (!edge.hasState('error')) {
          _this.graph.setItemState(edge, 'hoverHighLight', true)
        } else {
        _this.graph.setItemState(edge, 'errorHover', true)
        }
      })
      this.graph.on('edge:mouseleave', function (evt) {
        const edge = evt.item
        _this.graph.clearItemStates(edge, ['hoverHighLight', 'errorHover'])
      })
      this.graph.on('edge:click', function (evt) {
        const edge = evt.item
        _this.$emit('edgeSelected', edge.getModel())

        _this.clearSelectedStateByCache()
        if (!edge.hasState('error')) {
          _this.graph.setItemState(edge, 'edgeClickSelectedHighLight', true)
        } else {
          _this.graph.setItemState(edge, 'errorSelected', true)
        }
        _this.selectedLinkCache = [edge]
      })
      this.graph.on('node:click', function (evt) {
        const node = evt.item
        const model = node.getModel()
        _this.displayInfo = model
        _this.nodeClicked(_this.displayInfo)
        _this.highlightNodeWithConnections(node)
      })
      this.graph.on('canvas:click', function () {
        _this.clearSelectedStateByCache()
        _this.$emit('canvasClick')
      })

      this.graph.data({
        nodes: this.nodes,
        edges: this.edges
      })

      this.graphIsDoingLayout = true
      this.graph.render()
      this.initailized = true
      // 添加画布根据元素宽度自动适配的事件
      this.$emit('addResizeFunction', function () {
        if (!_this.graph || _this.graph.get('destroyed')) return
        if (!container || !container.clientWidth || !container.clientHeight) return
        _this.graph.changeSize(container.clientWidth, container.clientHeight)
      })
    }
  },
  mounted: function () {
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
    // background-color: burlywood;
  }
</style>
