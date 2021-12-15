<template>
  <a-drawer
    title="垂直层级"
    closable
    @close="handleCancel"
    :visible="visible"
    width="600"
  >
    <vertical-tree
      :isShow="visible"
      :treeData="treeData"
      :selectedNodeId="selectedNodeId"
      @treeNodeClicked="treeNodeClicked"
    />
  </a-drawer>
</template>

<script>
import VerticalTree from './VerticalTree.vue'
export default {
    name: 'VerticalMapDrawer',
    components: {
        VerticalTree
    },
    props: {
        visible: {
          type: Boolean,
          default: false
        },
        treeData: {
            type: Object,
            default: () => {}
        },
        selectedNodeId: {
            type: String,
            default: null
        }
    },
    data () {
        return {
        }
    },
    methods: {
        handleCancel () {
            this.$emit('close')
        },
        treeNodeClicked (nodeId) {
            this.$emit('treeNodeClicked', nodeId)
        }
    }
}
</script>

<style lang="less" scoped>
</style>
