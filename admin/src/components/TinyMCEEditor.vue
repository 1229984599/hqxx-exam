<template>
  <div class="tinymce-editor">
    <Editor
      :api-key="apiKey"
      v-model="content"
      :init="editorConfig"
      @onSelectionChange="handleSelectionChange"
      @onInput="handleInput"
      @onChange="handleChange"
    />

    <!-- 编辑器状态栏 -->
    <div class="editor-footer">
      <!-- 字数统计 -->
      <span v-if="showWordCount" class="word-count">字数: {{ wordCount }}</span>

      <!-- 保存状态 -->
      <div class="save-status" :class="saveStatus">
        <el-icon v-if="saveStatus === 'saving'" class="rotating"><Loading /></el-icon>
        <el-icon v-else-if="saveStatus === 'saved'" style="color: #67c23a;"><Check /></el-icon>
        <el-icon v-else style="color: #e6a23c;"><Warning /></el-icon>
        <span>{{ saveStatusText }}</span>
      </div>

      <!-- 快捷键提示 -->
      <el-button
        type="text"
        size="small"
        @click="showShortcutsHelp"
        class="shortcuts-btn"
      >
        ⌨️ 快捷键
      </el-button>
    </div>

    <!-- 响应式预览对话框 -->
    <el-dialog
      v-model="showPreview"
      title="响应式预览"
      width="95%"
      :close-on-click-modal="true"
      top="10"
      :modal-append-to-body="true"
      class="preview-dialog"
    >
      <div class="preview-container">
        <!-- 设备选择器 -->
        <div class="device-selector">
          <div class="device-presets">
            <el-button
              v-for="preset in devicePresets"
              :key="preset.name"
              :type="previewWidth === preset.width && previewHeight === preset.height ? 'primary' : 'default'"
              size="small"
              @click="selectDevicePreset(preset)"
              class="device-btn"
            >
              <span class="device-icon">{{ preset.icon }}</span>
              <span class="device-name">{{ preset.name }}</span>
              <span v-if="preset.width > 0" class="device-size">{{ preset.width }}×{{ preset.height }}</span>
            </el-button>
          </div>

          <!-- 自定义尺寸控制 -->
          <div class="custom-size-controls">
            <div class="size-input-group">
              <label>宽度:</label>
              <el-input-number
                v-model="customWidth"
                :min="200"
                :max="2000"
                size="small"
                @change="updateCustomSize"
              />
              <span class="unit">px</span>
            </div>
            <div class="size-input-group">
              <label>高度:</label>
              <el-input-number
                v-model="customHeight"
                :min="200"
                :max="2000"
                size="small"
                @change="updateCustomSize"
              />
              <span class="unit">px</span>
            </div>
          </div>
        </div>

        <!-- 预览区域 -->
        <div class="preview-area">
          <div class="preview-frame-container">
            <div
              class="preview-frame"
              :style="{
                width: previewWidth + 'px',
                height: previewHeight + 'px'
              }"
            >
              <div class="preview-content" v-html="content"></div>
            </div>
            <div class="frame-info">
              {{ previewWidth }} × {{ previewHeight }}
            </div>
          </div>
        </div>
      </div>

      <template #footer>
        <el-button @click="closePreview">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 内容统计对话框 -->
    <el-dialog
      v-model="showStats"
      title="📊 内容统计"
      width="500px"
      :append-to-body="true"
    >
      <div class="stats-container">
        <div class="stats-grid">
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.characters }}</div>
            <div class="stat-label">总字符数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.charactersNoSpaces }}</div>
            <div class="stat-label">字符数（不含空格）</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.chineseChars }}</div>
            <div class="stat-label">中文字符</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.words }}</div>
            <div class="stat-label">词语数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.paragraphs }}</div>
            <div class="stat-label">段落数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.sentences }}</div>
            <div class="stat-label">句子数</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.pinyinAnnotations }}</div>
            <div class="stat-label">拼音注音</div>
          </div>
          <div class="stat-item">
            <div class="stat-value">{{ contentStats.readingTime }} 分钟</div>
            <div class="stat-label">预计阅读时间</div>
          </div>
        </div>

        <div class="stats-tips">
          <h4>📝 统计说明</h4>
          <ul>
            <li>阅读时间基于中文300字/分钟，英文200词/分钟计算</li>
            <li>词语数包含中文字符和英文单词</li>
            <li>句子数基于句号、问号、感叹号统计</li>
            <li>拼音注音统计当前文档中的注音数量</li>
          </ul>
        </div>
      </div>

      <template #footer>
        <el-button @click="showStats = false">关闭</el-button>
        <el-button type="primary" @click="calculateContentStats">刷新统计</el-button>
      </template>
    </el-dialog>

    <!-- 符号选择对话框 -->
    <el-dialog
      v-model="showSymbolDialog"
      title="🔣 插入符号"
      width="800px"
      :append-to-body="true"
      class="symbol-dialog"
    >
      <div class="symbol-container">
        <!-- 搜索和筛选 -->
        <div class="symbol-filters">
          <div class="filter-row">
            <el-input
              v-model="symbolSearchText"
              placeholder="搜索符号或名称..."
              clearable
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="selectedSymbolCategory"
              placeholder="选择分类"
              clearable
              class="category-select"
            >
              <el-option label="全部分类" value="all" />
              <el-option
                v-for="group in symbolGroups"
                :key="group.id"
                :label="group.title"
                :value="group.id"
              >
                <span class="category-option">
                  <span class="category-icon">{{ group.icon }}</span>
                  <span class="category-name">{{ group.title }}</span>
                </span>
              </el-option>
            </el-select>
          </div>
        </div>

        <!-- 符号网格 -->
        <div class="symbol-groups">
          <div
            v-for="group in filteredSymbols"
            :key="group.id"
            class="symbol-group"
          >
            <div class="group-header">
              <span class="group-icon">{{ group.icon }}</span>
              <span class="group-title">{{ group.title }}</span>
              <span class="group-count">({{ group.symbols.length }})</span>
            </div>
            <div class="symbol-grid">
              <div
                v-for="item in group.symbols"
                :key="item.symbol"
                class="symbol-item"
                @click="insertSymbol(item.symbol)"
                :title="item.name"
              >
                <span class="symbol-char">{{ item.symbol }}</span>
                <span class="symbol-name">{{ item.name }}</span>
              </div>
            </div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-if="filteredSymbols.length === 0"
          description="未找到符合条件的符号"
          :image-size="100"
        />
      </div>

      <template #footer>
        <el-button @click="closeSymbolDialog">关闭</el-button>
      </template>
    </el-dialog>

    <!-- 模板选择对话框 -->
    <el-dialog
      v-model="showTemplateDialog"
      title="📋 插入模板"
      width="900px"
      :append-to-body="true"
      class="template-dialog"
    >
      <div class="template-container" v-loading="templateLoading">
        <!-- 搜索和筛选 -->
        <div class="template-filters">
          <div class="filter-row">
            <el-input
              v-model="templateSearchText"
              placeholder="搜索模板名称或描述..."
              clearable
              class="search-input"
            >
              <template #prefix>
                <el-icon><Search /></el-icon>
              </template>
            </el-input>
            <el-select
              v-model="selectedTemplateCategory"
              placeholder="选择分类"
              clearable
              class="category-select"
            >
              <el-option label="全部分类" value="" />
              <el-option
                v-for="category in templateCategories"
                :key="category"
                :label="category"
                :value="category"
              />
            </el-select>
          </div>
        </div>

        <!-- 模板网格 -->
        <div class="template-grid">
          <div
            v-for="template in filteredTemplates"
            :key="template.id"
            class="template-card"
            @click="insertSelectedTemplate(template)"
          >
            <div class="template-header">
              <div class="template-icon">{{ template.icon || '📄' }}</div>
              <div class="template-info">
                <h4 class="template-name">{{ template.name }}</h4>
                <p class="template-description">{{ template.description || '暂无描述' }}</p>
              </div>
            </div>
            <div class="template-meta">
              <el-tag size="small" type="primary">{{ template.category }}</el-tag>
              <el-tag v-if="template.subject" size="small" type="info">
                {{ template.subject.name }}
              </el-tag>
              <span class="usage-count">使用 {{ template.usage_count }} 次</span>
            </div>
            <div class="template-preview" v-html="getTemplatePreview(template.content)"></div>
          </div>
        </div>

        <!-- 空状态 -->
        <el-empty
          v-if="filteredTemplates.length === 0 && !templateLoading"
          description="未找到符合条件的模板"
          :image-size="100"
        />
      </div>

      <template #footer>
        <el-button @click="closeTemplateDialog">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import {ref, computed, watch, onMounted, nextTick, h} from 'vue'
import Editor from '@tinymce/tinymce-vue'

// 导入 TinyMCE 核心
import tinymce from 'tinymce/tinymce'
import 'tinymce/models/dom'
import 'tinymce/themes/silver'
import 'tinymce/icons/default'

// 导入所有必要的插件
import 'tinymce/plugins/advlist'
import 'tinymce/plugins/autolink'
import 'tinymce/plugins/lists'
import 'tinymce/plugins/link'
import 'tinymce/plugins/image'
import 'tinymce/plugins/charmap'
import 'tinymce/plugins/preview'
import 'tinymce/plugins/anchor'
import 'tinymce/plugins/searchreplace'
import 'tinymce/plugins/visualblocks'
import 'tinymce/plugins/code'
import 'tinymce/plugins/fullscreen'
import 'tinymce/plugins/insertdatetime'
import 'tinymce/plugins/media'
import 'tinymce/plugins/table'
import 'tinymce/plugins/help'
import 'tinymce/plugins/wordcount'
import 'tinymce/plugins/emoticons'
import 'tinymce/plugins/autosave'
import 'tinymce/plugins/directionality'
import 'tinymce/plugins/nonbreaking'
import 'tinymce/plugins/pagebreak'
import 'tinymce/plugins/quickbars'
import { Reading, Delete, Close, DocumentAdd, Search, Loading, Check, Warning } from '@element-plus/icons-vue'
import { pinyin } from 'pinyin-pro'
import { ElMessage, ElMessageBox } from 'element-plus'
import api from '../utils/api'
import { useAuthStore } from '../stores/auth'

const props = defineProps({
  modelValue: {
    type: String,
    default: ''
  },
  placeholder: {
    type: String,
    default: '请输入内容...'
  },
  height: {
    type: [String, Number],
    default: 400
  },
  showPinyinTools: {
    type: Boolean,
    default: true
  },
  showWordCount: {
    type: Boolean,
    default: true
  },
  toolbarMode: {
    type: String,
    default: 'sliding'
  },
  apiKey: {
    type: String,
    default: 'gpl' // 使用免费版本
  },
  autoStyleImages: {
    type: Boolean,
    default: true // 默认自动应用图片样式
  }
})

const emit = defineEmits(['update:modelValue'])

// 获取auth store
const authStore = useAuthStore()

const content = ref('')
const selectedText = ref('')
const editorInstance = ref(null)

// 预览相关状态
const showPreview = ref(false)
const previewWidth = ref(375) // 默认iPhone宽度
const previewHeight = ref(667) // 默认iPhone高度
const customWidth = ref(375)
const customHeight = ref(667)

// 预设设备尺寸
const devicePresets = [
  { name: 'iPhone SE', width: 375, height: 667, icon: '📱' },
  { name: 'iPhone 12', width: 390, height: 844, icon: '📱' },
  { name: 'iPhone 12 Pro Max', width: 428, height: 926, icon: '📱' },
  { name: 'iPad', width: 768, height: 1024, icon: '📱' },
  { name: 'iPad Pro', width: 1024, height: 1366, icon: '📱' },
  { name: 'Desktop', width: 1200, height: 800, icon: '💻' },
  { name: '自定义', width: 0, height: 0, icon: '⚙️' }
]

// 内容统计相关
const showStats = ref(false)
const contentStats = ref({
  characters: 0,
  charactersNoSpaces: 0,
  words: 0,
  paragraphs: 0,
  sentences: 0,
  readingTime: 0,
  chineseChars: 0,
  pinyinAnnotations: 0
})

// 格式刷相关
const formatBrushActive = ref(false)
const copiedFormat = ref(null)

// 符号对话框相关
const showSymbolDialog = ref(false)
const symbolSearchText = ref('')
const selectedSymbolCategory = ref('all')

