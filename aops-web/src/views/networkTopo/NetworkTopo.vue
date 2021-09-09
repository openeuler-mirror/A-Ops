<template>
  <page-header-wrapper>
    <a-card border="false">
      <div class="header">
        <h4 v-show="graphIsDoingLayout">图形布局中，请稍等 <a-spin size="small" /></h4>
      </div>
      <a-spin :spinning="dataLoading" size="large">
        <div id="graph-container" class="container"></div>
      </a-spin>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import G6 from '@antv/g6'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'

import { getTopoData } from '@/api/topo'

const normalLinkColor = '#eee'
const nginxLinkColor = '#00f'

export default {
  name: 'NetworkTopoDiagram',
  components: {
    PageHeaderWrapper
  },
  data () {
    return {
      nodes: [],
      edges: [],
      combos: [],
      graph: {},
      nodePosition: [],
      dataLoading: false,
      graphIsDoingLayout: false
    }
  },
  methods: {
    setGraphData (dataList) {
      this.nodes = []
      this.edges = []
      this.combos = []
      const _this = this
      dataList.forEach(function (entity) {
        // set nodes
        if (entity.type === 'PROCESS') {
          const tempNode = entity
          tempNode.id = entity.entityid
          tempNode.label = entity.name
          // get combo info
          const parentInfo = entity.dependingitems.runOns || {}
          const comboId = parentInfo.id
          if (comboId) {
            if (!_this.combos.filter(item => item.id === comboId)[0]) {
            _this.combos.push({
              id: comboId,
              label: `${parentInfo.type}: ${comboId}`
              // collapsed: true
            })
          }
            tempNode.comboId = comboId
            tempNode.cluster = comboId
          }
          _this.nodes.push(tempNode)
        } else {
          // set edges
          const { type, ...tempEdge } = entity
          tempEdge.link_type = type

          if (entity.type === 'NGINX-LINK') {
            const leftEdge = {
              ...tempEdge,
              id: `${entity.entityid}_${entity.dependingitems.runOns.id}_${entity.dependingitems.calls.id}_left`,
              source: entity.dependeditems.calls.id,
              target: entity.dependingitems.runOns.id,
              siblingId: entity.entityid,
              style: { stroke: normalLinkColor }
            }
            const rightEdge = {
              ...tempEdge,
              id: `${entity.entityid}_${entity.dependingitems.runOns.id}_${entity.dependingitems.calls.id}_right`,
              source: entity.dependingitems.runOns.id,
              target: entity.dependingitems.calls.id,
              siblingId: entity.entityid,
              style: { stroke: normalLinkColor }
            }
            _this.edges.push(rightEdge)
            _this.edges.push(leftEdge)
          } else {
            tempEdge.source = entity.dependeditems.calls.id
            tempEdge.target = entity.dependingitems.calls.id
            tempEdge.style = { stroke: normalLinkColor }
            _this.edges.push(tempEdge)
          }
        }
      })
      G6.Util.processParallelEdges(this.edges)
    },
    getGraphDataFromRemote () {
      const _this = this
      this.dataLoading = true
      getTopoData().then(res => {
        _this.setGraphData(res.entities || [])
        _this.initialGraph()
      }).catch(err => {
        _this.$message.error(err.response.data.msg)
      }).finally(() => {
        _this.dataLoading = false
      })
    },
    updateGraphDatafromRemote () {
      const _this = this
      getTopoData().then(res => {
        _this.setGraphData(res.entities || [])
        const data = {
          nodes: _this.nodes,
          edges: _this.edges,
          combos: _this.combos
        }
        _this.graph.changeData(data)
      }).catch(err => {
        _this.$message.error(err.response.data.msg)
      })
    },
    saveNodePosition () {
      this.nodePosition = []
      const nodes = this.graph.getNodes()
      nodes.forEach(node => {
        const model = node.getModel()
        this.nodePosition.push({
          id: model.id,
          x: model.x,
          y: model.y
        })
      })
    },
    updateNodeByPosition (nodes) {
      const TempNodeList = nodes.map(node => {
        const tempNode = Object.assign({}, node)
        const matchedPos = this.nodePosition.filter(nodeP => nodeP.id === node.id)[0]
        if (matchedPos) {
          tempNode.x = matchedPos.x
          tempNode.y = matchedPos.y
        }
        return tempNode
      })
      this.nodes = TempNodeList
    },
    onLayoutEnd () {
      this.graphIsDoingLayout = false
      this.graph.fitView()
    },
    initialGraph () {
      const _this = this
      const container = document.getElementById('graph-container')
      const width = container.scrollWidth
      const height = (container.scrollHeight || 500) - 20

      const tooltip = new G6.Tooltip({
        offsetX: 10,
        offsetY: 10,
        // the types of items that allow the tooltip show up
        // 允许出现 tooltip 的 item 类型
        itemTypes: ['node', 'edge'],
        // custom the tooltip's content
        // 自定义 tooltip 内容
        getContent: (e) => {
          const model = e.item.getModel()
          if (model.isComboEdge) {
            return `link from ${model.source} to ${model.target}`
          }
          const outDiv = document.createElement('div')
          outDiv.style.width = 'fit-content'
          // outDiv.style.padding = '0px 0px 20px 0px';
          let innerHTML = `
            <h4>${model.type}:${model.name}</h4>
            <ul>`
          model.attrs && model.attrs.forEach(attr => {
            innerHTML += `<li>${attr.key}: ${attr.value}</li>`
          })
          innerHTML += `</ul>`
          outDiv.innerHTML = innerHTML
          return outDiv
        }
      })
      this.graph = new G6.Graph({
        container: container,
        width: width,
        height: height,
        plugins: [tooltip],
        layout: {
          type: 'force',
          linkDistance: 50,
          nodeStrength: -10,
          nodeSpacing: 10,
          clustering: true,
          clusterNodeStrength: -5,
          clusterEdgeDistance: 200,
          clusterNodeSize: 50,
          clusterFociStrength: 1.2,
          edgeStrength: 0.1,
          preventOverlap: true,
          alphaMin: 0.03,
          onLayoutEnd: this.onLayoutEnd
        },
        defaultNode: {
          size: 20,
          style: {
            fill: 'steelblue',
            stroke: '#666',
            lineWidth: 1
          },
          labelCfg: {
            style: {
              fill: '#000'
            }
          }
        },
        defaultEdge: {
          style: {
            endArrow: true
          }
        },
        defaultCombo: {
          labelCfg: {
          position: 'top'
        }
      },
        modes: {
          default: ['drag-canvas', 'zoom-canvas', 'drag-combo',
            {
              type: 'drag-node',
              onlyChangeComboSize: true
            },
            {
              type: 'collapse-expand-combo',
              trigger: 'click',
              relayout: false // 收缩展开后，不重新布局
            }
          ]
        },
        nodeStateStyles: {
          hover: {
            fill: 'lightsteelblue'
          },
          click: {
            stroke: '#000',
            lineWidth: 3
          }
        },
        edgeStateStyles: {
          click: {
            stroke: 'steelblue'
          }
        }
      })

      this.graph.on('edge:mouseenter', function (evt) {
        const edge = evt.item
        const model = edge.getModel()
        if (model.link_type !== 'NGINX-LINK') {
          return
        }
        const siblingId = model.siblingId
        const siblingEdgeList = _this.graph.findAll('edge', edge => {
           return edge.get('model').siblingId === siblingId
           })
        siblingEdgeList.forEach(sibling => {
          _this.graph.updateItem(sibling, {
            style: {
                stroke: nginxLinkColor
              }
          })
        })
      })
      this.graph.on('edge:mouseleave', function (evt) {
        const edge = evt.item
        const model = edge.getModel()
        if (model.link_type !== 'NGINX-LINK') {
          return
        }
        const siblingId = model.siblingId
        const siblingEdgeList = _this.graph.findAll('edge', edge => {
           return edge.get('model').siblingId === siblingId
           })
        siblingEdgeList.forEach(sibling => {
          _this.graph.updateItem(sibling, {
            style: {
                stroke: normalLinkColor
              }
          })
        })
      })

      this.graph.data({
        nodes: this.nodes,
        edges: this.edges,
        combos: this.combos
      })

      this.graphIsDoingLayout = true
      this.graph.render()

      if (typeof window !== 'undefined') {
        window.onresize = () => {
          if (!_this.graph || _this.graph.get('destroyed')) return
          if (!container || !container.scrollWidth || !container.scrollHeight) return
          _this.graph.changeSize(container.scrollWidth, container.scrollHeight)
        }
      }
    }
  },
  mounted: function () {
    this.getGraphDataFromRemote()
  }
}
</script>

<style lang="less" scoped>
  .g6-tooltip {
      border: 1px solid #e2e2e2;
      border-radius: 4px;
      font-size: 12px;
      color: #545454;
      background-color: rgba(255, 255, 255, 0.9);
      padding: 10px 8px;
      box-shadow: rgb(174, 174, 174) 0px 0px 10px;
    }

  .header {
    height: 24px;
    line-height: 24px;
  }
  .container {
    min-height: 500px;
  }
</style>
