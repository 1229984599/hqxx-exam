<template>
  <PageLayout
    title="TinyMCE 编辑器测试"
    subtitle="测试 TinyMCE 富文本编辑器功能"
  >
    <div class="test-container">
      <el-card>
        <template #header>
          <div class="card-header">
            <span>TinyMCE 编辑器</span>
            <el-button type="primary" @click="showContent">查看内容</el-button>
          </div>
        </template>
        
        <TinyMCEEditor
          v-model="content"
          placeholder="请输入内容进行测试..."
          :height="500"
          :show-pinyin-tools="true"
          :show-word-count="true"
        />
        
        <div class="content-preview" v-if="showPreview">
          <h3>编辑器内容预览：</h3>
          <div class="preview-box" v-html="content"></div>
          
          <h3>原始 HTML：</h3>
          <pre class="html-code">{{ content }}</pre>
        </div>
      </el-card>
      
      <el-card style="margin-top: 20px;">
        <template #header>
          <span>测试功能</span>
        </template>
        
        <el-space wrap>
          <el-button @click="insertSampleText">插入示例文本</el-button>
          <el-button @click="clearContent">清空内容</el-button>
          <el-button @click="togglePreview">{{ showPreview ? '隐藏' : '显示' }}预览</el-button>
        </el-space>
        
        <div style="margin-top: 20px;">
          <h4>测试拼音注音功能（使用标准 Ruby 标签）：</h4>
          <p>1. 在编辑器中输入一些中文文字</p>
          <p>2. 选中文字后点击工具栏中的"添加拼音"按钮</p>
          <p>3. 查看是否正确显示拼音（每个字符一一对应）</p>
          <p>4. 选中已注音的文字，点击"移除拼音"按钮可以移除注音</p>
          <p><strong>注意：</strong>现在使用标准的 HTML Ruby 标签，显示效果更加专业</p>

          <h4 style="margin-top: 20px;">测试图片粘贴上传功能：</h4>
          <p>1. 复制任意图片（截图、从网页复制等）</p>
          <p>2. 在编辑器中按 Ctrl+V 粘贴</p>
          <p>3. 图片会自动上传到CDN并插入到编辑器中</p>
          <p><strong>注意：</strong>需要配置有效的图床token才能正常上传</p>

          <h4 style="margin-top: 20px;">测试字体大小调整功能：</h4>
          <p>1. 选中一些文字</p>
          <p>2. 点击工具栏中的"A+"按钮增大字体</p>
          <p>3. 点击工具栏中的"A-"按钮减小字体</p>
          <p>4. <strong>🎉 新功能：</strong>可以连续点击A+/A-按钮，无需重新选择文字！</p>
          <p>5. 字体大小选择器现在支持更大的字体：8px-120px</p>
          <p><strong>💡 使用技巧：</strong>选中文字后，可以连续点击A+或A-来快速调整到理想的字体大小</p>

          <h4 style="margin-top: 20px;">测试表情功能：</h4>
          <p>1. 点击工具栏中的表情按钮（😀）</p>
          <p>2. 选择各种表情符号插入到编辑器中</p>
          <p>3. 支持搜索表情关键词</p>
          <p>4. 包含丰富的表情、符号、学习相关图标等</p>

          <h4 style="margin-top: 20px;">测试响应式预览功能：</h4>
          <p>1. 点击工具栏<strong>最前面</strong>的"预览"按钮（已移到最前面）</p>
          <p>2. 选择不同的设备预设（iPhone、iPad、Desktop等）</p>
          <p>3. 实时调整预览窗口的宽度和高度</p>
          <p>4. 查看内容在不同屏幕尺寸下的显示效果</p>
          <p>5. 支持自定义尺寸设置</p>

          <h4 style="margin-top: 20px;">最新优化说明：</h4>
          <p><strong>✅ 预览按钮美化：</strong>添加了👁️图标，位于工具栏最前面</p>
          <p><strong>✅ 字体大小调整：</strong>完全修复了A+/A-按钮，支持连续点击调整</p>
          <p><strong>✅ 表情功能：</strong>修复了表情加载问题，现在使用内置表情库</p>
          <p><strong>🚀 字体调整效率提升：</strong></p>
          <ul style="margin-left: 20px;">
            <li>选中文字后，可以连续点击A+/A-按钮</li>
            <li>无需每次调整后重新选择文字</li>
            <li>自动保持选区状态，大幅提升操作效率</li>
            <li>支持快速调整到理想的字体大小</li>
          </ul>
          <p><strong>✅ 响应式预览优化：</strong></p>
          <ul style="margin-left: 20px;">
            <li>预览对话框位置优化，避免被屏幕底部遮挡</li>
            <li>切换设备尺寸时自动滚动到内容顶部</li>
            <li>预览区域支持垂直滚动，可查看完整内容</li>
            <li>大尺寸设备预览时内容始终从顶部开始显示</li>
          </ul>
        </div>
      </el-card>
    </div>
  </PageLayout>
</template>

<script setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import TinyMCEEditor from '../components/TinyMCEEditor.vue'
import PageLayout from '../components/PageLayout.vue'

const content = ref('')
const showPreview = ref(false)

function showContent() {
  ElMessage.info(`当前内容长度: ${content.value.length} 字符`)
  console.log('编辑器内容:', content.value)
}

function insertSampleText() {
  content.value = `
    <h2>欢迎使用 TinyMCE 编辑器</h2>
    <p>这是一个<strong>富文本编辑器</strong>测试页面。</p>
    <p>支持以下功能：</p>
    <ul>
      <li>文字格式化（<strong>粗体</strong>、<em>斜体</em>、<u>下划线</u>）</li>
      <li>列表和缩进</li>
      <li>拼音注音功能（集成在工具栏中）</li>
      <li>插入模板</li>
    </ul>
    <p>测试拼音注音：请选择"发布"这两个字，然后点击工具栏中的"添加拼音"按钮。</p>
    <p>发布</p>
    <p>测试编辑稳定性：对"发布"添加拼音后，尝试在中间插入空格，拼音应该保持正确对应。</p>
    <p>更多测试文字：北京大学、清华大学、中国科学院</p>
  `
  ElMessage.success('示例文本已插入')
}

function clearContent() {
  content.value = ''
  ElMessage.success('内容已清空')
}

function togglePreview() {
  showPreview.value = !showPreview.value
}
</script>

<style scoped>
.test-container {
  max-width: 1200px;
  margin: 0 auto;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.content-preview {
  margin-top: 20px;
  padding-top: 20px;
  border-top: 1px solid #eee;
}

.preview-box {
  border: 1px solid #ddd;
  padding: 15px;
  border-radius: 4px;
  background: #f9f9f9;
  margin: 10px 0;
  min-height: 100px;
}

.html-code {
  background: #f5f5f5;
  padding: 15px;
  border-radius: 4px;
  border: 1px solid #ddd;
  font-family: 'Courier New', monospace;
  font-size: 12px;
  white-space: pre-wrap;
  word-break: break-all;
  max-height: 200px;
  overflow-y: auto;
}
</style>
