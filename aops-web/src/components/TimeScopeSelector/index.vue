<template>
  <div class="time-scope-selector">
    <a-date-picker
      show-time
      placeholder="筛选在此时间之后"
      @change="onStartChange"
      @ok="onStartOk"
    />
    <a-date-picker
      show-time
      placeholder="筛选在此时间之前"
      @change="onEndChange"
      @ok="onEndOk"
    />
  </div>
</template>

<script>
export default {
  name: 'TimeScopeSelector',
  props: {
    /* eslint-disable */
    value: {
      type: Object,
      default: undefined
    }
    /* eslint-enable */
  },
  data () {
    return {
      time: [
        null,
        null
      ]
    }
  },
  methods: {
    onStartOk (value) {
      this.time[0] = value
      this.$emit('change', this.time)
    },
    onEndOk (value) {
      this.time[1] = value
      this.$emit('change', this.time)
    },
    onStartChange (value) {
      this.time[0] = value
      this.$emit('change', this.time)
    },
    onEndChange (value) {
      this.time[1] = value
      this.$emit('change', this.time)
    }
  }
}
</script>

<style lang="less" scoped>
</style>