// 模板对话框相关
const showTemplateDialog = ref(false)
const templateSearchText = ref('')
const selectedTemplateCategory = ref('')
const availableTemplates = ref([])
const templateLoading = ref(false)

// 自动保存相关
const autoSaveEnabled = ref(true)
const lastSaveTime = ref(null)
const saveStatus = ref('saved') // 'saved', 'saving', 'unsaved'

const hasSelection = computed(() => selectedText.value.length > 0)
const wordCount = computed(() => {
  const text = content.value.replace(/<[^>]*>/g, '')
  return text.replace(/\s/g, '').length
})

// 保存状态文本
const saveStatusText = computed(() => {
  switch (saveStatus.value) {
    case 'saving':
      return '保存中...'
    case 'saved':
      return '已保存'
    case 'unsaved':
      return '未保存'
    default:
      return '已保存'
  }
})

// 符号数据
const symbolGroups = [
  {
    id: 'emoji',
    title: '常用表情',
    icon: '😀',
    symbols: [
      { symbol: '😀', name: '开心' },
      { symbol: '😁', name: '露齿笑' },
      { symbol: '😂', name: '笑哭' },
      { symbol: '😃', name: '大笑' },
      { symbol: '😄', name: '眯眼笑' },
      { symbol: '😅', name: '苦笑' },
      { symbol: '😆', name: '咧嘴笑' },
      { symbol: '😇', name: '天使' },
      { symbol: '😉', name: '眨眼' },
      { symbol: '😊', name: '微笑' },
      { symbol: '😋', name: '美味' },
      { symbol: '😌', name: '满足' },
      { symbol: '😍', name: '花痴' },
      { symbol: '😘', name: '飞吻' },
      { symbol: '😎', name: '酷' },
      { symbol: '😏', name: '得意' },
      { symbol: '😐', name: '面无表情' },
      { symbol: '😒', name: '无聊' },
      { symbol: '🙄', name: '翻白眼' },
      { symbol: '🤔', name: '思考' },
      { symbol: '😳', name: '脸红' },
      { symbol: '😞', name: '失望' },
      { symbol: '😟', name: '担心' },
      { symbol: '😠', name: '生气' },
      { symbol: '😡', name: '愤怒' },
      { symbol: '😢', name: '哭泣' },
      { symbol: '😭', name: '大哭' },
      { symbol: '😷', name: '口罩' },
      { symbol: '😴', name: '睡觉' },
      { symbol: '👍', name: '点赞' },
      { symbol: '👎', name: '点踩' },
      { symbol: '👏', name: '鼓掌' },
      { symbol: '👋', name: '挥手' },
      { symbol: '👌', name: 'OK' },
      { symbol: '✋', name: '停止' },
      { symbol: '💪', name: '肌肉' },
      { symbol: '🙏', name: '祈祷' },
      { symbol: '❤️', name: '红心' },
      { symbol: '💛', name: '黄心' },
      { symbol: '💚', name: '绿心' },
      { symbol: '💙', name: '蓝心' },
      { symbol: '💜', name: '紫心' },
      { symbol: '💔', name: '心碎' },
      { symbol: '💯', name: '满分' },
      { symbol: '✨', name: '闪亮' },
      { symbol: '⭐', name: '星星' },
      { symbol: '🔥', name: '火' },
      { symbol: '🎉', name: '庆祝' },
      { symbol: '🚀', name: '火箭' },
      { symbol: '📚', name: '书本' },
      { symbol: '📖', name: '打开的书' },
      { symbol: '📝', name: '记录' },
      { symbol: '💡', name: '灯泡' },
      { symbol: '🎓', name: '学士帽' },
      { symbol: '🍎', name: '苹果' },
      { symbol: '🏆', name: '奖杯' }
    ]
  },
  {
    id: 'punctuation',
    title: '标点符号',
    icon: '📝',
    symbols: [
      { symbol: '。', name: '句号' },
      { symbol: '，', name: '逗号' },
      { symbol: '；', name: '分号' },
      { symbol: '：', name: '冒号' },
      { symbol: '？', name: '问号' },
      { symbol: '！', name: '感叹号' },
      { symbol: '、', name: '顿号' },
      { symbol: '（', name: '左括号' },
      { symbol: '）', name: '右括号' },
      { symbol: '【', name: '左方括号' },
      { symbol: '】', name: '右方括号' },
      { symbol: '《', name: '左书名号' },
      { symbol: '》', name: '右书名号' },
      { symbol: '"', name: '左双引号' },
      { symbol: '"', name: '右双引号' },
      { symbol: '\'', name: '左单引号' },
      { symbol: '\'', name: '右单引号' }
    ]
  },
  {
    id: 'math',
    title: '数学符号',
    icon: '🔢',
    symbols: [
      { symbol: '＋', name: '加号' },
      { symbol: '－', name: '减号' },
      { symbol: '×', name: '乘号' },
      { symbol: '÷', name: '除号' },
      { symbol: '＝', name: '等号' },
      { symbol: '≠', name: '不等号' },
      { symbol: '＞', name: '大于号' },
      { symbol: '＜', name: '小于号' },
      { symbol: '≥', name: '大于等于' },
      { symbol: '≤', name: '小于等于' },
      { symbol: '±', name: '正负号' },
      { symbol: '∞', name: '无穷大' },
      { symbol: '√', name: '根号' },
      { symbol: '∑', name: '求和' },
      { symbol: '∏', name: '求积' },
      { symbol: '∫', name: '积分' },
      { symbol: '∂', name: '偏微分' },
      { symbol: '∆', name: '增量' },
      { symbol: '∇', name: '梯度' },
      { symbol: '∈', name: '属于' },
      { symbol: '∉', name: '不属于' },
      { symbol: '⊂', name: '包含于' },
      { symbol: '⊃', name: '包含' },
      { symbol: '∪', name: '并集' },
      { symbol: '∩', name: '交集' }
    ]
  },
  {
    id: 'units',
    title: '单位符号',
    icon: '📏',
    symbols: [
      { symbol: '℃', name: '摄氏度' },
      { symbol: '℉', name: '华氏度' },
      { symbol: '°', name: '度' },
      { symbol: '′', name: '分' },
      { symbol: '″', name: '秒' },
      { symbol: '㎡', name: '平方米' },
      { symbol: '㎥', name: '立方米' },
      { symbol: '㎏', name: '千克' },
      { symbol: '㎎', name: '毫克' },
      { symbol: '㎝', name: '厘米' },
      { symbol: '㎜', name: '毫米' },
      { symbol: '㎞', name: '千米' },
      { symbol: '％', name: '百分号' },
      { symbol: '‰', name: '千分号' },
      { symbol: '㎎/L', name: '毫克每升' },
      { symbol: '㎞/h', name: '千米每小时' }
    ]
  },
  {
    id: 'special',
    title: '特殊符号',
    icon: '✨',
    symbols: [
      { symbol: '★', name: '实心星' },
      { symbol: '☆', name: '空心星' },
      { symbol: '♠', name: '黑桃' },
      { symbol: '♥', name: '红心' },
      { symbol: '♦', name: '方块' },
      { symbol: '♣', name: '梅花' },
      { symbol: '♪', name: '音符' },
      { symbol: '♫', name: '双音符' },
      { symbol: '☀', name: '太阳' },
      { symbol: '☁', name: '云' },
      { symbol: '☂', name: '雨伞' },
      { symbol: '☃', name: '雪人' },
      { symbol: '✅', name: '对勾' },
      { symbol: '❌', name: '错号' },
      { symbol: '💡', name: '灯泡' },
      { symbol: '🔥', name: '火焰' },
      { symbol: '⚡', name: '闪电' },
      { symbol: '🌟', name: '星星' },
      { symbol: '🎯', name: '靶心' },
      { symbol: '🔔', name: '铃铛' }
    ]
  },
  {
    id: 'arrows',
    title: '箭头符号',
    icon: '➡️',
    symbols: [
      { symbol: '→', name: '右箭头' },
      { symbol: '←', name: '左箭头' },
      { symbol: '↑', name: '上箭头' },
      { symbol: '↓', name: '下箭头' },
      { symbol: '↗', name: '右上箭头' },
      { symbol: '↖', name: '左上箭头' },
      { symbol: '↘', name: '右下箭头' },
      { symbol: '↙', name: '左下箭头' },
      { symbol: '⇒', name: '双线右箭头' },
      { symbol: '⇐', name: '双线左箭头' },
      { symbol: '⇑', name: '双线上箭头' },
      { symbol: '⇓', name: '双线下箭头' },
      { symbol: '➡', name: '粗右箭头' },
      { symbol: '⬅', name: '粗左箭头' },
      { symbol: '⬆', name: '粗上箭头' },
      { symbol: '⬇', name: '粗下箭头' }
    ]
  }
]

// 过滤后的符号
const filteredSymbols = computed(() => {
  let groups = symbolGroups

  // 按分类过滤
  if (selectedSymbolCategory.value !== 'all') {
    groups = groups.filter(group => group.id === selectedSymbolCategory.value)
  }

  // 按搜索文本过滤
  if (symbolSearchText.value.trim()) {
    const searchText = symbolSearchText.value.toLowerCase()
    groups = groups.map(group => ({
      ...group,
      symbols: group.symbols.filter(item =>
        item.symbol.includes(searchText) ||
        item.name.toLowerCase().includes(searchText)
      )
    })).filter(group => group.symbols.length > 0)
  }

  return groups
})

// 过滤后的模板
const filteredTemplates = computed(() => {
  let templates = availableTemplates.value

  // 按分类过滤
  if (selectedTemplateCategory.value) {
    templates = templates.filter(template => template.category === selectedTemplateCategory.value)
  }

  // 按搜索文本过滤
  if (templateSearchText.value.trim()) {
    const searchText = templateSearchText.value.toLowerCase()
    templates = templates.filter(template =>
      template.name.toLowerCase().includes(searchText) ||
      (template.description && template.description.toLowerCase().includes(searchText))
    )
  }

  return templates
})

