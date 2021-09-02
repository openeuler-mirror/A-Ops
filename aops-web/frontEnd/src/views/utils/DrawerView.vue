<template>
  <span @click="visible = true" style="display: inline">
    <slot name="click"></slot>
    <a-drawer :title="title" :width="720" :height="600" :visible="visible" @close="visible = false">
      <slot name="drawerView"></slot>
      <div class="drawerBtn">
        <a-button style="margin-right: 8px" @click="visible = false">取消</a-button>
        <a-button v-for="(button,key) in buttonList" @click="button.callBack" :key="key">{{ button.text }}</a-button>
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
      onload: this.addLoad
    }
  },
  props: {
    title: String
  },
  data () {
    return {
      buttonList: [],
      loads: [],
      params: null,
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
    close () {
      this.visible = false
    },
    open (params) {
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
