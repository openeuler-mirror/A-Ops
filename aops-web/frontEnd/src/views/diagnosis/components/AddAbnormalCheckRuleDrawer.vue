<template>
  <a-form :form="form" @submit="handleSubmit">
    <a-form-item label="检测项名称" v-bind="formItemLayout">
      <a-input
        v-decorator="['check_item', { rules: [{ required: true, message: '请填写归属业务域!' }] }]"
        placeholder="请输入检测项名称"
        style="width: 80%; margin-right: 8px"
      />
    </a-form-item>
    <a-form-item
      v-for="(k, index) in form.getFieldValue('keys')"
      :key="k"
      v-bind="index === 0 ? formItemLayout : formItemLayoutWithOutLabel"
      :label="index === 0 ? '数据项' : ''"
      :required="false"
    >
      <a-input
        v-decorator="[
          `names[${k}]`,
          {
            validateTrigger: ['change', 'blur'],
            rules: [
              {
                required: true,
                whitespace: true,
                message: '请输入数据项',
              },
            ],
          },
        ]"
        placeholder="请输入数据项"
        style="width: 80%; margin-right: 8px"
      />
      <a-icon
        v-if="form.getFieldValue('keys').length > 1"
        class="dynamic-delete-button"
        type="minus-circle-o"
        :disabled="form.getFieldValue('keys').length === 1"
        @click="() => remove(k)"
      />
    </a-form-item>
    <a-form-item v-bind="formItemLayoutWithOutLabel">
      <a-button type="dashed" style="width: 60%" @click="add">
        <a-icon type="plus" /> 添加
      </a-button>
    </a-form-item>
    <a-form-item label="检测条件" v-bind="formItemLayout">
      <a-input
        v-decorator="['check_condition', { rules: [{ required: false, message: '请填检测条件!' }] }]"
        style="width: 80%; margin-right: 8px"
        placeholder="请输入检测条件"
      />
    </a-form-item>
    <a-form-item label="检测描述项" v-bind="formItemLayout">
      <a-textarea
        v-decorator="['check_result_description', { rules: [{ required: false, message: '请填写检测描述项!' }] }]"
        style="width: 80%; margin-right: 8px"
        placeholder="请输入检测描述项"
      />
    </a-form-item>
    <a-form-item label="数据标签" v-bind="formItemLayout">
      <div>
        <template v-for="(tag, index) in tags">
          <a-tooltip v-if="tag.length > 20" :key="tag" :title="tag">
            <a-tag :key="tag" :closable="index !== 0" @close="() => handleClose(tag)">
              {{ `${tag.slice(0, 20)}...` }}
            </a-tag>
          </a-tooltip>
          <a-tag v-else :key="tag" :closable="index !== 0" @close="() => handleClose(tag)">
            {{ tag }}
          </a-tag>
        </template>
        <a-input
          v-if="inputVisible"
          ref="input"
          type="text"
          size="small"
          :style="{ width: '78px' }"
          :value="inputValue"
          @change="handleInputChange"
          @blur="handleInputConfirm"
          @keyup.enter="handleInputConfirm"
        />
        <a-tag v-else style="background: #fff; borderStyle: dashed;" @click="showInput">
          <a-icon type="plus" /> New Tag
        </a-tag>
      </div>
    </a-form-item>
  </a-form>
</template>

<script>
  import { importCheckRule } from '@/api/diagnosis'
  let id = 0
  export default {
    name: 'AddAbnormalCheckRuleDrawer',
    components: { },
    inject: ['setButtons', 'close', 'onload'], // 来自祖辈们provide中声明的参数、方法
    data () {
      return {
        formItemLayout: {
          labelCol: {
            xs: { span: 24 },
            sm: { span: 4 }
          },
          wrapperCol: {
            xs: { span: 24 },
            sm: { span: 20 }
          }
        },
        formItemLayoutWithOutLabel: {
          wrapperCol: {
            xs: { span: 24, offset: 0 },
            sm: { span: 20, offset: 4 }
          }
        },
        tags: [],
        inputVisible: false,
        inputValue: ''
      }
    },
    computed: {
    },
    beforeCreate () {
      this.form = this.$form.createForm(this, { name: 'dynamic_form_item' })
      this.form.getFieldDecorator('keys', { initialValue: [1], preserve: true })
    },
    methods: {
      remove (k) {
        const { form } = this
        const keys = form.getFieldValue('keys')
        if (keys.length === 1) {
          return
        }
        form.setFieldsValue({
          keys: keys.filter(key => key !== k)
        })
      },

      add () {
        const { form } = this
        const keys = form.getFieldValue('keys')
        const nextKeys = keys.concat(id++)
        form.setFieldsValue({
          keys: nextKeys
        })
      },
      handleSubmit (e) {
        const _this = this
        e.preventDefault()
        this.form.validateFields((err, values) => {
          if (!err) {
            const { keys, names } = values
            console.log('tags: ', _this.tags.join(','))
            console.log('Received values of form: ', values)
            console.log(
              'Merged values:',
              keys.map(key => names[key])
            )
            const checkItems = []
            checkItems.push({
              'check_item': values.check_item,
              'data_list': keys.map(key => names[key]),
              'check_condition': values.check_condition,
              'check_result_description': values.check_result_description,
              'label_config': _this.tags.join(',')
            })
            importCheckRule(checkItems)
              .then(function () {
                _this.$message.success('添加成功')
                _this.form.resetFields()
              })
              .catch(function (err) {
                _this.$message.error(err.response.data.message)
              })
              .finally(function () {
                _this.isLoading = false
              })
          }
        })
      },
      handleClose (removedTag) {
        const tags = this.tags.filter(tag => tag !== removedTag)
        this.tags = tags
      },

      showInput () {
        this.inputVisible = true
        this.$nextTick(function () {
          this.$refs.input.focus()
        })
      },

      handleInputChange (e) {
        this.inputValue = e.target.value
      },

      handleInputConfirm () {
        const inputValue = this.inputValue
        let tags = this.tags
        if (inputValue && tags.indexOf(inputValue) === -1) {
          tags = [...tags, inputValue]
        }
        console.log(tags)
        Object.assign(this, {
          tags,
          inputVisible: false,
          inputValue: ''
        })
      },
      anotherNew () {
        this.form.resetFields()
      }
    },
    mounted: function () {
      this.setButtons({ callBack: this.anotherNew, text: '再建一个' }, { callBack: this.handleSubmit, text: '保存' })
    }
  }
</script>
<style>

  .dynamic-delete-button {
    cursor: pointer;
    position: relative;
    top: 4px;
    font-size: 24px;
    color: #999;
    transition: all 0.3s;
  }
  .dynamic-delete-button:hover {
    color: #777;
  }
  .dynamic-delete-button[disabled] {
    cursor: not-allowed;
    opacity: 0.5;
  }

</style>
