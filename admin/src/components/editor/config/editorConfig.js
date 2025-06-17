/**
 * TinyMCE 编辑器配置
 */

import { useAuthStore } from '../../../stores/auth'

// 基础编辑器配置
export const getBaseConfig = (props) => ({
  height: props.height,
  menubar: false,
  branding: false,
  promotion: false,
  language: 'zh_CN',
  language_url: '/admin/langs/zh_CN.js',
  skin_url: '/admin/tinymce/skins/ui/oxide',
  content_css: '/admin/tinymce/skins/content/default/content.css',
  directionality: 'ltr',
  element_format: 'html',
  entity_encoding: 'raw',
  convert_urls: false,
  relative_urls: false,
  placeholder: props.placeholder,
  auto_focus: false,
  browser_spellcheck: true,
  contextmenu_never_use_native: false,
})

// 插件配置
export const getPluginsConfig = () => [
  'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
  'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
  'insertdatetime', 'media', 'table', 'wordcount',
  'autosave', 'directionality', 'nonbreaking', 'pagebreak'
]

// 工具栏配置
export const getToolbarConfig = (props) => ({
  toolbar: 'responsivepreview | undo redo | blocks fontsize fontsizeplus fontsizeminus lineheight | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor | link image styleimages table | quicksymbols | addpinyin removepinyin smartpinyin | inserttemplate | advancedcode | fullscreen',
  toolbar_mode: props.toolbarMode,
  contextmenu: 'undo redo | cut copy paste pastetext | selectall | removeformat | addpinyin removepinyin | link unlink',
})

// 字体配置
export const getFontConfig = () => ({
  font_size_formats: '8px 10px 12px 14px 16px 18px 20px 24px 28px 32px 36px 42px 48px 54px 60px 72px 84px 96px 108px 120px 144px 168px 192px 216px 240px',
  formats: {
    fontsize: { inline: 'span', styles: { 'font-size': '%value' } }
  }
})

// 内容样式配置
export const getContentStyleConfig = () => `
  body {
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
    font-size: 14px;
    line-height: 2.5;
    margin: 1rem;
  }

  /* 图片默认样式 - 宽度100%，高度自适应 */
  .mce-content-body img {
    width: 100%;
    height: auto;
    max-width: 100%;
    display: block;
    margin: 10px auto;
    border-radius: 8px;
    box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
    transition: all 0.3s ease;
  }

  /* 图片悬停效果 */
  .mce-content-body img:hover {
    box-shadow: 0 4px 16px rgba(0, 0, 0, 0.15);
    transform: translateY(-1px);
  }

  /* 响应式图片 - 确保在小屏幕上也能正确显示 */
  @media (max-width: 768px) {
    .mce-content-body img {
      margin: 8px auto;
      border-radius: 6px;
    }
  }

  /* 拼音注音样式 */
  ruby {
    ruby-align: center;
    display: inline-block;
    white-space: nowrap;
    margin: 0 2px;
    vertical-align: baseline;
    line-height: 2.2;
    position: relative;
  }

  ruby.pinyin-ruby {
    background: rgba(64, 158, 255, 0.05);
    border-radius: 4px;
    padding: 3px 2px 1px 2px;
    cursor: pointer;
    transition: all 0.2s ease;
    border: 1px solid transparent;
    margin: 0 1px;
    position: relative;
  }

  ruby.pinyin-ruby:hover {
    background: rgba(64, 158, 255, 0.1);
    border-color: rgba(64, 158, 255, 0.3);
    transform: translateY(-1px);
    box-shadow: 0 2px 4px rgba(64, 158, 255, 0.2);
  }

  ruby.pinyin-ruby:focus-within {
    background: rgba(64, 158, 255, 0.15);
    border-color: rgba(64, 158, 255, 0.5);
    outline: none;
  }

  rt {
    color: #409eff;
    font-weight: 500;
    display: block;
    text-align: center;
    line-height: 1.2;
    margin-bottom: 3px;
    user-select: none;
    min-width: 1em;
    padding: 0 1px;
    position: relative;
    z-index: 1;
    font-size: 0.75em;
  }

  rt[style*="font-size"] {
    font-size: inherit !important;
  }

  rb {
    border-bottom: 1px dotted #409eff;
    display: block;
    text-align: center;
    user-select: text;
    line-height: 1.4;
    position: relative;
    z-index: 1;
    font-size: 1em;
  }

  rb[style*="font-size"] {
    font-size: inherit !important;
  }

  ruby:not(.pinyin-ruby) {
    background: transparent;
    padding: 0;
  }

  /* 表格样式增强 */
  table {
    border-collapse: collapse;
    width: 100%;
    margin: 15px 0;
  }

  table.default-table {
    border: 1px solid #ddd;
  }

  table.striped-table tbody tr:nth-child(even) {
    background-color: #f9f9f9;
  }

  table.bordered-table,
  table.bordered-table th,
  table.bordered-table td {
    border: 1px solid #ddd;
  }

  table.compact-table th,
  table.compact-table td {
    padding: 4px 8px;
  }

  table.score-table {
    border: 2px solid #409eff;
  }

  table.score-table th {
    background-color: #409eff;
    color: white;
    font-weight: bold;
  }

  th, td {
    padding: 8px 12px;
    text-align: left;
    border-bottom: 1px solid #ddd;
  }

  th {
    background-color: #f5f5f5;
    font-weight: bold;
  }

  .table-header {
    background-color: #409eff !important;
    color: white !important;
    font-weight: bold !important;
  }

  .table-important {
    background-color: #f56c6c !important;
    color: white !important;
  }

  .table-warning {
    background-color: #e6a23c !important;
    color: white !important;
  }

  .table-success {
    background-color: #67c23a !important;
    color: white !important;
  }
`

