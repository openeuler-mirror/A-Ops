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

const normalLinkColor = '#090'
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
      const links = []
      const processToNodeMap = {}
      dataList.forEach(function (entity) {
        // set nodes
        if (entity.type === 'PROCESS') {
          // 将进程添加到节点的children下
          const tempNode = entity
          const matchedNode = _this.nodes.filter(node => node.id === entity.dependingitems.runOns.id)[0]
          if (matchedNode) {
            tempNode.id = entity.entityid
            tempNode.label = entity.name
            matchedNode.children.push(tempNode)
          } else {
            _this.nodes.push({
              id: entity.dependingitems.runOns.id,
              children: [tempNode]
            })
          }
          processToNodeMap[entity.entityid] = entity.dependingitems.runOns.id
        } else if (entity.type === 'VM') {
          // 添加节点
          const tempNode = entity
          const matchedNode = _this.nodes.filter(node => node.id === entity.entityid)[0]
          if (!matchedNode) {
            tempNode.id = entity.entityid
            tempNode.label = entity.name
            tempNode.children = []
            _this.nodes.push(tempNode)
          } else {
            matchedNode.label = entity.name
          }
        } else {
          links.push(entity)
        }
      })

      links.forEach(function (entity) {
        // set edges
        const { type, attrs, ...tempEdge } = entity
        tempEdge.link_type = type

        tempEdge.source = processToNodeMap[entity.dependeditems.calls.id]
        tempEdge.target = processToNodeMap[entity.dependingitems.calls.id]
        tempEdge.id = `${tempEdge.source}_${tempEdge.target}`
        const matchedEdge = _this.edges.filter(edge => edge.id === tempEdge.id)[0]
        if (matchedEdge) {
          // 后续需要处理enitiy中的type
          matchedEdge.children.push(entity)
        } else {
          tempEdge.style = { stroke: normalLinkColor }
          if (tempEdge.source === tempEdge.target) {
            tempEdge.type = 'loop'
          } else {
            tempEdge.type = 'line'
          }
          tempEdge.children = [entity]
          _this.edges.push(tempEdge)
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
        if (err.response.data && err.response.data.status === 500) {
          _this.$message.error('服务器错误，请稍后再试')
        }
        _this.$message.error(err.response.data.msg || err.response.data.title || '获取架构数据失败，请稍后再试')
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

          const outDiv = document.createElement('div')
          outDiv.style.width = 'fit-content'

          const limit = 10
          if (e.item._cfg.type === 'edge') {
            let innerHTML = `<div> 
              <h4>Links from ${model.source} to ${model.target}</h4>
              <h5>Links: </h5>
              <ul>`
            if (model.children) {
              const list = [...model.children]
              if (model.children.length > limit) {
                list.splice(limit, list.length - 1)
              }
              list.forEach(edge => {
                innerHTML += `<li>- ${edge.name}</li>`
              })
              if (model.children.length > limit) {
                innerHTML += `and other ${model.children.length - limit} links`
              }
            }
            innerHTML += `</ul></div>`
            outDiv.innerHTML = innerHTML
          } else {
            let innerHTML = `<div>
              <h4>Node: ${model.label}</h4>
              <h5>Processes: </h5>
              <ul>`
            if (model.children) {
              const list = [...model.children]
              if (model.children.length > limit) {
                list.splice(limit, list.length - 1)
              }
              list.forEach(edge => {
                innerHTML += `<li>- ${edge.name}</li>`
              })
              if (model.children.length > limit) {
                innerHTML += `and other ${model.children.length - limit} processes`
              }
            }
            innerHTML += `</ul></div>`
            outDiv.innerHTML = innerHTML
          }
          return outDiv
        }
      })
      this.graph = new G6.Graph({
        container: container,
        width: width,
        height: height,
        plugins: [tooltip],
        linkCenter: true,
        layout: {
          type: 'force',
          linkDistance: 20,
          nodeStrength: 10,
          nodeSpacing: 20,
          edgeStrength: 0.1,
          preventOverlap: true,
          alphaMin: 0.03,
          onLayoutEnd: this.onLayoutEnd
        },
        defaultNode: {
          size: 60,
          style: {
            fill: 'steelblue',
            stroke: 'steelblue',
            lineWidth: 1
          },
          labelCfg: {
            style: {
              fill: '#fff'
            }
          }
        },
        defaultEdge: {
          style: {
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

      this.edges.forEach(edge => {
        if (!edge.style) {
          edge.style = {}
        }
        edge.style.lineWidth = edge.children.length > 8 ? 8 : (edge.children.length || 1)
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
