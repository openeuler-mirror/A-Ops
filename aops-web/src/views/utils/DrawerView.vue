<template>
  <span @click="visible = true" style="display: inline">
    <slot name="click"></slot>
    <a-drawer
      :title="title"
      :width="width"
      :height="height"
      :body-style="bodyStyle"
      :visible="visible"
      @close="visible = false"
      destroyOnClose
    >
      <slot name="drawerView"></slot>
      <div class="drawerBtn" v-if="hasButtonOnBottom">
        <a-button style="margin-left: 8px" @click="visible = false">{{ closeButtonText }}</a-button>
        <a-button
          :loading="spinning"
          v-for="(button,key) in buttonList"
          :key="key"
          style="margin-left: 8px"
          @click="button.callBack"
          :type="button.type || ''"
        >
          {{ button.text }}
        </a-button>
      </div>
    </a-drawer>
  </span>
</template>
<style>
  .drawerBtn{position: absolute;right: 0;bottom: 0;width:100%;border-top: 1px solid #e9e9e9;padding: 10px 16px;background: #fff;text-align: right;z-index: 1}
</style>
<script>

export default {
  name: 'DrawerView',
  provide () {
    return {
      setButtons: this.setButtons,
      close: this.close,
      showSpin: this.showSpin,
      closeSpin: this.closeSpin,
      onload: this.addLoad
    }
  },
  props: {
    title: {
      type: String,
      default: ''
    },
    width: {
      type: Number,
      default: 720
    },
    height: {
      type: Number,
      default: 600
    },
    bodyStyle: {
      type: Object,
      default: () => { return {} }
    },
    hasButtonOnBottom: {
      type: Boolean,
      default: true
    },
    closeButtonText: {
      type: String,
      default: '关闭'
    }
  },
  data () {
    return {
      buttonList: [],
      loads: [],
      params: null,
      spinning: false,
      visible: false
    }
  },
  methods: {
    addLoad (onload) { // 注册load通知
      this.loads.push(onload)
      onload(this.params)// 初次注册，open已经触发，补通知一次
    },
    setButtons (...list) {
      this.buttonList = list
    },
    showSpin () {
      this.spinning = true
    },
    closeSpin () {
      this.spinning = false
    },
    close () {
      this.visible = false
    },
    open (params) {
      // 外部通过ref调用本组件的open方法，实现drawer展开
      this.params = params
      this.visible = true
      // 通知注册了load事件的子组件
      this.loads.forEach(function (load) {
        typeof load === 'function' && load(params)
      })
    }
  }
}
</script>
