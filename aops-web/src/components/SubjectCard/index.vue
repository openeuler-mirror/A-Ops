<template>
  <a-card :bordered="false" class="aops-theme-incard">
    <div class="subject-card-content" @click="onClick" :class="linkTo && 'has-link'">
      <a-row :gutter="16" type="flex">
        <a-col flex="60px">
          <div class="avatar-div">
            <slot name="logoImg" />
          </div>
        </a-col>
        <a-col flex="1 1 10px">
          <div class="content-div">
            <div class="title">{{ itemLabel }}</div>
            <div class="remark">{{ itemContent }}</div>
          </div>
        </a-col>
      </a-row>
      <div class="tagList" @click.stop>
        <a-tag v-for="tag in tagList" :key="tag">{{ tag }}</a-tag>
      </div>
    </div>
    <template slot="actions" class="ant-card-actions">
      <slot />
    </template>
  </a-card>
</template>

<script>
import router from '@/appCore/router'
export default {
  name: 'SubjectCard',
  props: {
    linkTo: {
      type: String,
      default: ''
    },
    itemLabel: {
      type: String,
      default: ''
    },
    itemContent: {
      type: String,
      default: ''
    },
    tagList: {
      type: Array,
      default: () => []
    }
  },
  methods: {
    onClick: function () {
      router.push(this.linkTo)
    }
  }
}
</script>

<style lang="less" scoped>
  .subject-card-content {
    &.has-link {
      cursor: pointer;
    }
    color: #000;
    height: 80px;
    line-height: 1.2em;
    .avatar-div {
      height: 1px;
      /deep/ img {
        height: 48px;
        width: 48px;
      }
    }
    .title {
      margin-bottom: 0.4em;
      font-weight: 600;
      font-size:20px;
    }
    .remark {
      text-overflow: -o-ellipsis-lastline;
      overflow: hidden;
      text-overflow: ellipsis;
      display: -webkit-box;
      -webkit-line-clamp: 2;
      line-clamp: 2;
      -webkit-box-orient: vertical;
    }
    .tagList{
      margin-top: 20px;
      overflow: hidden;
      white-space: nowrap;
      text-overflow: ellipsis;
      span { cursor: default }
    }
  }
</style>
