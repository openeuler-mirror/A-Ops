<template>
  <div>
    <input type="file" name="file" :id="uid" />
  </div>
</template>

<script>
import yaml from 'js-yaml'
const TYPE_ENUM = {
  'json': 'application/json',
  'yaml': 'application/x-yaml'
}
const REG_TYPE_ENUM = {
  'json': /.json$/,
  'yaml': /.yaml$/
}

export default {
  name: 'Uploader',
  props: {
    toJSON: {
      type: Boolean,
      default: false
    },
    uid: {
      type: String,
      default: 'upload'
    },
    sizeLimit: {
      type: Number,
      default: 1024 * 1024 * 100 // 100MB, no limit
    },
    fileType: {
      type: String,
      default: ''
    },
    /* eslint-disable */
    // this props.value can not set default value because of the rule of antd form.
    // and this prop is not used in this component for now.
    value: {
      type: [String, Object, Array]
    }
    /* eslint-disable */
  },
  methods: {
    // call this.$refs.<refName>.getFile() to get file content in parent component
    getFile () {
      const _this = this
      return new Promise((resolve, reject) => {
        try {
          const file = document.getElementById(_this.uid).files[0]
          if (!file) {
            throw new Error('请上传文件')
          }
          
          if (_this.fileType && TYPE_ENUM[_this.fileType] !== file.type && !file.name.match(REG_TYPE_ENUM[_this.fileType])) {
            throw new Error(`请上传${_this.fileType}类型文件!`)
          }
          if (_this.sizeLimit && _this.sizeLimit < file.size && !file.name.match(REG_TYPE_ENUM[_this.fileType])) {
            throw new Error(`文件大小超过${_this.sizeLimit / 1024}KB`)
          }
          const reader = new FileReader()
          reader.readAsText(file)
          reader.onload = function (e) {
            let content = e.target.result
            if (_this.toJSON) {
              if (TYPE_ENUM[_this.fileType] = 'application/x-yaml') {
                content = yaml.load(content)
              } else {
                content = JSON.parse(content)
              }
            }
            _this.$emit('load', content)
            _this.$emit('change', content)
            resolve(content)
          }
        } catch (err) {
          _this.$emit('error', err)
          _this.$emit('change')
          reject(err)
        }
      })
    }
  },
  mounted () {
    const _this = this
    document.getElementById(this.uid).addEventListener('change', function () {
      _this.getFile()
    })
  }
}
</script>

<style lang="less" scoped>

</style>
