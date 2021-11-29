<template>
  <span v-if="!toolTip">{{ output }}</span>
  <a-tooltip :placement="direction" v-else>
    <template slot="title">
      <span>{{ toolTip }}</span>
    </template>
    {{ output }}
  </a-tooltip>
</template>

<script>

export default {
  name: 'CutText',
  props: {
    text: {
      type: String,
      default: ''
    },
    length: {
      type: Number,
      default: 10
    },
    direction: {
      type: String,
      default: 'top'
    }
  },
  data () {
    return {
      output: '',
      toolTip: ''
    }
  },
  watch: {
    text: function (val) {
      this.output = this.cutoff(this.text, this.length)
    }
  },
  methods: {
    cutoff (text, length) {
      const oldText = text
      if (text && text.length > length) {
        text = text.substr(0, length) + '...'
        this.toolTip = oldText
      } else {
        this.toolTip = ''
      }
      return text
    }
  },
  mounted () {
    this.output = this.cutoff(this.text, this.length)
  }
}
</script>

<style lang="less" scoped>
</style>
