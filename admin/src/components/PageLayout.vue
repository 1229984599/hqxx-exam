<template>
  <div class="page-layout">
    <div class="page-content">
      <slot></slot>
    </div>
  </div>
</template>

<script setup>
defineProps({
  title: {
    type: String,
    required: true
  },
  subtitle: {
    type: String,
    default: ''
  }
})
</script>

<style scoped>
.page-layout {
  height: 100vh;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 24px;
  display: flex;
  flex-direction: column;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-bottom: 32px;
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
}

.header-left {
  flex: 1;
}

.page-title {
  font-size: 32px;
  font-weight: 700;
  color: #1a202c;
  margin: 0 0 8px 0;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.page-subtitle {
  font-size: 16px;
  color: #718096;
  margin: 0;
  font-weight: 400;
}

.header-right {
  display: flex;
  gap: 12px;
  align-items: center;
}

.page-content {
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 32px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  flex: 1;
  overflow: auto;
}

/* 全局按钮样式优化 */
:deep(.el-button) {
  border-radius: 12px;
  font-weight: 500;
  transition: all 0.3s ease;
  border: none;
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
}

:deep(.el-button--primary) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
}

:deep(.el-button--primary:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(102, 126, 234, 0.4);
}

:deep(.el-button--success) {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
}

:deep(.el-button--success:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(72, 187, 120, 0.4);
}

:deep(.el-button--warning) {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
}

:deep(.el-button--warning:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(237, 137, 54, 0.4);
}

:deep(.el-button--danger) {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
}

:deep(.el-button--danger:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(245, 101, 101, 0.4);
}

:deep(.el-button--info) {
  background: linear-gradient(135deg, #a0aec0 0%, #718096 100%);
}

:deep(.el-button--info:hover) {
  transform: translateY(-2px);
  box-shadow: 0 8px 24px rgba(160, 174, 192, 0.4);
}

/* 表格样式优化 */
:deep(.el-table) {
  border-radius: 12px;
  overflow: hidden;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: none;
}

:deep(.el-table__header) {
  background: linear-gradient(135deg, #f7fafc 0%, #edf2f7 100%);
}

:deep(.el-table th) {
  background: transparent;
  border: none;
  color: #4a5568;
  font-weight: 600;
  font-size: 14px;
  padding: 16px 12px;
}

:deep(.el-table td) {
  border: none;
  padding: 16px 12px;
  color: #2d3748;
}

:deep(.el-table__row:hover) {
  background: rgba(102, 126, 234, 0.05);
}

:deep(.el-table__row:nth-child(even)) {
  background: rgba(247, 250, 252, 0.5);
}

/* 卡片样式优化 */
:deep(.el-card) {
  border-radius: 16px;
  border: none;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  background: rgba(255, 255, 255, 0.95);
  backdrop-filter: blur(10px);
}

:deep(.el-card__body) {
  padding: 24px;
}

/* 标签样式优化 */
:deep(.el-tag) {
  border-radius: 8px;
  border: none;
  font-weight: 500;
  padding: 4px 12px;
}

:deep(.el-tag--success) {
  background: linear-gradient(135deg, #48bb78 0%, #38a169 100%);
  color: white;
}

:deep(.el-tag--danger) {
  background: linear-gradient(135deg, #f56565 0%, #e53e3e 100%);
  color: white;
}

:deep(.el-tag--warning) {
  background: linear-gradient(135deg, #ed8936 0%, #dd6b20 100%);
  color: white;
}

/* 输入框样式优化 */
:deep(.el-input__wrapper) {
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  border: 1px solid #e2e8f0;
  transition: all 0.3s ease;
}

:deep(.el-input__wrapper:hover) {
  border-color: #667eea;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.2);
}

:deep(.el-input__wrapper.is-focus) {
  border-color: #667eea;
  box-shadow: 0 0 0 3px rgba(102, 126, 234, 0.1);
}

/* 选择器样式优化 */
:deep(.el-select .el-input__wrapper) {
  border-radius: 12px;
}

/* 对话框样式优化 */
:deep(.el-dialog) {
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.2);
  backdrop-filter: blur(10px);
}

:deep(.el-dialog__header) {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 16px 16px 0 0;
  padding: 20px 24px;
}

:deep(.el-dialog__title) {
  color: white;
  font-weight: 600;
  font-size: 18px;
}

:deep(.el-dialog__body) {
  padding: 24px;
}

:deep(.el-dialog__footer) {
  padding: 16px 24px 24px;
  text-align: right;
}
</style>
