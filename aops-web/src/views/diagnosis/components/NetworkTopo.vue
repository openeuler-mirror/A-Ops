<template>
  <page-header-wrapper>
    <a-card>
      <div id="graph-container"></div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
import G6 from '@antv/g6'
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'

import { testJson } from '@/mock/topoTestJson'

export default {
  name: 'NetworkTopoDiagram',
  components: {
    PageHeaderWrapper
  },
  data () {
    return {}
  },
  mounted: function () {
    const graph = new G6.Graph({
      container: 'graph-container',
      width: 1000,
      height: 600,
      layout: {
        type: 'force',
        preventOverlap: true,
        linkDistance: 100
      },
      defaultNode: {
        size: 30,
        style: {
          fill: 'steelblue',
          stroke: '#666',
          lineWidth: 1
        },
        labelCfg: {
          style: {
            fill: '#fff'
          }
        }
      },
      defaultEdge: {
        labelCfg: {
          autoRotate: true,
          style: {
            background: {
              fill: '#ffffff',
              padding: [0, 2, 0, 2]
            }
          }
        }
      },
      modes: {
        default: ['drag-canvas', 'zoom-canvas', 'drag-node',
          {
            type: 'tooltip',
            formatText (model) {
              const text = 'label: ' + model.label + '<br/> class: ' + model.class
              return text
            }
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

    // 设置node个性化样式
    testJson.nodes.forEach((node) => {
      if (!node.style) {
        node.style = {}
      }
      switch (
        node.class
      ) {
        case 'c0': {
          node.type = 'circle'
          break
        }
        case 'c1': {
          node.type = 'rect'
          node.size = [35, 20]
          break
        }
        case 'c2': {
          node.type = 'ellipse'
          node.size = [35, 20]
          break
        }
      }
    })

    // 设置edge个性化样式
    testJson.edges.forEach((edge) => {
      if (!edge.style) {
        edge.style = {}
      }
      edge.style.lineWidth = edge.weight
      edge.style.opacity = 0.6
      edge.style.stroke = 'green'
    })

    // 设置事件响应
    graph.on('node:mouseenter', (e) => {
      const nodeItem = e.item
      graph.setItemState(nodeItem, 'hover', true)
    })

    graph.on('node:mouseleave', (e) => {
      const nodeItem = e.item
      graph.setItemState(nodeItem, 'hover', false)
    })

    graph.on('node:click', (e) => {
      const clickNodes = graph.findAllByState('node', 'click')
      clickNodes.forEach((cn) => {
        graph.setItemState(cn, 'click', false)
      })
      const nodeItem = e.item
      graph.setItemState(nodeItem, 'click', true)
    })

    graph.on('edge:click', (e) => {
      const clickEdges = graph.findAllByState('edge', 'click')
      clickEdges.forEach((ce) => {
        graph.setItemState(ce, 'click', false)
      })
      const edgeItem = e.item
      graph.setItemState(edgeItem, 'click', true)
    })

    graph.data(testJson)
    graph.render()
  }
}
</script>

<style>
  .g6-tooltip {
      border: 1px solid #e2e2e2;
      border-radius: 4px;
      font-size: 12px;
      color: #545454;
      background-color: rgba(255, 255, 255, 0.9);
      padding: 10px 8px;
      box-shadow: rgb(174, 174, 174) 0px 0px 10px;
    }
</style>
