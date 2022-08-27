<template>
  <div style="margin-bottom: 10px">
    <div>数据项列表：</div>
    <div style="line-height: 18px;" v-for="(data, index) in dataSource" :key="index">
      <span v-for="(key, idx) in keyArray" :key="idx" v-if="!!data[key]">
        <span v-if="idx>0" style="padding: 0 8px;font-size: 18px;font-weight: lighter;color: #000">|</span>
        <span style="color: #333">{{ key }}<span style="padding: 0 3px">:</span></span>
        <span v-if="typeof data[key] === 'object'">
          <span v-for="(value, key2, mapIndex2) in data[key]" :key="key2">
            <span v-if="mapIndex2>0">、</span><span style="border-bottom: 1px solid;padding: 0 2px;margin-right: 3px">{{ key2 }}<span style="padding: 0 3px">:</span>{{ value }}</span>
          </span>
        </span>
        <span v-else style="border-bottom: 1px solid;padding: 0 2px;margin-right: 3px">{{ data[key] }}</span>
      </span>
    </div>
  </div>
</template>

<script>
// this component is abandoned
export default {
  name: 'CheckResultExpanded',
  props: {
    dataSource: {
      type: Array,
      default: () => []
    }
  },
  data () {
    return {
      keyArray: ['name', 'type', 'macro', 'label', 'data_name_str']
    }
  },
  mounted: function () {
    var that = this
    this.dataSource.forEach(function (data) {
      for (const key in data) {
        if (that.keyArray.indexOf(key) < 0) {
          that.keyArray.push(key)
        }
      }
    })
  }
}
</script>

<style scoped>

</style>