// TinyMCE 配置
const editorConfig = computed(() => ({
  height: props.height,
  menubar: false,
  plugins: [
    'advlist', 'autolink', 'lists', 'link', 'image', 'charmap',
    'anchor', 'searchreplace', 'visualblocks', 'code', 'fullscreen',
    'insertdatetime', 'media', 'table', 'wordcount',
    'autosave', 'directionality', 'nonbreaking', 'pagebreak'
  ],
  toolbar: 'responsivepreview contentstats | undo redo | blocks fontsize fontsizeplus fontsizeminus lineheight | bold italic underline strikethrough | alignleft aligncenter alignright alignjustify | outdent indent | numlist bullist | forecolor backcolor | link image styleimages table | quicksymbols | addpinyin removepinyin smartpinyin | inserttemplate | code | fullscreen',
  toolbar_mode: props.toolbarMode,

  // 右键菜单
  contextmenu: 'undo redo | cut copy paste | selectall | removeformat | link unlink',
  // 字体大小配置 - 添加更多大字体选项，特别适合教学场景
  font_size_formats: '8px 10px 12px 14px 16px 18px 20px 24px 28px 32px 36px 42px 48px 54px 60px 72px 84px 96px 108px 120px 144px 168px 192px 216px 240px',

  // 移除表情插件配置，使用自定义符号功能
  /*
  emoticons_append: {
    // 表情配置已移除，使用自定义符号面板
  },
  */
  content_style: `
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
      /* 如果没有设置具体字体大小，使用相对大小 */
      font-size: 0.75em;
    }
    /* 当rt有具体字体大小时，优先使用 */
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
      /* 如果没有设置具体字体大小，使用默认大小 */
      font-size: 1em;
    }
    /* 当rb有具体字体大小时，优先使用 */
    rb[style*="font-size"] {
      font-size: inherit !important;
    }
    /* 确保拼音注音在编辑器中正确显示 */
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
  `,
  placeholder: props.placeholder,
  branding: false,
  promotion: false,
  language: 'zh_CN',
  language_url: '/langs/zh_CN.js',
  skin_url: '/tinymce/skins/ui/oxide',
  content_css: '/tinymce/skins/content/default/content.css',
  directionality: 'ltr',
  element_format: 'html',
  entity_encoding: 'raw',
  convert_urls: false,
  relative_urls: false,
  valid_elements: '*[*]',
  extended_valid_elements: 'ruby[class],rb[*],rt[*],rp[*]',
  custom_elements: 'ruby,rb,rt,rp',
  paste_data_images: true,
  paste_as_text: false,
  paste_remove_styles: false,
  paste_preprocess: function(plugin, args) {
    // 清理从Word复制的内容
    args.content = cleanWordContent(args.content)
  },
  // 自动保存配置
  autosave_ask_before_unload: true,
  autosave_interval: '30s',
  autosave_prefix: 'tinymce-autosave-{path}{query}-{id}-',
  autosave_restore_when_empty: true,
  autosave_retention: '2m',
  // 表格配置增强
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
  // 快速工具栏配置
  quickbars_selection_toolbar: 'bold italic | quicklink h2 h3 blockquote',
  quickbars_insert_toolbar: 'quickimage quicktable',
  // 图片上传配置
  images_upload_handler: async function (blobInfo, progress) {
    return new Promise(async (resolve, reject) => {
      try {
        const formData = new FormData()
        formData.append('image', blobInfo.blob(), blobInfo.filename())
        formData.append('folder', 'tinymce')

        // 获取token - 优先从auth store，回退到localStorage
        let token = null
        if (authStore.token) {
          token = authStore.token
        } else {
          // 回退方式：从localStorage获取
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
  setup: (editor) => {
    editorInstance.value = editor

    // 添加自动换行快捷键 Shift+Enter
    editor.addShortcut('shift+13', '插入换行符', () => {
      editor.insertContent('<br>')
    })

    // 添加快速保存快捷键 Ctrl+S
    editor.addShortcut('ctrl+83', '快速保存', () => {
      // 触发保存事件
      editor.fire('save')
      ElMessage.success('内容已保存')
    })

    // 添加快速清除格式快捷键 Ctrl+Shift+X
    editor.addShortcut('ctrl+shift+88', '清除格式', () => {
      editor.execCommand('RemoveFormat')
    })

    // 添加拼音注音按钮
    editor.ui.registry.addButton('addpinyin', {
      text: '添加拼音',
      tooltip: '为选中的文字添加拼音注音\n💡 多音字支持：双击编辑 | 右键快速切换 | Delete删除',
      onAction: () => addPinyinAnnotation()
    })

    // 添加移除拼音按钮
    editor.ui.registry.addButton('removepinyin', {
      text: '移除拼音',
      tooltip: '移除选中文字的拼音注音',
      onAction: () => removePinyinAnnotation()
    })

    // 添加智能拼音按钮
    editor.ui.registry.addButton('smartpinyin', {
      text: '智能拼音',
      tooltip: '为所有中文字符自动添加拼音注音',
      onAction: () => addSmartPinyinAnnotation()
    })

    // 添加清理格式按钮
    editor.ui.registry.addButton('cleanformat', {
      text: '清理格式',
      tooltip: '清理Word等外部格式',
      onAction: () => cleanCurrentFormat()
    })

    // 添加插入模板按钮
    editor.ui.registry.addButton('inserttemplate', {
      text: '📋 模板',
      tooltip: '插入预设模板',
      onAction: () => openTemplateDialog()
    })

    // 添加字体大小增加按钮
    editor.ui.registry.addButton('fontsizeplus', {
      text: 'A+',
      tooltip: '增大字体 (Ctrl/Cmd + +)',
      onAction: () => increaseFontSize()
    })

    // 添加字体大小减少按钮
    editor.ui.registry.addButton('fontsizeminus', {
      text: 'A-',
      tooltip: '减小字体 (Ctrl/Cmd + -)',
      onAction: () => decreaseFontSize()
    })

    // 添加行间距调整按钮
    editor.ui.registry.addMenuButton('lineheight', {
      text: '行距',
      tooltip: '调整行间距',
      fetch: (callback) => {
        const items = [
          {
            type: 'menuitem',
            text: '单倍行距 (1.0)',
            onAction: () => setLineHeight('1.0')
          },
          {
            type: 'menuitem',
            text: '1.15倍行距',
            onAction: () => setLineHeight('1.15')
          },
          {
            type: 'menuitem',
            text: '1.5倍行距',
            onAction: () => setLineHeight('1.5')
          },
          {
            type: 'menuitem',
            text: '双倍行距 (2.0)',
            onAction: () => setLineHeight('2.0')
          },
          {
            type: 'menuitem',
            text: '2.5倍行距',
            onAction: () => setLineHeight('2.5')
          },
          {
            type: 'menuitem',
            text: '3倍行距',
            onAction: () => setLineHeight('3.0')
          }
        ]
        callback(items)
      }
    })

    // 添加内容统计按钮
    editor.ui.registry.addButton('contentstats', {
      text: '📊 统计',
      tooltip: '查看内容统计信息',
      onAction: () => showContentStats()
    })

    // 添加格式刷按钮
    editor.ui.registry.addToggleButton('formatbrush', {
      text: '🖌️ 格式刷',
      tooltip: '复制和应用格式 - 点击激活，选择源格式，再选择目标文字',
      onAction: () => toggleFormatBrush()
    })

    // 添加快速符号按钮
    editor.ui.registry.addButton('quicksymbols', {
      text: '🔣 符号',
      tooltip: '快速插入常用符号和表情',
      onAction: () => openSymbolDialog()
    })

    // 添加快捷键帮助按钮
    editor.ui.registry.addButton('shortcuts', {
      text: '⌨️ 快捷键',
      tooltip: '查看快捷键帮助',
      onAction: () => showShortcutsHelp()
    })

    // 添加响应式预览按钮
    editor.ui.registry.addButton('responsivepreview', {
      text: '👁️ 预览',
      tooltip: '响应式预览 - 查看内容在不同设备上的显示效果',
      onAction: () => openResponsivePreview()
    })

    // 添加图片样式按钮
    editor.ui.registry.addButton('styleimages', {
      text: '🖼️ 图片样式',
      tooltip: '为所有图片应用响应式样式（宽度100%，高度自适应）',
      onAction: () => styleAllImages()
    })

    editor.on('init', () => {
      console.log('TinyMCE 编辑器初始化完成')
    })

    editor.on('SelectionChange', () => {
      const selection = editor.selection.getContent({ format: 'text' })
      selectedText.value = selection.trim()
    })

    editor.on('Change', () => {
      content.value = editor.getContent()
      emit('update:modelValue', content.value)
    })

    // 键盘事件处理 - 添加字体大小调整快捷键和拼音导航
    editor.on('keydown', (e) => {
      // 字体大小调整快捷键
      if (e.ctrlKey || e.metaKey) {
        if (e.key === '=' || e.key === '+') {
          // Ctrl/Cmd + Plus: 增大字体
          e.preventDefault()
          increaseFontSize()
        } else if (e.key === '-') {
          // Ctrl/Cmd + Minus: 减小字体
          e.preventDefault()
          decreaseFontSize()
        }
      }

      // 拼音导航处理
      handlePinyinNavigation(e, editor)
    })

    // 添加双击事件处理 - 双击拼音可以编辑
    editor.on('dblclick', (e) => {
      const target = e.target
      if (target && target.closest && target.closest('ruby.pinyin-ruby')) {
        handlePinyinEdit(target.closest('ruby.pinyin-ruby'), editor)
      }
    })

    // 添加右键菜单支持
    editor.on('contextmenu', (e) => {
      const target = e.target
      if (target && target.closest && target.closest('ruby.pinyin-ruby')) {
        e.preventDefault()
        showPinyinContextMenu(target.closest('ruby.pinyin-ruby'), e, editor)
      }
    })

    // 图片样式应用函数
    const applyImageStyles = (images, showMessage = false) => {
      if (!props.autoStyleImages) return

      let styledCount = 0
      images.forEach(img => {
        if (!img.hasAttribute('data-styled')) {
          // 设置图片样式：宽度100%，高度自适应
          img.style.width = '100%'
          img.style.height = 'auto'
          img.style.maxWidth = '100%'
          img.style.display = 'block'
          img.style.margin = '10px auto'
          img.style.borderRadius = '8px'
          img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
          img.style.transition = 'all 0.3s ease'

          // 标记已处理，避免重复设置
          img.setAttribute('data-styled', 'true')
          styledCount++
        }
      })

      // 显示用户反馈
      if (showMessage && styledCount > 0) {
        ElMessage.success(`已为 ${styledCount} 张图片应用响应式样式`)
      }
    }

    // 监听图片插入事件，自动设置样式
    editor.on('NodeChange', (e) => {
      const images = editor.getBody().querySelectorAll('img:not([data-styled])')
      if (images.length > 0) {
        applyImageStyles(images)
      }
    })

    // 监听内容变化，处理粘贴的图片
    editor.on('SetContent', (e) => {
      // 延迟处理，确保内容已完全插入
      setTimeout(() => {
        const images = editor.getBody().querySelectorAll('img:not([data-styled])')
        if (images.length > 0) {
          applyImageStyles(images, true)
        }
      }, 100)
    })

    // 监听命令执行，处理通过工具栏插入的图片
    editor.on('ExecCommand', (e) => {
      if (e.command === 'mceImage' || e.command === 'mceInsertContent') {
        setTimeout(() => {
          const images = editor.getBody().querySelectorAll('img:not([data-styled])')
          if (images.length > 0) {
            applyImageStyles(images, true)
          }
        }, 200)
      }
    })

    // 监听粘贴事件
    editor.on('paste', (e) => {
      setTimeout(() => {
        const images = editor.getBody().querySelectorAll('img:not([data-styled])')
        if (images.length > 0) {
          applyImageStyles(images, true)
        }
      }, 300)
    })
  }
}))

// 监听外部值变化
watch(() => props.modelValue, (newVal) => {
  if (newVal !== content.value) {
    content.value = newVal || ''
  }
}, { immediate: true })

// 处理输入
function handleInput(event) {
  content.value = event.target.getContent()
  emit('update:modelValue', content.value)
}

// 处理内容变化
function handleChange(event) {
  content.value = event.target.getContent()
  emit('update:modelValue', content.value)
}

// 处理选择变化
function handleSelectionChange(event) {
  if (event.target) {
    const selection = event.target.selection.getContent({ format: 'text' })
    selectedText.value = selection.trim()
  }
}

// 添加拼音注音 - 使用标准的 ruby 标签实现字符与拼音一一对应
function addPinyinAnnotation() {
  if (!editorInstance.value || !selectedText.value) {
    ElMessage.warning('请先选择要注音的文字')
    return
  }

  try {
    const text = selectedText.value
    const chars = Array.from(text) // 正确处理Unicode字符
    let annotatedHtml = ''

    chars.forEach((char, index) => {
      if (/[\u4e00-\u9fff]/.test(char)) {
        // 是中文字符，使用 ruby 标签添加拼音
        const pinyinOptions = getAllPinyinOptions(char)
        const defaultPinyin = pinyinOptions[0] || char

        // 使用标准 ruby 标签，添加零宽度空格确保光标可以正常移动
        // 存储所有拼音选项以便后续快速切换
        const pinyinData = JSON.stringify(pinyinOptions).replace(/"/g, '&quot;')
        annotatedHtml += `<ruby class="pinyin-ruby" data-pinyin="${defaultPinyin}" data-char="${char}" data-pinyin-options="${pinyinData}"><rt>${defaultPinyin}</rt><rb>${char}</rb></ruby>&#8203;`
      } else if (char === ' ') {
        // 空格字符，保持原样
        annotatedHtml += '&nbsp;'
      } else {
        // 其他非中文字符，直接添加
        annotatedHtml += char
      }
    })

    // 插入注音内容
    editorInstance.value.selection.setContent(annotatedHtml)

    // 确保光标移动到插入内容的末尾，并添加一个空格便于继续输入
    setTimeout(() => {
      try {
        const body = editorInstance.value.getBody()
        const lastRuby = body.querySelector('ruby.pinyin-ruby:last-of-type')

        if (lastRuby) {
          // 在最后一个拼音注音后添加空格并移动光标
          const range = editorInstance.value.dom.createRng()
          const spaceNode = editorInstance.value.getDoc().createTextNode(' ')

          // 在ruby元素后插入空格
          if (lastRuby.nextSibling) {
            lastRuby.parentNode.insertBefore(spaceNode, lastRuby.nextSibling)
          } else {
            lastRuby.parentNode.appendChild(spaceNode)
          }

          // 将光标移动到空格后
          range.setStart(spaceNode, 1)
          range.collapse(true)
          editorInstance.value.selection.setRng(range)
        }
      } catch (error) {
        console.error('光标定位失败:', error)
      }
    }, 10)

    selectedText.value = ''
    ElMessage.success('拼音注音添加成功')
  } catch (error) {
    console.error('拼音注音错误:', error)
    ElMessage.error('添加拼音注音失败')
  }
}

// 移除拼音注音 - 移除 ruby 标签
function removePinyinAnnotation() {
  if (!editorInstance.value) {
    ElMessage.warning('编辑器未初始化')
    return
  }

  const selectedHtml = editorInstance.value.selection.getContent()
  if (!selectedHtml) {
    ElMessage.warning('请先选择要移除注音的文字')
    return
  }

  // 移除 ruby 标签，保留 rb 标签内的文字内容，处理各种可能的属性
  let cleanHtml = selectedHtml.replace(/<ruby[^>]*class="pinyin-ruby"[^>]*><rt[^>]*>.*?<\/rt><rb[^>]*>(.*?)<\/rb><\/ruby>/g, '$1')
  cleanHtml = cleanHtml.replace(/<ruby[^>]*><rt[^>]*>.*?<\/rt><rb[^>]*>(.*?)<\/rb><\/ruby>/g, '$1')
  // 处理可能的嵌套span标签
  cleanHtml = cleanHtml.replace(/<span>([^<]*)<\/span>/g, '$1')

  editorInstance.value.selection.setContent(cleanHtml)
  selectedText.value = ''
  ElMessage.success('拼音注音移除成功')
}

// 智能拼音注音 - 为所有中文字符添加拼音
function addSmartPinyinAnnotation() {
  if (!editorInstance.value) {
    ElMessage.warning('编辑器未初始化')
    return
  }

  const currentContent = editorInstance.value.getContent()
  if (!currentContent) {
    ElMessage.warning('编辑器内容为空')
    return
  }

  try {
    // 创建临时div来解析HTML
    const tempDiv = document.createElement('div')
    tempDiv.innerHTML = currentContent

    // 递归处理所有文本节点
    function processTextNodes(node) {
      if (node.nodeType === Node.TEXT_NODE) {
        const text = node.textContent
        if (text && /[\u4e00-\u9fff]/.test(text)) {
          // 包含中文字符，需要处理
          const chars = Array.from(text)
          let annotatedHtml = ''

          chars.forEach(char => {
            if (/[\u4e00-\u9fff]/.test(char)) {
              const pinyinOptions = getAllPinyinOptions(char)
              const defaultPinyin = pinyinOptions[0] || char

              const pinyinData = JSON.stringify(pinyinOptions).replace(/"/g, '&quot;')
              annotatedHtml += `<ruby class="pinyin-ruby" data-pinyin="${defaultPinyin}" data-char="${char}" data-pinyin-options="${pinyinData}"><rt>${defaultPinyin}</rt><rb>${char}</rb></ruby>&#8203;`
            } else {
              annotatedHtml += char
            }
          })

          // 创建新的HTML片段替换文本节点
          const wrapper = document.createElement('span')
          wrapper.innerHTML = annotatedHtml
          node.parentNode.replaceChild(wrapper, node)
        }
      } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'RUBY') {
        // 递归处理子节点，但跳过已有的ruby标签
        const children = Array.from(node.childNodes)
        children.forEach(child => processTextNodes(child))
      }
    }

    processTextNodes(tempDiv)

    // 清理多余的span包装
    tempDiv.innerHTML = tempDiv.innerHTML.replace(/<span>([^<]*)<\/span>/g, '$1')

    editorInstance.value.setContent(tempDiv.innerHTML)
    ElMessage.success('智能拼音注音添加成功')
  } catch (error) {
    console.error('智能拼音注音错误:', error)
    ElMessage.error('智能拼音注音失败')
  }
}

// 清理当前格式
function cleanCurrentFormat() {
  if (!editorInstance.value) {
    ElMessage.warning('编辑器未初始化')
    return
  }

  const currentContent = editorInstance.value.getContent()
  if (!currentContent) {
    ElMessage.warning('编辑器内容为空')
    return
  }

  const cleanedContent = cleanWordContent(currentContent)
  editorInstance.value.setContent(cleanedContent)
  ElMessage.success('格式清理完成')
}

// 增大字体
function increaseFontSize() {
  if (!editorInstance.value) {
    return
  }

  let selection = editorInstance.value.selection.getContent()

  // 如果没有选中文字，尝试智能选择
  if (!selection) {
    if (!trySmartSelection()) {
      return // 如果智能选择失败，直接返回，不显示警告
    }
    // 重新获取选择的内容
    selection = editorInstance.value.selection.getContent()
  }

  adjustFontSize(2) // 增加2px
}

// 减小字体
function decreaseFontSize() {
  if (!editorInstance.value) {
    return
  }

  let selection = editorInstance.value.selection.getContent()

  // 如果没有选中文字，尝试智能选择
  if (!selection) {
    if (!trySmartSelection()) {
      return // 如果智能选择失败，直接返回，不显示警告
    }
    // 重新获取选择的内容
    selection = editorInstance.value.selection.getContent()
  }

  adjustFontSize(-2) // 减少2px
}

// 尝试智能选择文本
function trySmartSelection() {
  if (!editorInstance.value) {
    return false
  }

  try {
    const currentNode = editorInstance.value.selection.getNode()
    const range = editorInstance.value.selection.getRng()

    // 方法1: 如果光标在文本节点中，选择整个文本节点
    if (currentNode.nodeType === Node.TEXT_NODE && currentNode.textContent.trim()) {
      const newRange = editorInstance.value.dom.createRng()
      newRange.selectNodeContents(currentNode)
      editorInstance.value.selection.setRng(newRange)
      const content = editorInstance.value.selection.getContent()
      return content && content.trim().length > 0
    }

    // 方法2: 如果光标在元素中，查找最近的文本内容
    let targetElement = currentNode
    while (targetElement && targetElement !== editorInstance.value.getBody()) {
      if (targetElement.textContent && targetElement.textContent.trim()) {
        // 优先选择段落、span等文本容器
        if (['P', 'DIV', 'SPAN', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI'].includes(targetElement.tagName)) {
          const newRange = editorInstance.value.dom.createRng()
          newRange.selectNodeContents(targetElement)
          editorInstance.value.selection.setRng(newRange)
          const content = editorInstance.value.selection.getContent()
          if (content && content.trim().length > 0) {
            return true
          }
        }
      }
      targetElement = targetElement.parentNode
    }

    // 方法3: 查找光标附近的文本节点
    const body = editorInstance.value.getBody()
    const walker = editorInstance.value.dom.createTreeWalker(
      body,
      NodeFilter.SHOW_TEXT,
      (node) => {
        return node.textContent.trim() ? NodeFilter.FILTER_ACCEPT : NodeFilter.FILTER_REJECT
      },
      false
    )

    let node
    while (node = walker.nextNode()) {
      if (node.textContent.trim()) {
        const newRange = editorInstance.value.dom.createRng()
        newRange.selectNodeContents(node)
        editorInstance.value.selection.setRng(newRange)
        return true
      }
    }

    // 方法4: 最后尝试选择整个编辑器内容
    const bodyContent = body.textContent
    if (bodyContent && bodyContent.trim()) {
      const newRange = editorInstance.value.dom.createRng()
      newRange.selectNodeContents(body)
      editorInstance.value.selection.setRng(newRange)
      return true
    }

  } catch (error) {
    console.warn('智能选择失败:', error)
  }

  return false
}

// 设置行间距
function setLineHeight(lineHeight) {
  if (!editorInstance.value) {
    return
  }

  const selectedContent = editorInstance.value.selection.getContent()

  // 如果没有选中内容，尝试智能选择
  if (!selectedContent) {
    if (!trySmartSelection()) {
      // 如果智能选择失败，对整个编辑器内容应用行间距
      const body = editorInstance.value.getBody()
      if (body) {
        body.style.lineHeight = lineHeight
        return
      }
    }
  }

  // 对选中的内容应用行间距
  const currentNode = editorInstance.value.selection.getNode()

  // 查找最近的块级元素
  let targetElement = currentNode
  while (targetElement && targetElement !== editorInstance.value.getBody()) {
    if (['P', 'DIV', 'H1', 'H2', 'H3', 'H4', 'H5', 'H6', 'LI', 'BLOCKQUOTE'].includes(targetElement.tagName)) {
      targetElement.style.lineHeight = lineHeight
      return
    }
    targetElement = targetElement.parentNode
  }

  // 如果没有找到合适的块级元素，包装选中内容
  const wrappedContent = `<div style="line-height: ${lineHeight};">${selectedContent}</div>`
  editorInstance.value.selection.setContent(wrappedContent)
}

// 显示内容统计
function showContentStats() {
  if (!editorInstance.value) {
    return
  }

  calculateContentStats()
  showStats.value = true
}

// 计算内容统计
function calculateContentStats() {
  if (!editorInstance.value) {
    return
  }

  const htmlContent = editorInstance.value.getContent()
  const textContent = editorInstance.value.getContent({ format: 'text' })

  // 基础统计
  const characters = textContent.length
  const charactersNoSpaces = textContent.replace(/\s/g, '').length

  // 中文字符统计
  const chineseChars = (textContent.match(/[\u4e00-\u9fff]/g) || []).length

  // 拼音注音统计
  const pinyinAnnotations = (htmlContent.match(/<ruby[^>]*class="pinyin-ruby"[^>]*>/g) || []).length

  // 段落统计
  const paragraphs = Math.max(1, (htmlContent.match(/<p[^>]*>/g) || []).length)

  // 句子统计（基于中文句号、问号、感叹号）
  const sentences = Math.max(1, (textContent.match(/[。！？.!?]/g) || []).length)

  // 词语统计（中文按字符计算，英文按单词计算）
  const englishWords = (textContent.match(/[a-zA-Z]+/g) || []).length
  const words = chineseChars + englishWords

  // 阅读时间估算（中文：300字/分钟，英文：200词/分钟）
  const readingTime = Math.ceil((chineseChars / 300 + englishWords / 200))

  contentStats.value = {
    characters,
    charactersNoSpaces,
    words,
    paragraphs,
    sentences,
    readingTime,
    chineseChars,
    pinyinAnnotations
  }
}

// 切换格式刷状态
function toggleFormatBrush() {
  formatBrushActive.value = !formatBrushActive.value

  if (formatBrushActive.value) {
    // 激活格式刷，等待用户选择源格式
    ElMessage.info('格式刷已激活，请选择要复制格式的文字')

    // 监听选择变化
    if (editorInstance.value) {
      editorInstance.value.on('SelectionChange', handleFormatBrushSelection)
    }
  } else {
    // 取消格式刷
    copiedFormat.value = null
    if (editorInstance.value) {
      editorInstance.value.off('SelectionChange', handleFormatBrushSelection)
    }
    ElMessage.info('格式刷已取消')
  }
}

// 处理格式刷选择
function handleFormatBrushSelection() {
  if (!formatBrushActive.value || !editorInstance.value) {
    return
  }

  const selectedContent = editorInstance.value.selection.getContent()
  if (!selectedContent) {
    return
  }

  if (!copiedFormat.value) {
    // 第一次选择：复制格式
    copiedFormat.value = extractFormat(selectedContent)
    ElMessage.success('格式已复制，请选择要应用格式的文字')
  } else {
    // 第二次选择：应用格式
    applyFormat(selectedContent)

    // 重置格式刷状态
    formatBrushActive.value = false
    copiedFormat.value = null
    editorInstance.value.off('SelectionChange', handleFormatBrushSelection)
    ElMessage.success('格式已应用')
  }
}

// 提取格式
function extractFormat(htmlContent) {
  const tempDiv = document.createElement('div')
  tempDiv.innerHTML = htmlContent

  const firstElement = tempDiv.firstElementChild || tempDiv
  const computedStyle = window.getComputedStyle ? window.getComputedStyle(firstElement) : {}

  return {
    fontSize: firstElement.style.fontSize || computedStyle.fontSize,
    fontWeight: firstElement.style.fontWeight || computedStyle.fontWeight,
    fontStyle: firstElement.style.fontStyle || computedStyle.fontStyle,
    color: firstElement.style.color || computedStyle.color,
    backgroundColor: firstElement.style.backgroundColor || computedStyle.backgroundColor,
    textDecoration: firstElement.style.textDecoration || computedStyle.textDecoration,
    lineHeight: firstElement.style.lineHeight || computedStyle.lineHeight,
    textAlign: firstElement.style.textAlign || computedStyle.textAlign
  }
}

// 应用格式
function applyFormat(targetContent) {
  if (!copiedFormat.value || !editorInstance.value) {
    return
  }

  const format = copiedFormat.value
  let styleString = ''

  Object.entries(format).forEach(([key, value]) => {
    if (value && value !== 'normal' && value !== 'none') {
      const cssKey = key.replace(/([A-Z])/g, '-$1').toLowerCase()
      styleString += `${cssKey}: ${value}; `
    }
  })

  if (styleString) {
    const wrappedContent = `<span style="${styleString}">${targetContent}</span>`
    editorInstance.value.selection.setContent(wrappedContent)
  }
}



// 插入符号
// function insertSymbol(symbol) {
//   if (!editorInstance.value) {
//     return
//   }
//
//   editorInstance.value.insertContent(symbol)
//   editorInstance.value.focus()
// }

// 统一的字体大小调整函数
function adjustFontSize(sizeChange) {
  if (!editorInstance.value) {
    return
  }

  const selectedContent = editorInstance.value.selection.getContent()
  if (!selectedContent) {
    return
  }

  // 检查选区是否包含拼音注音
  const containsRuby = selectedContent.includes('<ruby') || selectedContent.includes('pinyin-ruby')

  // 获取当前选区的节点
  const currentNode = editorInstance.value.selection.getNode()
  const currentSize = getCurrentFontSize(currentNode)
  const newSize = calculateNewFontSize(currentSize, sizeChange)

  // 如果字体大小没有变化，直接返回
  if (newSize === currentSize) {
    return
  }

  // 创建书签保存选区位置
  const bookmark = editorInstance.value.selection.getBookmark(2, true)

  try {
    // 开始撤销管理器的事务
    editorInstance.value.undoManager.transact(() => {
      if (containsRuby) {
        // 如果包含拼音注音，使用自定义处理方法
        adjustFontSizeForRubyContent(selectedContent, newSize)
      } else {
        // 普通文本，使用TinyMCE的内置命令
        editorInstance.value.execCommand('FontSize', false, `${newSize}px`)
      }
    })

    // 恢复选区 - 优化选区恢复逻辑
    setTimeout(() => {
      try {
        // 先尝试恢复书签
        editorInstance.value.selection.moveToBookmark(bookmark)

        // 验证选区是否正确恢复
        const restoredContent = editorInstance.value.selection.getContent()
        if (!restoredContent || restoredContent.length < selectedContent.length * 0.5) {
          // 如果恢复的内容太少，尝试智能恢复
          smartRestoreSelection(newSize)
        }
      } catch (error) {
        // 书签恢复失败，尝试智能恢复
        smartRestoreSelection(newSize)
      }
    }, 10)

  } catch (error) {
    console.error('字体大小调整失败:', error)

    // 如果出错，尝试恢复原始选区
    try {
      editorInstance.value.selection.moveToBookmark(bookmark)
    } catch (restoreError) {
      console.error('选区恢复失败:', restoreError)
    }
  }
}

// 为包含拼音注音的内容调整字体大小
function adjustFontSizeForRubyContent(selectedContent, newSize) {
  try {
    // 使用正则表达式处理HTML内容，更简单可靠
    let processedContent = selectedContent

    // 处理ruby标签内的rb和rt元素
    processedContent = processedContent.replace(/<ruby([^>]*)>([\s\S]*?)<\/ruby>/g, (match, rubyAttrs, rubyContent) => {
      // 处理rb标签（汉字）
      let newRubyContent = rubyContent.replace(/<rb([^>]*)>([\s\S]*?)<\/rb>/g, (rbMatch, rbAttrs, rbText) => {
        // 移除现有的font-size样式
        let newRbAttrs = rbAttrs.replace(/style\s*=\s*"[^"]*font-size[^"]*"/g, '')
        // 添加新的font-size样式
        if (newRbAttrs.includes('style=')) {
          newRbAttrs = newRbAttrs.replace(/style\s*=\s*"([^"]*)"/, `style="$1; font-size: ${newSize}px;"`)
        } else {
          newRbAttrs += ` style="font-size: ${newSize}px;"`
        }
        return `<rb${newRbAttrs}>${rbText}</rb>`
      })

      // 处理rt标签（拼音）
      newRubyContent = newRubyContent.replace(/<rt([^>]*)>([\s\S]*?)<\/rt>/g, (rtMatch, rtAttrs, rtText) => {
        const pinyinSize = Math.round(newSize * 0.75)
        // 移除现有的font-size样式
        let newRtAttrs = rtAttrs.replace(/style\s*=\s*"[^"]*font-size[^"]*"/g, '')
        // 添加新的font-size样式
        if (newRtAttrs.includes('style=')) {
          newRtAttrs = newRtAttrs.replace(/style\s*=\s*"([^"]*)"/, `style="$1; font-size: ${pinyinSize}px;"`)
        } else {
          newRtAttrs += ` style="font-size: ${pinyinSize}px;"`
        }
        return `<rt${newRtAttrs}>${rtText}</rt>`
      })

      return `<ruby${rubyAttrs}>${newRubyContent}</ruby>`
    })

    // 处理其他文本内容（非ruby标签内的文本）
    // 将非ruby标签的文本包装在span中
    processedContent = processedContent.replace(/([^>])([^<]+)(?=<|$)/g, (match, prefix, text) => {
      // 跳过已经在标签内的文本
      if (text.trim() && !text.includes('<') && !text.includes('>')) {
        return `${prefix}<span style="font-size: ${newSize}px;">${text}</span>`
      }
      return match
    })

    // 将处理后的内容替换回编辑器
    editorInstance.value.selection.setContent(processedContent)

  } catch (error) {
    console.error('处理拼音内容字体大小失败:', error)
    // 如果自定义处理失败，回退到默认方法
    editorInstance.value.execCommand('FontSize', false, `${newSize}px`)
  }
}

// 计算新的字体大小
function calculateNewFontSize(currentSize, sizeChange) {
  const newSize = currentSize + sizeChange

  // 限制字体大小范围：最小8px，最大200px
  return Math.max(8, Math.min(200, newSize))
}

// 智能选区恢复 - 简化版本
function smartRestoreSelection(targetFontSize) {
  try {
    // 查找最近修改的带有目标字体大小的元素
    const body = editorInstance.value.getBody()
    const targetElements = body.querySelectorAll(`span[style*="font-size: ${targetFontSize}px"]`)

    if (targetElements.length > 0) {
      // 选择最后一个修改的元素
      const lastElement = targetElements[targetElements.length - 1]
      const range = editorInstance.value.dom.createRng()
      range.selectNodeContents(lastElement)
      editorInstance.value.selection.setRng(range)
    } else {
      // 如果找不到目标元素，查找任何带有字体样式的元素
      const styledElements = body.querySelectorAll('span[style*="font-size"]')
      if (styledElements.length > 0) {
        const lastElement = styledElements[styledElements.length - 1]
        const range = editorInstance.value.dom.createRng()
        range.selectNodeContents(lastElement)
        editorInstance.value.selection.setRng(range)
      }
    }
  } catch (error) {
    console.error('智能选区恢复失败:', error)
  }
}

// 获取当前字体大小 - 改进版本
function getCurrentFontSize(node) {
  let currentSize = 14 // 默认字体大小

  // 向上遍历DOM树查找字体大小
  let element = node
  while (element && element.nodeType === 1) {
    // 首先检查内联样式
    if (element.style && element.style.fontSize) {
      const inlineSize = parseInt(element.style.fontSize)
      if (!isNaN(inlineSize)) {
        currentSize = inlineSize
        break
      }
    }

    // 然后检查计算样式
    const style = window.getComputedStyle ? window.getComputedStyle(element) : element.currentStyle
    if (style && style.fontSize) {
      const fontSize = parseInt(style.fontSize)
      if (!isNaN(fontSize)) {
        currentSize = fontSize
        break
      }
    }
    element = element.parentNode
  }

  return currentSize
}

// 打开响应式预览
function openResponsivePreview() {
  if (!editorInstance.value) {
    ElMessage.warning('编辑器未初始化')
    return
  }

  content.value = editorInstance.value.getContent()
  showPreview.value = true
}

// 关闭预览
function closePreview() {
  showPreview.value = false
}

// 选择设备预设
function selectDevicePreset(preset) {
  if (preset.name === '自定义') {
    previewWidth.value = customWidth.value
    previewHeight.value = customHeight.value
  } else {
    previewWidth.value = preset.width
    previewHeight.value = preset.height
    customWidth.value = preset.width
    customHeight.value = preset.height
  }

  // 切换设备后，滚动到预览内容顶部
  nextTick(() => {
    const previewFrame = document.querySelector('.preview-frame')
    if (previewFrame) {
      previewFrame.scrollTop = 0
    }
  })
}

// 更新自定义尺寸
function updateCustomSize() {
  previewWidth.value = customWidth.value
  previewHeight.value = customHeight.value
}

// 打开符号对话框
function openSymbolDialog() {
  showSymbolDialog.value = true
}

// 关闭符号对话框
function closeSymbolDialog() {
  showSymbolDialog.value = false
  symbolSearchText.value = ''
  selectedSymbolCategory.value = 'all'
}

// 插入符号
function insertSymbol(symbol) {
  if (!editorInstance.value) {
    return
  }

  editorInstance.value.insertContent(symbol)
  editorInstance.value.focus()

  // 插入后不关闭对话框，方便连续插入
  ElMessage.success(`已插入符号：${symbol}`)
}

// 显示快捷键帮助
function showShortcutsHelp() {
  ElMessageBox({
    title: '⌨️ 快捷键帮助',
    message: h('div', { style: 'line-height: 1.8; font-size: 14px;' }, [
      h('div', { style: 'margin-bottom: 20px;' }, [
        h('h4', { style: 'color: #409eff; margin: 0 0 10px 0; font-size: 16px;' }, '🚀 编辑快捷键'),
        h('div', { style: 'display: grid; grid-template-columns: 1fr 2fr; gap: 8px; margin-left: 10px;' }, [
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Shift + Enter'),
          h('span', '插入换行符'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + S'),
          h('span', '快速保存'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + Shift + X'),
          h('span', '清除格式'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + Z'),
          h('span', '撤销'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + Y'),
          h('span', '重做'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + B'),
          h('span', '加粗'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + I'),
          h('span', '斜体'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Ctrl + U'),
          h('span', '下划线')
        ])
      ]),
      h('div', { style: 'margin-bottom: 20px;' }, [
        h('h4', { style: 'color: #67c23a; margin: 0 0 10px 0; font-size: 16px;' }, '🎯 拼音功能'),
        h('div', { style: 'display: grid; grid-template-columns: 1fr 2fr; gap: 8px; margin-left: 10px;' }, [
          h('span', { style: 'font-weight: bold;' }, '双击拼音'),
          h('span', '编辑多音字'),
          h('span', { style: 'font-weight: bold;' }, '右键拼音'),
          h('span', '快速切换读音'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, 'Delete'),
          h('span', '删除拼音注音'),
          h('kbd', { style: 'background: #f5f5f5; padding: 2px 6px; border-radius: 3px; font-family: monospace;' }, '← →'),
          h('span', '拼音导航')
        ])
      ]),
      h('div', [
        h('h4', { style: 'color: #e6a23c; margin: 0 0 10px 0; font-size: 16px;' }, '💡 实用技巧'),
        h('ul', { style: 'margin: 0; padding-left: 20px;' }, [
          h('li', '右键菜单提供常用操作'),
          h('li', '符号面板支持搜索和分类'),
          h('li', '模板可以快速插入常用内容'),
          h('li', '预览功能支持多种设备尺寸'),
          h('li', '自动保存防止内容丢失')
        ])
      ])
    ]),
    showCancelButton: false,
    confirmButtonText: '知道了',
    customClass: 'shortcuts-help-dialog'
  })
}

// 打开模板对话框
async function openTemplateDialog() {
  try {
    templateLoading.value = true
    showTemplateDialog.value = true

    // 从API获取模板列表
    const response = await api.get('/templates/', {
      params: { is_active: true, limit: 100 }
    })
    availableTemplates.value = response.data

    if (availableTemplates.value.length === 0) {
      ElMessage.warning('暂无可用模板')
      showTemplateDialog.value = false
    }
  } catch (error) {
    console.error('加载模板失败:', error)
    ElMessage.error('加载模板失败')
    showTemplateDialog.value = false
  } finally {
    templateLoading.value = false
  }
}

// 关闭模板对话框
function closeTemplateDialog() {
  showTemplateDialog.value = false
  templateSearchText.value = ''
  selectedTemplateCategory.value = ''
  availableTemplates.value = []
}

// 插入选中的模板
async function insertSelectedTemplate(template) {
  try {
    // 调用使用模板API（增加使用次数）
    await api.post(`/templates/${template.id}/use`)

    // 插入模板内容
    if (editorInstance.value) {
      editorInstance.value.insertContent(template.content)
      ElMessage.success(`已插入模板：${template.name}`)
      closeTemplateDialog()
    }
  } catch (error) {
    console.error('插入模板失败:', error)
    ElMessage.error('插入模板失败')
  }
}

// 获取模板分类列表
const templateCategories = computed(() => {
  const categories = [...new Set(availableTemplates.value.map(t => t.category).filter(Boolean))]
  return categories.sort()
})

// 获取模板预览内容
function getTemplatePreview(content) {
  if (!content) return '暂无内容'

  // 移除HTML标签，只保留文本内容
  const textContent = content.replace(/<[^>]*>/g, ' ').replace(/\s+/g, ' ').trim()

  // 限制预览长度
  const maxLength = 100
  if (textContent.length > maxLength) {
    return textContent.substring(0, maxLength) + '...'
  }

  return textContent || '暂无内容'
}

// 插入模板（保留原函数作为兼容）
async function insertTemplate() {
  await openTemplateDialog()
}

// 为所有图片应用样式
const styleAllImages = () => {
  if (!editorInstance.value) {
    ElMessage.warning('编辑器未初始化')
    return
  }

  const allImages = editorInstance.value.getBody().querySelectorAll('img')
  if (allImages.length === 0) {
    ElMessage.info('当前内容中没有图片')
    return
  }

  // 移除所有图片的 data-styled 标记，强制重新应用样式
  allImages.forEach(img => {
    img.removeAttribute('data-styled')
  })

  // 应用样式
  let styledCount = 0
  allImages.forEach(img => {
    img.style.width = '100%'
    img.style.height = 'auto'
    img.style.maxWidth = '100%'
    img.style.display = 'block'
    img.style.margin = '10px auto'
    img.style.borderRadius = '8px'
    img.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.1)'
    img.style.transition = 'all 0.3s ease'
    img.setAttribute('data-styled', 'true')
    styledCount++
  })

  ElMessage.success(`已为 ${styledCount} 张图片应用响应式样式`)
}




// 清理Word内容的函数
function cleanWordContent(content) {
  if (!content) return content

  // 移除Word特有的样式和标签
  let cleanContent = content
    // 移除Word的命名空间和特殊属性
    .replace(/\s*xmlns:[^=]*="[^"]*"/g, '')
    .replace(/\s*o:[^=]*="[^"]*"/g, '')
    .replace(/\s*w:[^=]*="[^"]*"/g, '')
    .replace(/\s*v:[^=]*="[^"]*"/g, '')
    .replace(/\s*m:[^=]*="[^"]*"/g, '')
    // 移除Word的样式类
    .replace(/\s*class="[^"]*Mso[^"]*"/g, '')
    .replace(/\s*class="[^"]*Word[^"]*"/g, '')
    // 移除Word的内联样式
    .replace(/\s*style="[^"]*mso-[^"]*"/g, '')
    // 移除Word的条件注释
    .replace(/<!--\[if[^>]*>[\s\S]*?<!\[endif\]-->/g, '')
    // 移除Word的特殊标签
    .replace(/<o:p[^>]*>[\s\S]*?<\/o:p>/g, '')
    .replace(/<w:[^>]*>[\s\S]*?<\/w:[^>]*>/g, '')
    .replace(/<v:[^>]*>[\s\S]*?<\/v:[^>]*>/g, '')
    .replace(/<m:[^>]*>[\s\S]*?<\/m:[^>]*>/g, '')
    // 清理多余的空白字符
    .replace(/\s+/g, ' ')
    .replace(/&nbsp;+/g, '&nbsp;')
    // 移除空的段落和span标签
    .replace(/<p[^>]*>\s*<\/p>/g, '')
    .replace(/<span[^>]*>\s*<\/span>/g, '')
    // 处理拼音注音相关的内容，保持ruby标签结构
    .replace(/<ruby[^>]*>([\s\S]*?)<\/ruby>/g, (match, content) => {
      // 如果包含rt和rb标签，保持结构
      if (content.includes('<rt>') && content.includes('<rb>')) {
        return match
      }
      // 否则移除ruby标签，保留内容
      return content.replace(/<[^>]*>/g, '')
    })

  return cleanContent.trim()
}

// 拼音导航处理
function handlePinyinNavigation(e, editor) {
  const selection = editor.selection
  const range = selection.getRng()

  // 检查当前光标是否在拼音区域
  const currentNode = selection.getNode()
  const rubyElement = currentNode.closest ? currentNode.closest('ruby.pinyin-ruby') : null

  if (rubyElement) {
    // 在拼音区域内，处理特殊导航
    if (e.key === 'ArrowRight') {
      // 右箭头：移动到拼音后面
      e.preventDefault()
      moveCaretAfterPinyin(rubyElement, editor)
    } else if (e.key === 'ArrowLeft') {
      // 左箭头：移动到拼音前面
      e.preventDefault()
      moveCaretBeforePinyin(rubyElement, editor)
    } else if (e.key === 'Delete' || e.key === 'Backspace') {
      // 删除键：删除整个拼音注音
      e.preventDefault()
      deletePinyinAnnotation(rubyElement, editor)
    }
  } else {
    // 不在拼音区域，检查是否需要跳过拼音
    if (e.key === 'ArrowRight' || e.key === 'ArrowLeft') {
      handleArrowKeyNavigation(e, editor)
    }
  }
}

// 移动光标到拼音后面
function moveCaretAfterPinyin(rubyElement, editor) {
  try {
    const range = editor.dom.createRng()
    const nextNode = rubyElement.nextSibling

    if (nextNode) {
      if (nextNode.nodeType === Node.TEXT_NODE) {
        range.setStart(nextNode, 0)
      } else {
        range.setStartAfter(rubyElement)
      }
    } else {
      range.setStartAfter(rubyElement)
    }

    range.collapse(true)
    editor.selection.setRng(range)
  } catch (error) {
    console.error('移动光标失败:', error)
  }
}

// 移动光标到拼音前面
function moveCaretBeforePinyin(rubyElement, editor) {
  try {
    const range = editor.dom.createRng()
    const prevNode = rubyElement.previousSibling

    if (prevNode && prevNode.nodeType === Node.TEXT_NODE) {
      range.setStart(prevNode, prevNode.textContent.length)
    } else {
      range.setStartBefore(rubyElement)
    }

    range.collapse(true)
    editor.selection.setRng(range)
  } catch (error) {
    console.error('移动光标失败:', error)
  }
}

// 删除拼音注音
function deletePinyinAnnotation(rubyElement, editor) {
  try {
    const char = rubyElement.getAttribute('data-char') || rubyElement.querySelector('rb')?.textContent || ''

    // 创建一个文本节点替换ruby元素
    const textNode = editor.getDoc().createTextNode(char)
    rubyElement.parentNode.replaceChild(textNode, rubyElement)

    // 将光标移动到文本节点后面
    const range = editor.dom.createRng()
    range.setStart(textNode, char.length)
    range.collapse(true)
    editor.selection.setRng(range)

    ElMessage.success('拼音注音已移除')
  } catch (error) {
    console.error('删除拼音注音失败:', error)
  }
}

// 处理箭头键导航
function handleArrowKeyNavigation(e, editor) {
  const selection = editor.selection
  const range = selection.getRng()

  // 检查光标附近是否有拼音元素
  if (e.key === 'ArrowRight') {
    const nextNode = range.endContainer.nextSibling
    if (nextNode && nextNode.classList && nextNode.classList.contains('pinyin-ruby')) {
      // 跳过拼音，移动到拼音后面
      e.preventDefault()
      moveCaretAfterPinyin(nextNode, editor)
    }
  } else if (e.key === 'ArrowLeft') {
    const prevNode = range.startContainer.previousSibling
    if (prevNode && prevNode.classList && prevNode.classList.contains('pinyin-ruby')) {
      // 跳过拼音，移动到拼音前面
      e.preventDefault()
      moveCaretBeforePinyin(prevNode, editor)
    }
  }
}

// 获取字符的所有拼音选项（包括多音字）
function getAllPinyinOptions(char) {
  try {
    // 获取所有可能的拼音（包括多音字）
    const allPinyins = pinyin(char, {
      toneType: 'symbol',
      type: 'array',
      multiple: true // 获取多音字的所有读音
    })

    // 如果是多音字，返回所有读音
    if (Array.isArray(allPinyins) && allPinyins.length > 0) {
      // 去重并排序
      const uniquePinyins = [...new Set(allPinyins.flat())]
      return uniquePinyins.length > 0 ? uniquePinyins : [char]
    }

    // 如果不是多音字，获取默认读音
    const defaultPinyin = pinyin(char, {
      toneType: 'symbol',
      type: 'array'
    })[0]

    return defaultPinyin ? [defaultPinyin] : [char]
  } catch (error) {
    console.error('获取拼音失败:', error)
    return [char]
  }
}

// 显示拼音右键菜单
function showPinyinContextMenu(rubyElement, event, editor) {
  const currentChar = rubyElement.getAttribute('data-char') || rubyElement.querySelector('rb')?.textContent || ''
  const currentPinyin = rubyElement.getAttribute('data-pinyin') || rubyElement.querySelector('rt')?.textContent || ''
  const pinyinOptionsStr = rubyElement.getAttribute('data-pinyin-options') || '[]'

  let pinyinOptions = []
  try {
    pinyinOptions = JSON.parse(pinyinOptionsStr.replace(/&quot;/g, '"'))
  } catch (error) {
    pinyinOptions = getAllPinyinOptions(currentChar)
  }

  // 创建右键菜单
  const menuItems = []

  // 如果是多音字，显示所有选项
  if (pinyinOptions.length > 1) {
    menuItems.push({
      text: `多音字选择 (${currentChar})`,
      disabled: true,
      style: 'font-weight: bold; color: #409eff;'
    })

    pinyinOptions.forEach(option => {
      menuItems.push({
        text: option,
        selected: option === currentPinyin,
        onclick: () => {
          updatePinyinAnnotation(rubyElement, option, currentChar, editor)
        }
      })
    })

    menuItems.push({ text: '---' }) // 分隔线
  }

  // 音调调整选项
  const basePinyin = removeTone(currentPinyin)
  if (basePinyin) {
    menuItems.push({
      text: '音调调整',
      disabled: true,
      style: 'font-weight: bold; color: #67c23a;'
    })

    const tones = [
      { name: '一声', symbol: 'ā', tone: 1 },
      { name: '二声', symbol: 'á', tone: 2 },
      { name: '三声', symbol: 'ǎ', tone: 3 },
      { name: '四声', symbol: 'à', tone: 4 },
      { name: '轻声', symbol: 'a', tone: 0 }
    ]

    tones.forEach(tone => {
      const tonedPinyin = applyTone(basePinyin, tone.tone)
      menuItems.push({
        text: `${tone.name} (${tonedPinyin})`,
        selected: tonedPinyin === currentPinyin,
        onclick: () => {
          updatePinyinAnnotation(rubyElement, tonedPinyin, currentChar, editor)
        }
      })
    })

    menuItems.push({ text: '---' }) // 分隔线
  }

  // 其他操作
  menuItems.push(
    {
      text: '✏️ 自定义编辑',
      onclick: () => handlePinyinEdit(rubyElement, editor)
    },
    {
      text: '🗑️ 删除拼音',
      onclick: () => deletePinyinAnnotation(rubyElement, editor)
    }
  )

  // 显示自定义右键菜单
  showCustomContextMenu(event.clientX, event.clientY, menuItems)
}

// 处理拼音编辑
function handlePinyinEdit(rubyElement, editor) {
  const currentPinyin = rubyElement.getAttribute('data-pinyin') || rubyElement.querySelector('rt')?.textContent || ''
  const currentChar = rubyElement.getAttribute('data-char') || rubyElement.querySelector('rb')?.textContent || ''
  const pinyinOptionsStr = rubyElement.getAttribute('data-pinyin-options') || '[]'

  let pinyinOptions = []
  try {
    pinyinOptions = JSON.parse(pinyinOptionsStr.replace(/&quot;/g, '"'))
  } catch (error) {
    pinyinOptions = getAllPinyinOptions(currentChar)
  }

  // 如果是多音字，显示选择对话框
  if (pinyinOptions.length > 1) {
    ElMessageBox({
      title: `编辑拼音注音 - ${currentChar}`,
      message: h('div', [
        h('p', { style: 'margin-bottom: 15px; color: #409eff;' }, '这是一个多音字，请选择正确的读音：'),
        h('div', {
          style: 'display: flex; flex-wrap: wrap; gap: 8px; margin-bottom: 15px;'
        }, pinyinOptions.map(option =>
          h('button', {
            style: `
              padding: 8px 16px;
              border: 2px solid ${option === currentPinyin ? '#409eff' : '#dcdfe6'};
              background: ${option === currentPinyin ? '#409eff' : '#fff'};
              color: ${option === currentPinyin ? '#fff' : '#606266'};
              border-radius: 6px;
              cursor: pointer;
              font-size: 16px;
              font-weight: ${option === currentPinyin ? 'bold' : 'normal'};
              transition: all 0.2s ease;
            `,
            onClick: () => {
              updatePinyinAnnotation(rubyElement, option, currentChar, editor)
              ElMessageBox.close()
            }
          }, option)
        )),
        h('p', { style: 'margin-top: 15px; font-size: 12px; color: #909399;' }, '提示：也可以右键点击拼音快速切换')
      ]),
      showCancelButton: true,
      confirmButtonText: '自定义输入',
      cancelButtonText: '取消'
    }).then(() => {
      // 用户选择自定义输入
      showCustomPinyinInput(rubyElement, currentPinyin, currentChar, editor)
    }).catch(() => {
      // 用户取消
    })
  } else {
    // 不是多音字，直接显示输入框
    showCustomPinyinInput(rubyElement, currentPinyin, currentChar, editor)
  }
}

// 显示自定义拼音输入
function showCustomPinyinInput(rubyElement, currentPinyin, currentChar, editor) {
  ElMessageBox.prompt(`自定义拼音注音 - ${currentChar}`, '拼音编辑', {
    confirmButtonText: '确定',
    cancelButtonText: '取消',
    inputValue: currentPinyin,
    inputPlaceholder: '请输入拼音（如：zhōng）',
    beforeClose: (action, instance, done) => {
      if (action === 'confirm') {
        const newPinyin = instance.inputValue.trim()
        if (!newPinyin) {
          ElMessage.warning('拼音不能为空')
          return false
        }

        // 更新拼音
        updatePinyinAnnotation(rubyElement, newPinyin, currentChar, editor)
        done()
      } else {
        done()
      }
    }
  }).catch(() => {
    // 用户取消
  })
}

// 移除拼音的声调
function removeTone(pinyin) {
  if (!pinyin) return ''

  // 声调字符映射
  const toneMap = {
    'ā': 'a', 'á': 'a', 'ǎ': 'a', 'à': 'a',
    'ē': 'e', 'é': 'e', 'ě': 'e', 'è': 'e',
    'ī': 'i', 'í': 'i', 'ǐ': 'i', 'ì': 'i',
    'ō': 'o', 'ó': 'o', 'ǒ': 'o', 'ò': 'o',
    'ū': 'u', 'ú': 'u', 'ǔ': 'u', 'ù': 'u',
    'ǖ': 'ü', 'ǘ': 'ü', 'ǚ': 'ü', 'ǜ': 'ü', 'ü': 'ü'
  }

  return pinyin.split('').map(char => toneMap[char] || char).join('')
}

// 为拼音添加声调
function applyTone(basePinyin, tone) {
  if (!basePinyin || tone === 0) return basePinyin

  // 声调规则：a > o > e > i > u > ü
  const toneChars = {
    1: { 'a': 'ā', 'o': 'ō', 'e': 'ē', 'i': 'ī', 'u': 'ū', 'ü': 'ǖ' },
    2: { 'a': 'á', 'o': 'ó', 'e': 'é', 'i': 'í', 'u': 'ú', 'ü': 'ǘ' },
    3: { 'a': 'ǎ', 'o': 'ǒ', 'e': 'ě', 'i': 'ǐ', 'u': 'ǔ', 'ü': 'ǚ' },
    4: { 'a': 'à', 'o': 'ò', 'e': 'è', 'i': 'ì', 'u': 'ù', 'ü': 'ǜ' }
  }

  const toneMap = toneChars[tone]
  if (!toneMap) return basePinyin

  // 按优先级查找要标调的字母
  const priority = ['a', 'o', 'e', 'i', 'u', 'ü']

  for (const vowel of priority) {
    if (basePinyin.includes(vowel)) {
      return basePinyin.replace(vowel, toneMap[vowel] || vowel)
    }
  }

  return basePinyin
}

// 显示自定义右键菜单
function showCustomContextMenu(x, y, menuItems) {
  // 移除已存在的菜单
  const existingMenu = document.querySelector('.pinyin-context-menu')
  if (existingMenu) {
    existingMenu.remove()
  }

  // 创建菜单容器
  const menu = document.createElement('div')
  menu.className = 'pinyin-context-menu'

  // 先设置基本样式，不设置位置
  menu.style.cssText = `
    position: fixed;
    background: white;
    border: 1px solid #e4e7ed;
    border-radius: 8px;
    box-shadow: 0 8px 24px rgba(0, 0, 0, 0.12);
    padding: 8px 0;
    z-index: 10000;
    min-width: 200px;
    max-width: 280px;
    font-size: 14px;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    opacity: 0;
    transform: scale(0.95);
    transition: all 0.15s ease-out;
    pointer-events: none;
  `

  // 添加菜单项
  menuItems.forEach(item => {
    if (item.text === '---') {
      // 分隔线
      const separator = document.createElement('div')
      separator.style.cssText = `
        height: 1px;
        background: linear-gradient(90deg, transparent, #e4e7ed, transparent);
        margin: 8px 16px;
        opacity: 0.6;
      `
      menu.appendChild(separator)
    } else {
      // 菜单项
      const menuItem = document.createElement('div')
      menuItem.textContent = item.text
      menuItem.style.cssText = `
        padding: 10px 16px;
        cursor: ${item.disabled ? 'default' : 'pointer'};
        color: ${item.disabled ? '#c0c4cc' : (item.selected ? '#409eff' : '#303133')};
        background: ${item.selected ? '#ecf5ff' : 'transparent'};
        font-weight: ${item.selected ? '600' : 'normal'};
        transition: all 0.15s ease;
        border-radius: 4px;
        margin: 2px 8px;
        position: relative;
        line-height: 1.4;
        ${item.style || ''}
      `

      // 为选中项添加小图标
      if (item.selected && !item.disabled) {
        const checkIcon = document.createElement('span')
        checkIcon.textContent = '✓'
        checkIcon.style.cssText = `
          position: absolute;
          right: 12px;
          top: 50%;
          transform: translateY(-50%);
          color: #409eff;
          font-weight: bold;
          font-size: 12px;
        `
        menuItem.appendChild(checkIcon)
        menuItem.style.paddingRight = '36px'
      }

      if (!item.disabled) {
        menuItem.addEventListener('mouseenter', () => {
          if (!item.selected) {
            menuItem.style.background = '#f0f9ff'
            menuItem.style.color = '#409eff'
            menuItem.style.transform = 'translateX(2px)'
          }
        })

        menuItem.addEventListener('mouseleave', () => {
          if (!item.selected) {
            menuItem.style.background = 'transparent'
            menuItem.style.color = '#303133'
            menuItem.style.transform = 'translateX(0)'
          }
        })

        menuItem.addEventListener('click', () => {
          if (item.onclick) {
            // 添加点击反馈
            menuItem.style.transform = 'scale(0.98)'
            setTimeout(() => {
              item.onclick()
            }, 50)
          }
          // 关闭菜单动画
          menu.style.opacity = '0'
          menu.style.transform = 'scale(0.95)'
          setTimeout(() => {
            if (menu.parentNode) {
              menu.remove()
            }
          }, 150)
        })
      }

      menu.appendChild(menuItem)
    }
  })

  // 添加到页面（先不显示）
  document.body.appendChild(menu)

  // 计算最佳位置
  const rect = menu.getBoundingClientRect()
  const viewportWidth = window.innerWidth
  const viewportHeight = window.innerHeight
  const scrollX = window.pageXOffset || document.documentElement.scrollLeft
  const scrollY = window.pageYOffset || document.documentElement.scrollTop

  // 计算菜单应该显示的位置
  let menuX = x
  let menuY = y

  // 水平位置调整
  if (x + rect.width > viewportWidth - 20) {
    // 如果右侧空间不够，显示在左侧
    menuX = x - rect.width - 5
    // 如果左侧也不够，则贴右边显示
    if (menuX < 20) {
      menuX = viewportWidth - rect.width - 20
    }
  }

  // 垂直位置调整
  if (y + rect.height > viewportHeight - 20) {
    // 如果下方空间不够，显示在上方
    menuY = y - rect.height - 5
    // 如果上方也不够，则贴底部显示
    if (menuY < 20) {
      menuY = viewportHeight - rect.height - 20
    }
  }

  // 确保菜单不会超出屏幕边界
  menuX = Math.max(10, Math.min(menuX, viewportWidth - rect.width - 10))
  menuY = Math.max(10, Math.min(menuY, viewportHeight - rect.height - 10))

  // 设置最终位置
  menu.style.left = menuX + 'px'
  menu.style.top = menuY + 'px'

  // 显示菜单动画
  requestAnimationFrame(() => {
    menu.style.opacity = '1'
    menu.style.transform = 'scale(1)'
    menu.style.pointerEvents = 'auto'
  })

  // 点击其他地方关闭菜单
  const closeMenu = (e) => {
    if (!menu.contains(e.target)) {
      // 关闭动画
      menu.style.opacity = '0'
      menu.style.transform = 'scale(0.95)'
      setTimeout(() => {
        if (menu.parentNode) {
          menu.remove()
        }
      }, 150)
      document.removeEventListener('click', closeMenu)
      document.removeEventListener('keydown', handleKeyDown)
    }
  }

  // 键盘事件处理
  const handleKeyDown = (e) => {
    if (e.key === 'Escape') {
      closeMenu(e)
    }
  }

  // 延迟添加事件监听器，避免立即触发
  setTimeout(() => {
    document.addEventListener('click', closeMenu)
    document.addEventListener('keydown', handleKeyDown)
  }, 100)
}

// 更新拼音注音
function updatePinyinAnnotation(rubyElement, newPinyin, char, editor) {
  try {
    // 更新ruby元素的内容和数据
    rubyElement.setAttribute('data-pinyin', newPinyin)
    const rtElement = rubyElement.querySelector('rt')
    if (rtElement) {
      rtElement.textContent = newPinyin
    }

    // 更新拼音选项（如果需要）
    const currentOptions = rubyElement.getAttribute('data-pinyin-options')
    if (currentOptions) {
      try {
        const options = JSON.parse(currentOptions.replace(/&quot;/g, '"'))
        if (!options.includes(newPinyin)) {
          options.unshift(newPinyin) // 将新拼音添加到选项列表开头
          const newOptionsStr = JSON.stringify(options).replace(/"/g, '&quot;')
          rubyElement.setAttribute('data-pinyin-options', newOptionsStr)
        }
      } catch (error) {
        // 忽略JSON解析错误
      }
    }

    ElMessage.success(`拼音已更新为：${newPinyin}`)
  } catch (error) {
    console.error('更新拼音注音失败:', error)
    ElMessage.error('更新拼音注音失败')
  }
}

// 清空内容
function clearAll() {
  content.value = ''
  if (editorInstance.value) {
    editorInstance.value.setContent('')
  }
  selectedText.value = ''
  emit('update:modelValue', '')
  ElMessage.success('内容已清空')
}
</script>

<style scoped>
.tinymce-editor {
  border: 1px solid #d9d9d9;
  border-radius: 6px;
  overflow: hidden;
}



.editor-footer {
  padding: 8px 12px;
  background: #fafafa;
  border-top: 1px solid #d9d9d9;
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 15px;
}

.word-count {
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
}

.save-status {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #666;
  flex-shrink: 0;
}

.save-status.saving {
  color: #409eff;
}

.save-status.saved {
  color: #67c23a;
}

.save-status.unsaved {
  color: #e6a23c;
}

.rotating {
  animation: rotate 1s linear infinite;
}

@keyframes rotate {
  from { transform: rotate(0deg); }
  to { transform: rotate(360deg); }
}

.shortcuts-btn {
  color: #909399 !important;
  font-size: 12px !important;
  padding: 4px 8px !important;
  height: auto !important;
  flex-shrink: 0;
}

.shortcuts-btn:hover {
  color: #409eff !important;
}

:deep(.tox-tinymce) {
  border: none !important;
}

:deep(.tox-editor-header) {
  border-bottom: 1px solid #d9d9d9 !important;
}

/* 修复工具栏 z-index 问题，确保在对话框中正常显示 */
:deep(.tox-toolbar) {
  z-index: 2100 !important;
}

:deep(.tox-toolbar__group) {
  z-index: 2100 !important;
}

:deep(.tox-tbtn) {
  z-index: 2100 !important;
}

:deep(.tox-split-button) {
  z-index: 2100 !important;
}

:deep(.tox-menubar) {
  z-index: 2100 !important;
}

/* 修复下拉菜单和弹出框的 z-index */
:deep(.tox-menu) {
  z-index: 2200 !important;
}

:deep(.tox-collection) {
  z-index: 2200 !important;
}

:deep(.tox-pop) {
  z-index: 2200 !important;
}

:deep(.tox-dialog-wrap) {
  z-index: 2300 !important;
}

:deep(.tox-dialog) {
  z-index: 2300 !important;
}

/* 修复 TinyMCE 的所有弹出层 */
:deep(.tox-silver-sink) {
  z-index: 2200 !important;
}

:deep(.tox-tinymce-aux) {
  z-index: 2200 !important;
}

:deep(.tox-floatpanel) {
  z-index: 2200 !important;
}

/* TinyMCE 编辑器内部滚动条样式 */
:deep(.tox-edit-area) {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.3) rgba(102, 126, 234, 0.05);
}

:deep(.tox-edit-area::-webkit-scrollbar) {
  width: 8px;
}

:deep(.tox-edit-area::-webkit-scrollbar-track) {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 4px;
}

:deep(.tox-edit-area::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 4px;
  transition: all 0.3s ease;
}

:deep(.tox-edit-area::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
}

/* TinyMCE 菜单和弹出框滚动条 */
:deep(.tox-menu) {
  scrollbar-width: thin;
  scrollbar-color: rgba(102, 126, 234, 0.3) rgba(102, 126, 234, 0.05);
}

:deep(.tox-menu::-webkit-scrollbar) {
  width: 6px;
}

:deep(.tox-menu::-webkit-scrollbar-track) {
  background: rgba(102, 126, 234, 0.05);
  border-radius: 3px;
}

:deep(.tox-menu::-webkit-scrollbar-thumb) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.3) 0%, rgba(118, 75, 162, 0.3) 100%);
  border-radius: 3px;
}

:deep(.tox-menu::-webkit-scrollbar-thumb:hover) {
  background: linear-gradient(135deg, rgba(102, 126, 234, 0.6) 0%, rgba(118, 75, 162, 0.6) 100%);
}

/* 预览对话框样式 */
.preview-dialog {
  .el-dialog {
    margin-top: 5vh !important;
    margin-bottom: 5vh !important;
    max-height: 90vh;
    display: flex;
    flex-direction: column;
  }

  .el-dialog__body {
    padding: 20px;
    flex: 1;
    overflow: hidden;
  }

  .el-dialog__header {
    padding: 20px 20px 10px 20px;
  }

  .el-dialog__footer {
    padding: 10px 20px 20px 20px;
  }
}

.preview-container {
  display: flex;
  flex-direction: column;
  gap: 20px;
  height: 80vh;
  max-height: 800px;
}

.device-selector {
  display: flex;
  flex-direction: column;
  gap: 15px;
  padding: 15px;
  background: #f8f9fa;
  border-radius: 8px;
  border: 1px solid #e9ecef;
}

.device-presets {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
}

.device-btn {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  padding: 12px 16px;
  min-width: 100px;
  height: auto;
  border-radius: 8px;
  transition: all 0.3s ease;
}

.device-btn:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

.device-icon {
  font-size: 20px;
}

.device-name {
  font-size: 12px;
  font-weight: 500;
}

.device-size {
  font-size: 10px;
  color: #666;
  opacity: 0.8;
}

.custom-size-controls {
  display: flex;
  gap: 20px;
  align-items: center;
  flex-wrap: wrap;
}

.size-input-group {
  display: flex;
  align-items: center;
  gap: 8px;
}

.size-input-group label {
  font-size: 14px;
  font-weight: 500;
  color: #333;
  min-width: 40px;
}

.size-input-group .unit {
  font-size: 12px;
  color: #666;
}

.preview-area {
  flex: 1;
  display: flex;
  justify-content: center;
  align-items: flex-start;
  background: #f0f2f5;
  border-radius: 8px;
  padding: 20px;
  overflow: auto;
  min-height: 400px;
}

.preview-frame-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 10px;
  width: 100%;
}

.preview-frame {
  background: white;
  border: 1px solid #ddd;
  border-radius: 8px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
  overflow-y: auto;
  overflow-x: hidden;
  position: relative;
  transition: all 0.3s ease;
  max-height: 600px;
}

.preview-frame:hover {
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.15);
}

.preview-content {
  padding: 20px;
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, Oxygen, Ubuntu, Cantarell, 'Open Sans', 'Helvetica Neue', sans-serif;
  line-height: 1.6;
  color: #333;
}

.preview-content h1, .preview-content h2, .preview-content h3 {
  margin-top: 0;
  margin-bottom: 16px;
}

.preview-content p {
  margin-bottom: 12px;
}

.preview-content img {
  max-width: 100%;
  height: auto;
  border-radius: 4px;
}

.frame-info {
  font-size: 12px;
  color: #666;
  background: #fff;
  padding: 4px 8px;
  border-radius: 4px;
  border: 1px solid #e9ecef;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .preview-container {
    height: 60vh;
  }

  .device-presets {
    justify-content: center;
  }

  .device-btn {
    min-width: 80px;
    padding: 8px 12px;
  }

  .custom-size-controls {
    justify-content: center;
  }

  .preview-area {
    padding: 10px;
  }
}

/* 内容统计对话框样式 */
.stats-container {
  padding: 10px 0;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
  margin-bottom: 25px;
}

.stat-item {
  text-align: center;
  padding: 15px;
  background: linear-gradient(135deg, #f8f9fa 0%, #e9ecef 100%);
  border-radius: 8px;
  border: 1px solid #dee2e6;
  transition: all 0.3s ease;
}

.stat-item:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
  background: linear-gradient(135deg, #e3f2fd 0%, #bbdefb 100%);
}

.stat-value {
  font-size: 24px;
  font-weight: bold;
  color: #409eff;
  margin-bottom: 5px;
}

.stat-label {
  font-size: 12px;
  color: #666;
  font-weight: 500;
}

.stats-tips {
  background: #f0f9ff;
  border: 1px solid #bfdbfe;
  border-radius: 8px;
  padding: 15px;
}

.stats-tips h4 {
  margin: 0 0 10px 0;
  color: #1e40af;
  font-size: 14px;
}

.stats-tips ul {
  margin: 0;
  padding-left: 20px;
}

.stats-tips li {
  font-size: 12px;
  color: #374151;
  margin-bottom: 5px;
  line-height: 1.4;
}

@media (max-width: 480px) {
  .stats-grid {
    grid-template-columns: 1fr;
    gap: 15px;
  }

  .stat-item {
    padding: 12px;
  }

  .stat-value {
    font-size: 20px;
  }
}

/* 符号对话框样式 */
.symbol-dialog .el-dialog__body {
  padding: 20px;
}

.symbol-container {
  max-height: 600px;
  overflow-y: auto;
}

.symbol-filters {
  margin-bottom: 20px;
}

.filter-row {
  display: flex;
  gap: 15px;
  align-items: center;
}

.search-input {
  flex: 1;
  max-width: 300px;
}

.category-select {
  width: 200px;
}

.category-option {
  display: flex;
  align-items: center;
  gap: 8px;
}

.category-icon {
  font-size: 16px;
}

.symbol-groups {
  display: flex;
  flex-direction: column;
  gap: 25px;
}

.symbol-group {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  overflow: hidden;
}

.group-header {
  background: linear-gradient(135deg, #f8fafc 0%, #e2e8f0 100%);
  padding: 12px 16px;
  border-bottom: 1px solid #e4e7ed;
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 600;
  color: #374151;
}

.group-icon {
  font-size: 18px;
}

.group-title {
  flex: 1;
}

.group-count {
  font-size: 12px;
  color: #6b7280;
  background: #f3f4f6;
  padding: 2px 8px;
  border-radius: 12px;
}

.symbol-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
  gap: 1px;
  background: #f3f4f6;
  padding: 1px;
}

.symbol-item {
  background: white;
  padding: 12px 8px;
  text-align: center;
  cursor: pointer;
  transition: all 0.2s ease;
  border-radius: 4px;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 4px;
  min-height: 70px;
  justify-content: center;
}

.symbol-item:hover {
  background: #ecf5ff;
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
}

.symbol-char {
  font-size: 24px;
  font-weight: 500;
  color: #1f2937;
  line-height: 1;
}

.symbol-name {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.2;
  text-align: center;
  word-break: break-all;
}

/* 模板对话框样式 */
.template-dialog .el-dialog__body {
  padding: 20px;
}

.template-container {
  max-height: 600px;
  overflow-y: auto;
}

.template-filters {
  margin-bottom: 20px;
}

.template-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(300px, 1fr));
  gap: 16px;
}

.template-card {
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  padding: 16px;
  cursor: pointer;
  transition: all 0.2s ease;
  background: white;
}

.template-card:hover {
  border-color: #409eff;
  box-shadow: 0 4px 12px rgba(64, 158, 255, 0.15);
  transform: translateY(-2px);
}

.template-header {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  margin-bottom: 12px;
}

.template-icon {
  font-size: 24px;
  flex-shrink: 0;
  width: 40px;
  height: 40px;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #f8fafc;
  border-radius: 8px;
}

.template-info {
  flex: 1;
  min-width: 0;
}

.template-name {
  font-size: 16px;
  font-weight: 600;
  color: #1f2937;
  margin: 0 0 4px 0;
  line-height: 1.3;
}

.template-description {
  font-size: 13px;
  color: #6b7280;
  margin: 0;
  line-height: 1.4;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.template-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  margin-bottom: 12px;
  flex-wrap: wrap;
}

.usage-count {
  font-size: 12px;
  color: #9ca3af;
  margin-left: auto;
}

.template-preview {
  font-size: 12px;
  color: #6b7280;
  line-height: 1.4;
  background: #f8fafc;
  padding: 8px;
  border-radius: 4px;
  border-left: 3px solid #e5e7eb;
  max-height: 60px;
  overflow: hidden;
  position: relative;
}

.template-preview::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 0;
  right: 0;
  height: 20px;
  background: linear-gradient(transparent, #f8fafc);
}

/* 响应式调整 */
@media (max-width: 768px) {
  .filter-row {
    flex-direction: column;
    align-items: stretch;
  }

  .search-input,
  .category-select {
    max-width: none;
    width: 100%;
  }

  .symbol-grid {
    grid-template-columns: repeat(auto-fill, minmax(80px, 1fr));
  }

  .symbol-item {
    min-height: 60px;
    padding: 8px 4px;
  }

  .symbol-char {
    font-size: 20px;
  }

  .template-grid {
    grid-template-columns: 1fr;
  }
}
</style>
