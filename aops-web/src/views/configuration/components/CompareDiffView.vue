<template>
  <a-card>
    <div
      v-for="(part, index) in diffPartList"
      :key="index"
    >
      <a-row type="flex" justify="space-between">
        <a-col :span="11" class="diff-line" :class="[setDiffClass(part.added, part.removed, true)]">
          {{ !part.added ? part.value : '' }}
        </a-col>
        <a-col :span="11" class="diff-line" :class="[setDiffClass(part.added, part.removed)]">
          {{ !part.removed ? part.value: '' }}
        </a-col>
      </a-row>
    </div>
  </a-card>
</template>

<script>
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'

export default {
    name: 'CompareDiffView',
    components: {
        PageHeaderWrapper
    },
    props: {
      comparedConf: {
        type: Object,
        default: () => {}
      }
    },
    data () {
      return {}
    },
    computed: {
      diffByLine () {
        return this.comparedConf.diffResult || []
      },
      diffPartList () {
        return this.diffByLine.map((part) => {
          return part
        })
      }
    },
    methods: {
      setDiffClass (isAdd, isRemoved, isOrigin) {
        if (isOrigin) {
          if (isAdd) {
            return 'diff-add-blank'
          }
          if (isRemoved) {
            return 'diff-remove'
          }
        } else {
          if (isAdd) {
            return 'diff-add'
          }
          if (isRemoved) {
            return 'diff-remove-blank'
          }
        }
        return ''
      }
    }
}
</script>

<style lang="less" scoped>
  .test {
    margin:0 -2px;
    word-break: break-all;
    white-space: pre-wrap;
  }
  .diff-line {
    word-break: break-all;
    white-space: pre-wrap;
  }
  .diff-add {
    background: rgb(236, 253, 240);
    &-blank {
      background: rgb(236, 253, 240);
      color: rgb(236, 253, 240);
    }
  }
  .diff-remove {
    background: rgb(251,233,235);
    &-blank {
      background: rgb(251,233,235);
      color: rgb(251,233,235);
    }
  }
</style>
