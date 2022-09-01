import { isIE } from '@/vendor/ant-design-pro/utils/util'

if (process.env.NODE_ENV !== 'production' || process.env.VUE_APP_PREVIEW === 'true') {
  if (isIE()) {
    console.error('ERROR: `mockjs` NOT SUPPORT `IE`.')
  }
  // 使用同步加载依赖
  // 防止 vuex 中的 GetInfo 早于 mock 运行，导致无法 mock 请求返回结果
  const Mock = require('mockjs2')
  // require('./services/auth')
  // require('./services/assest')
  // require('./services/diagnosis')
  // require('./services/configuration')
  // require('./services/management')
  // require('./services/task')
  // require('./services/leaks')

  Mock.setup({
    timeout: 800 // setter delay time
  })
}