// 验证配置
export const getValidationConfig = () => ({
  valid_elements: '*[*]',
  extended_valid_elements: 'ruby[class],rb[*],rt[*],rp[*]',
  custom_elements: 'ruby,rb,rt,rp',
})

// 粘贴配置
export const getPasteConfig = () => ({
  paste_data_images: true,
  paste_as_text: false,
  paste_remove_styles: false,
  paste_webkit_styles: 'none',
  paste_retain_style_properties: '',
  paste_merge_formats: true,
  smart_paste: true,
  paste_postprocess: (plugin, args) => {
    // 自定义粘贴后处理
    console.log('粘贴内容处理:', args.node)
  }
})

// 自动保存配置
export const getAutosaveConfig = () => ({
  autosave_ask_before_unload: true,
  autosave_interval: '30s',
  autosave_prefix: 'tinymce-autosave-{path}{query}-{id}-',
  autosave_restore_when_empty: true,
  autosave_retention: '2m',
})

// 快速工具栏配置
export const getQuickbarsConfig = () => ({
  quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote',
  quickbars_insert_toolbar: 'quickimage quicktable',
})

// 表格配置
export const getTableConfig = () => ({
  table_default_attributes: {
    border: '1',
    style: 'border-collapse: collapse; width: 100%;'
  },
  table_default_styles: {
    'border-collapse': 'collapse',
    'width': '100%'
  },
  table_class_list: [
    { title: '默认表格', value: 'default-table' },
    { title: '斑马纹表格', value: 'striped-table' },
    { title: '边框表格', value: 'bordered-table' },
    { title: '紧凑表格', value: 'compact-table' },
    { title: '评分表格', value: 'score-table' }
  ],
  table_cell_class_list: [
    { title: '默认', value: '' },
    { title: '表头', value: 'table-header' },
    { title: '重要', value: 'table-important' },
    { title: '警告', value: 'table-warning' },
    { title: '成功', value: 'table-success' }
  ],
})

// 图片上传配置
export const getImageUploadConfig = () => ({
  images_upload_handler: async function (blobInfo, progress) {
    return new Promise(async (resolve, reject) => {
      try {
        const formData = new FormData()
        formData.append('image', blobInfo.blob(), blobInfo.filename())
        formData.append('folder', 'tinymce')

        // 获取token
        const authStore = useAuthStore()
        let token = null
        if (authStore.token) {
          token = authStore.token
        } else {
          const authData = localStorage.getItem('auth-store')
          if (authData) {
            const parsedData = JSON.parse(authData)
            token = parsedData.token
          }
        }

        const response = await fetch('/api/v1/upload/image', {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`
          },
          body: formData
        })

        if (!response.ok) {
          throw new Error('上传失败')
        }

        const result = await response.json()
        if (result.success) {
          resolve(result.data.url)
        } else {
          reject(result.message || '上传失败')
        }
      } catch (error) {
        reject(error.message || '上传失败')
      }
    })
  },
  images_upload_url: '/api/v1/upload/image',
  images_upload_base_path: '',
  images_upload_credentials: true,
})

// 合并所有配置
export const createEditorConfig = (props) => ({
  ...getBaseConfig(props),
  plugins: getPluginsConfig(),
  ...getToolbarConfig(props),
  ...getFontConfig(),
  content_style: getContentStyleConfig(),
  ...getValidationConfig(),
  ...getPasteConfig(),
  ...getAutosaveConfig(),
  ...getQuickbarsConfig(),
  ...getTableConfig(),
  ...getImageUploadConfig(),
})
