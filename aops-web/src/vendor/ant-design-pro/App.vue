<template>
  <a-config-provider :locale="locale">
    <div id="app">
      <keep-alive>
         <router-view v-if="$route.meta.keepAlive"/>
      </keep-alive>
      <router-view v-if="!$route.meta.keepAlive"/>
    </div>
  </a-config-provider>
</template>

<script>
import { domTitle, setDocumentTitle } from '@/vendor/ant-design-pro/utils/domUtil'
import { i18nRender } from '@/vendor/ant-design-pro/locales'

export default {
  data () {
    return {
    }
  },
  computed: {
    locale () {
      const { title } = this.$route.meta
      title && (setDocumentTitle(`${i18nRender(title)} - ${domTitle}`))

      return this.$i18n.getLocaleMessage(this.$store.getters.lang).antLocale
    }
  }
}
</script>
