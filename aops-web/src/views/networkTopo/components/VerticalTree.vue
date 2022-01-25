<template>
  <div id="vertical-tree-container"></div>
</template>

<script>
import G6 from '@antv/g6'

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
  name: 'VerticalTree',
  components: {
  },
  data () {
    return {
      drawData: {},
      tree: {},
      selectedNodeChache: null
    }
  },
  props: {
    selectedNodeId: {
        type: String,
        default: null
    },
    treeData: {
      type: Object,
      default: () => {}
    },
    isShow: {
      type: Boolean,
      default: () => {}
    }
  },
  computed: {
  },
  watch: {
    isShow () {
      if (this.isShow) {
        this.drawTree()
      }
    }
  },
  methods: {
    drawTree () {
      const drawData = this.treeData
        if (drawData !== null) {
          this.tree.data(drawData)
          this.tree.render()
          // this.tree.fitView()

          this.hightLightSelectedNode()

          this.setUXEvent()
          this.tree.translate(300, 500)
        }
    },
    // 点亮已选择的节点
    hightLightSelectedNode () {
      if (!this.selectedNodeId) {
        return
      }
      const highLightNodeList = this.tree.findAll('node', node => {
        return node.get('model').id === this.selectedNodeId
      })
      this.selectedNodeChache = highLightNodeList[0]
      this.tree.setItemState(highLightNodeList[0], 'nodeClickSelected', true)
    },
    // 设置交互事件
    setUXEvent () {
        const _this = this
        // hover
        this.tree.on('node:mouseenter', function (evt) {
          const node = evt.item
          _this.tree.setItemState(node, 'hoverFocus', true)
        })
        this.tree.on('node:mouseleave', function (evt) {
          const node = evt.item
          _this.tree.setItemState(node, 'hoverFocus', false)
        })
        this.tree.on('node:click', function (evt) {
          const node = evt.item
          const nodeId = node.getModel().id
          _this.$emit('treeNodeClicked', nodeId)
        })
    },
    initializingTree () {
      const tooltip = new G6.Tooltip({
        itemTypes: ['node'],
        getContent(e) {
           const outDiv = document.createElement('div');
           const msd = e.item.getModel()
           console.log(msd);
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
      const container = document.getElementById('vertical-tree-container')
      const width = container.scrollWidth
      const height = (container.scrollHeight || 500) - 20
      this.tree = new G6.TreeGraph({
        container: container,
        width: width,
        height: height,
        linkCenter: true,
        modes: {
          default: [
            'drag-canvas',
            'zoom-canvas'
          ]
        },
        defaultNode: {
          // type: 'diamond',
          size: 65,
          anchorPoints: [
            [0, 0.5],
            [1, 0.5]
          ]
        },
        defaultEdge: {
          type: 'cubic-vertical'
        },
        layout: {
          type: 'dendrogram',
          direction: 'BT', // H / V / LR / RL / TB / BT
          nodeSep: 40,
          rankSep: 100
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
          }
      })
      if (typeof window !== 'undefined') {
        window.onresize = () => {
          if (!_this.tree || _this.tree.get('destroyed')) return
          if (!container || !container.scrollWidth || !container.scrollHeight) return
          _this.tree.changeSize(container.scrollWidth, container.scrollHeight)
        }
      }
    }
  },
  mounted: function () {
    this.initializingTree()
    this.drawTree()
  }
}
</script>

<style>
