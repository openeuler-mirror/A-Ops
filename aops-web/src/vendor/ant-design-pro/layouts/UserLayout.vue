<template>

  <div id="userLayout" :class="['user-layout-wrapper', isMobile && 'mobile']">
    <div class="container">
      <div class="user-layout-content">
        <a-row style="height: 100vh" type="flex">
          <a-col class="left-side" :xs="{span: 24, order: 2}" :lg="{span: 12, order: 1}">
            <img src="~@/assets/loginPage.png" />
          </a-col>
          <a-col class="right-side" :xs="{span: 24, order: 1}" :lg="{span: 12, order: 2}">
            <div class="top">
              <div class="header">
                <a href="/">
                  <img src="~@/assets/vertical-left.png" class="logo" alt="logo">
                </a>
              </div>
              <div class="desc">
                {{ $t('layouts.userLayout.title') }}
              </div>
            </div>
            <router-view />
            <div class="footer">
              <div class="links">
                <a href="_self">帮助</a>
                <a href="_self">隐私</a>
                <a href="_self">条款</a>
              </div>
              <div class="copyright">
                Copyright &copy;
              </div>
            </div>
          </a-col>
        </a-row>
      </div>
    </div>
  </div>
</template>

<script>
import { deviceMixin } from '@/vendor/ant-design-pro/store/device-mixin'

export default {
  name: 'UserLayout',
  mixins: [deviceMixin],
  mounted () {
    document.body.classList.add('userLayout')
  },
  beforeDestroy () {
    document.body.classList.remove('userLayout')
  }
}
</script>

<style lang="less" scoped>
#userLayout.user-layout-wrapper {
  height: 100%;

  &.mobile {
    .container {
      .main {
        max-width: 368px;
        width: 98%;
      }
    }
  }

  .left-side {
    height: 100%;
    background: #EDEFF3;
    img {
      width: 500px;
      display: block;
      position: relative;
      margin: auto;
      top: 50vh;
      margin-top: -150px;
    }
  }
  .right-side {
    height: 100%;
    background: #fff;
    padding-top: 18vh;
  }

  .container {
    width: 100%;
    min-height: 100%;
    // background: #f0f2f5 url(~@/assets/background.svg) no-repeat 50%;
    background-size: 100%;
    position: relative;

    .user-layout-lang {
      width: 100%;
      height: 40px;
      line-height: 44px;
      text-align: right;

      .select-lang-trigger {
        cursor: pointer;
        padding: 12px;
        margin-right: 24px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        font-size: 18px;
        vertical-align: middle;
      }
    }

    .user-layout-content {

      .top {
        text-align: center;

        .header {
          .badge {
            position: absolute;
            display: inline-block;
            line-height: 1;
            vertical-align: middle;
            margin-left: -12px;
            margin-top: -10px;
            opacity: 0.8;
          }

          .logo {
            height: 80px;
            vertical-align: top;
            border-style: none;
          }

          .title {
            font-size: 33px;
            color: rgba(0, 0, 0, .85);
            font-family: Avenir, 'Helvetica Neue', Arial, Helvetica, sans-serif;
            font-weight: 600;
            position: relative;
            top: 2px;
          }
        }
        .desc {
          font-size: 14px;
          color: rgba(0, 0, 0, 0.45);
          margin-top: 12px;
          margin-bottom: 40px;
        }
      }

      .main {
        min-width: 260px;
        width: 368px;
        margin: 0 auto;
      }

      .footer {
        width: 100%;
        bottom: 0;
        padding: 0 16px;
        margin: 48px 0 24px;
        text-align: center;

        .links {
          margin-bottom: 8px;
          font-size: 14px;
          a {
            color: rgba(0, 0, 0, 0.45);
            transition: all 0.3s;
            &:not(:last-child) {
              margin-right: 40px;
            }
          }
        }
        .copyright {
          color: rgba(0, 0, 0, 0.45);
          font-size: 14px;
        }
      }
    }

    a {
      text-decoration: none;
    }

  }
}
</style>
