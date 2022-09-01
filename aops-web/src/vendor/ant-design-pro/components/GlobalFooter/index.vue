<template>
  <global-footer class="footer custom-render">
    <template v-slot:links>
      <div>
        <a href="" target="_blank">帮助</a>
        <a href="" target="_blank">反馈</a>
        <a href="" target="_blank">关于我们</a>
      </div>
      <div>
        版权所有 ©华为技术有限公司 1998-2022。 保留一切权利。 粤A2-20044005号
      </div>
    </template>
    <template v-slot:copyright>
      <img src="~@/assets/horizontal-left.png" style="height: 20px" class="logo" alt="logo">
    </template>
  </global-footer>
</template>

<script>
import { GlobalFooter } from '@ant-design-vue/pro-layout'

export default {
  name: 'ProGlobalFooter',
  components: {
    GlobalFooter
  }
}
</script>
