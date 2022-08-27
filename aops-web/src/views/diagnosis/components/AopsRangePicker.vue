<template>
  <a-range-picker
    v-bind="$attrs"
    :value="value"
    @change="handleChange"
    @ok="handleOk"
    @openChange="handleOpenChange"
  />
</template>

<script>
// this component is abandoned
export default {
  name: 'AopsRangePicker',
  data () {
    return {
      isOk: false,
      value: [],
      oldValue: []
    }
  },
  methods: {
    handleChange (val) {
      this.value = val
      if (val.length <= 0) {
        this.$emit('clear', this.value)
      }
    },
    handleOk () {
      this.isOk = true
    },
    handleOpenChange (state) {
      if (state) {
        this.oldValue = this.value
      } else {
        if (this.isOk) {
          this.$emit('ok', this.value)
          this.isOk = false
        } else {
          this.value = this.oldValue
          this.$emit('cancel')
        }
      }
    }
  }
}
</script>

<style lang="less" scoped>

</style>
