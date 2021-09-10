<template>
  <page-header-wrapper>
    <a-card>
      <a-row type="flex" justify="space-between">
        <a-col :span="11">
          {{ testConf1 }}
        </a-col>
        <a-col :span="11">
          {{ testConf2 }}
        </a-col>
      </a-row>
    </a-card>
    <a-card>
      对比字符
      <a-row type="flex" justify="space-between">
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffLeft"
            :key="index"
            :style="{ background: setColor(part.added, part.removed), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffRight"
            :key="index"
            :style="{ background: setColor(part.added, part.removed), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
      </a-row>
    </a-card>
    <a-card>
      对比行
      <a-row type="flex" justify="space-between">
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffLeft2"
            :key="index"
            :style="{ background: setColor(part.added, part.removed, true), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffRight2"
            :key="index"
            :style="{ background: setColor(part.added, part.removed), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
      </a-row>
    </a-card>
    <a-card>
      对比行，不一致的位置占位
      <a-row type="flex" justify="space-between">
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffByLine"
            :key="index"
            :style="{ background: setColor2(part.added, part.removed, true), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
        <a-col :span="11">
          <span
            class="test"
            v-for="(part, index) in diffByLine"
            :key="index"
            :style="{ background: setColor2(part.added, part.removed), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </span>
        </a-col>
      </a-row>
    </a-card>
    <a-card>
      对比行，div形式包裹元素，以block标记颜色
      <a-row type="flex" justify="space-between">
        <a-col :span="11">
          <div
            class="test"
            v-for="(part, index) in diffPartList"
            :key="index"
            :style="{ background: setColor2(part.added, part.removed, true), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </div>
        </a-col>
        <a-col :span="11">
          <div
            class="test"
            v-for="(part, index) in diffPartList"
            :key="index"
            :style="{ background: setColor2(part.added, part.removed), color: (part.added || part.removed) ? '#fff' : '' }"
          >
            {{ part.value }}
          </div>
        </a-col>
      </a-row>
    </a-card>
    <a-card>
      仿git样式
      <div
        v-for="(part, index) in diffPartList"
        :key="index"
      >
        <a-row type="flex" justify="space-between">
          <a-col :span="11" class="diff-line" :class="[setDiffClass(part.added, part.removed, true)]">
            {{ part.value }}
          </a-col>
          <a-col :span="11" class="diff-line" :class="[setDiffClass(part.added, part.removed)]">
            {{ part.value }}
          </a-col>
        </a-row>
      </div>
    </a-card>
  </page-header-wrapper>
</template>

<script>
// 本组件是diff对比组件的几个测试样例，生产代码中不应包含
import { PageHeaderWrapper } from '@ant-design-vue/pro-layout'
const Diff = require('diff')

export default {
    name: 'DiffTest',
    components: {
        PageHeaderWrapper
    },
    data () {
        return {
          /* eslint-disable */
          testConf1: '{\n    \"OS\": {\n    \"OS\": {\n    \"OS\": {\n    \"OS\": {\n    \"OS\": {\n        \"nam12e\": \"OS\",\n        \"baseurl\": \"http://repo.open{\n    \"OS\": {\n        \"nam12e\": \"OS\",\n        \"baseurl\": \"http://repo.openeuler.org/OS/$basearch/\",\n        \"enabled\": \"1\",\n        \"gpgcheck\": \"1\",\n        \"gpgkey\": \"http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler\"\n    },\n    \"21.09\": {\n}',
          testConf2: '{\n    \"OS\": {\n        \"nam34e\": \"OS\",\n        \"baseurl\": \"http://repo.open{\n    \"OS\": {\n        \"nam12e\": \"OS\",\n        \"baseurl\": \"http://repo.openeuler.org/openEuler-21.03/OS/$basearch/\",\n        \"enabled\": \"1\",\n        \"gpgcheck\": \"1\",\n        \"gpgkey\": \"http://repo.openeuler.org/openEuler-21.03/OS/$basearch/RPM-GPG-KEY-openEuler\"\n    },\n    \"21.09\": {\n        \"name\": \"21.09\",\n        \"baseurl\": \"http://119.3.219.20:82/openEuler:/21.09/standard_aarch64/12345\",\n        \"enabled\": \"1\",\n        \"gpgcheck\": \"0\"\n    },\n    \"everything\": {\n        \"name\": \"everything\",\n        \"baseurl\": \"http://repo.openeuler.org/openEuler-21.03/everything/$basearch/\",\n}',
          /* esline-enable */
          diff: [],
          diffByLine: []
        }
    },
    computed: {
        diffLeft () {
          return this.diff.filter(part => part.added !== true)
        },
        diffRight () {
          return this.diff.filter(part => part.removed !== true)
        },
        diffLeft2 () {
          return this.diffByLine.filter(part => part.added !== true)
        },
        diffRight2 () {
          return this.diffByLine.filter(part => part.removed !== true)
        },
        diffPartList () {
          return this.diffByLine.map((part) => {
            return {
              ...part,
              value: part.value.replace(/\n$/, '')
            }
          })
        },
    },
    methods: {
      setColor (isAdd, isRemoved) {
        if (isAdd) {
          return 'red'
        }
        if (isRemoved) {
          return 'green'
        }
        return ''
      },
      setColor2 (isAdd, isRemoved, isLeft) {
        if (isLeft) {
          if (isAdd) {
          return 'white'
        }
          if (isRemoved) {
            return 'green'
          }
        } else {
          if (isAdd) {
          return 'red'
        }
        if (isRemoved) {
          return 'white'
        }
        }
        return ''
      },
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
    },
    mounted: function () {
      // console.log(Diff)
      this.diff = Diff.diffChars(this.testConf1, this.testConf2)
      // console.log(this.diff)
      this.diffByLine = Diff.diffLines(this.testConf1, this.testConf2)
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
