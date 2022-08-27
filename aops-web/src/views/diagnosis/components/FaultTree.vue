<template>
  <a-spin :spinning="treeDataLoading">
    <a-card>
      <div id="graph-container"></div>
    </a-card>
  </a-spin>
</template>

<script>
// this component is abandoned
import G6 from '@antv/g6'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
import { treeDataProcesser } from '../utils/treeDataProcesser'

export default {
  name: 'FaultTrees',
  components: {
    PageHeaderWrapper
  },
  data () {
    return {
      drawData: {},
      tree: {}
    }
  },
  props: {
    treeData: {
      type: Object,
      default: () => {}
    },
    treeDataLoading: {
      type: Boolean,
      default: false
    },
    highLightError: {
      type: Boolean,
      default: false
    }
  },
  computed: {
  },
  watch: {
    treeDataLoading () {
      const _this = this
      this.drawData = treeDataProcesser(this.treeData)
      if (this.drawData !== null) {
        this.tree.data(this.drawData)
        this.tree.render()
        this.tree.fitView()
      }

      this.tree.on('collapse-text:click', function (e) {
        _this.handleCollapse(e)
      })
      this.tree.on('collapse-back:click', function (e) {
        _this.handleCollapse(e)
      })
    }
  },
  methods: {
    getColor (cfg) {
      if (this.highLightError && cfg.value) {
        return '#c00'
      }
      // return color depends on params in cfg
      return '#8cc33e'
    },
    handleCollapse (e) {
      const target = e.target
      const id = target.get('modelId')
      const item = this.tree.findById(id)
      const nodeModel = item.getModel()
      nodeModel.collapsed = !nodeModel.collapsed
      this.tree.layout()
      this.tree.setItemState(item, 'collapse', nodeModel.collapsed)
    }
  },
  mounted: function () {
    G6.registerNode('treeNode', {
      draw: (cfg, group) => {
        const rootNode = cfg.id === '0'
        const fontSize = 16
        const width = G6.Util.getTextSize(cfg.label, fontSize)[0]

        if (cfg.children && cfg.children.length) {
          let controlX = width * 2
          let controlY = fontSize * 1
          let controlTextX = width * 2 + 8
          let controlTextY = fontSize * 1 + 6
          if (rootNode) {
            controlX = width * 2
            controlY = fontSize * 1.5
            controlTextX = width * 2 + 8
            controlTextY = fontSize * 1.5 + 6
          }
          group.addShape('rect', {
            attrs: {
              x: controlX,
              y: controlY,
              width: 16,
              height: 16,
              stroke: 'rgba(0, 0, 0, 0.25)',
              cursor: 'pointer',
              fill: '#fff'
            },
            name: 'collapse-back',
            modelId: cfg.id
          })

          // collpase text
          group.addShape('text', {
            attrs: {
              x: controlTextX,
              y: controlTextY,
              textAlign: 'center',
              textBaseline: 'middle',
              text: cfg.collapsed ? '+' : '-',
              fontSize,
              cursor: 'pointer',
              fill: 'rgba(0, 0, 0, 0.25)'
            },
            name: 'collapse-text',
            modelId: cfg.id
          })
        }

        if (rootNode) {
          const rect = group.addShape('rect', {
            attrs: {
              x: 0,
              y: 0,
              fill: this.getColor(cfg),
              width: width * 2,
              height: fontSize * 4,
              lineWidth: 0,
              opacity: 1,
              radius: 4
            },
            name: 'rect-shape',
            draggable: true
          })
          group.addShape('text', {
            attrs: {
              text: cfg.label,
              fill: '#fff',
              fontSize: 24,
              textBaseline: 'middle',
              x: width / 4 + 8,
              y: fontSize * 2
            },
            cursor: 'pointer',
            name: 'label-shape',
            draggable: true
          })

          return rect
        } else {
          const rect = group.addShape('rect', {
            attrs: {
              x: 0,
              y: 0,
              fill: this.getColor(cfg),
              width: width * 2,
              height: fontSize * 3,
              radius: 4,
              lineWidth: 0,
              opacity: 1
            },
            name: 'rect-shape',
            draggable: true
          })

          group.addShape('text', {
            attrs: {
              text: cfg.label,
              fill: '#000',
              fontSize: fontSize * 1.5,
              x: width / 4 - 4,
              y: fontSize * 2 + 4
            },
            cursor: 'pointer',
            name: 'label-shape',
            draggable: true
          })

          const bboxWidth = rect.getBBox().width
          const bboxHeight = rect.getBBox().height

          group.addShape('path', {
            attrs: {
              lineWidth: 2,
              fill: '#ccc',
              stroke: '#ccc',
              path: [
                ['M', 0, bboxHeight],
                ['L', bboxWidth, bboxHeight]
              ]
            },
            name: 'path-shape',
            draggable: true
          })
          return rect
        }
      },
      setState (name, value, item) {
        if (name === 'collapse') {
          const group = item.getContainer()
          const collapseText = group.find((e) => e.get('name') === 'collapse-text')
          if (collapseText) {
            if (!value) {
              collapseText.attr({
                text: '-'
              })
            } else {
              collapseText.attr({
                text: '+'
              })
            }
          }
        }
      },
      getAnchorPoints: (type, cfg) => {
        if (type.id === '0') {
          return [
          [0, 0.5],
          [1, 0.5]
        ]
        } else {
          return [
          [0, 1],
          [1, 1]
        ]
        }
      }
    })

    const tooltip = new G6.Tooltip({
      offsetX: 10,
      offsetY: 10,
      itemTypes: ['node'],
      getContent: (e) => {
        const model = e.item.getModel()
        return model.description || ''
      },
      shouldBegin: (e) => {
        const model = e.item.getModel()
        return !!model.description
      }
    })

    const _this = this
    const container = document.getElementById('graph-container')
    const width = container.scrollWidth
    const height = (container.scrollHeight || 500) - 20
    this.tree = new G6.TreeGraph({
      container: container,
      width: width,
      height: height,
      layout: {
        type: 'compactBox',
        direction: 'LR',
        getWidth: (node) => {
          return G6.Util.getTextSize(node.label, 16)[0] * 3
        },
        getVGap: () => {
          return 20
        },
        getHGap: () => {
          return 0
        }
      },
      defaultNode: {
        type: 'treeNode'
      },
      defaultEdge: {
        type: 'cubic-horizontal',
        style: {
          lineWidth: 2,
          color: '#ccc'
        }
      },
      minZoom: 0.5,
      modes: {
        default: [
          'drag-canvas', 'zoom-canvas'
        ]
      },
      plugins: [tooltip]
    })
    if (typeof window !== 'undefined') {
      window.onresize = () => {
        if (!_this.tree || _this.tree.get('destroyed')) return
        if (!container || !container.scrollWidth || !container.scrollHeight) return
        _this.tree.changeSize(container.scrollWidth, container.scrollHeight)
      }
    }
  }
}
</script>

<style>
