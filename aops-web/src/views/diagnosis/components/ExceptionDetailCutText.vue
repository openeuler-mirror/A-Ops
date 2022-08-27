<template>
  <span v-if="!show">{{ output }}</span>
  <a-tooltip :placement="direction" v-else>
    <template slot="title">
      <div v-for="(item,index) in labelText" :key="index">
        <span>{{ item }}</span>
      </div>
    </template>
    {{ output }}
  </a-tooltip>
</template>

<script>

export default {
  name: 'ExceptionDetailCutText',
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
      show: false
    }
  },
  watch: {
    text: function (val) {
      this.output = this.cutoff(this.text, this.length)
    }
  },
  computed: {
    labelText () {
      // 消除开头的 '{' , 和末尾的 '}'
      const list = this.text.replace(/^(\s|{)+|(\s|})+$/g, '').split(',')
      let tmpArr = []
      const result = []
      list.map(item => {
        tmpArr = item.split('=')
        tmpArr[1] = tmpArr[1].substring(1, tmpArr[1].length - 1)
        result.push(tmpArr.join(': '))
      })
      return result
    }
  },
  methods: {
    cutoff (text, length) {
      text = text.replace(/^(\s|{)+|(\s|})+$/g, '')
      if (text && text.length > length) {
        text = text.substr(0, length) + '...'
        this.show = true
      } else {
        this.show = false
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
