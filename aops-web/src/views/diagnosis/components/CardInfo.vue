<template>
  <div class="cardInfo">
    <div>
      <p>描述：{{ remark }}</p>
    </div>
  </div>
</template>

<script>
// this component is abandoned
export default {
  name: 'CardInfo',
  props: {
    remark: {
      type: [String, String],
      default: ''
    }
  }
}
</script>

<style lang="less" scoped>
@import "~@/components/index.less";
@import "~@/utils/utils.less";

.cardInfo {

  .clearfix();

  margin-top: 16px;
  margin-left: 40px;
  & > div {
    position: relative;
    float: left;
    width: 100%;
    text-align: left;
    p {
      margin: 0;
      font-size: 24px;
      line-height: 32px;
    }
    p:first-child {
      margin-bottom: 4px;
      color: @text-color-secondary;
      font-size: 12px;
      line-height: 20px;
    }
  }
}
</style>
