<template>
  <div class="stat-card" :class="{ loading: loading }">
    <div class="stat-icon" :style="{ background: iconBg }">
      <el-icon :size="24" :color="iconColor">
        <component :is="icon" />
      </el-icon>
    </div>
    <div class="stat-content">
      <div class="stat-value" v-if="!loading">{{ value }}</div>
      <div class="stat-value loading-placeholder" v-else></div>
      <div class="stat-label">{{ label }}</div>
      <div class="stat-change" v-if="change !== undefined" :class="changeClass">
        <el-icon :size="12">
          <ArrowUp v-if="change > 0" />
          <ArrowDown v-if="change < 0" />
          <Minus v-if="change === 0" />
        </el-icon>
        <span>{{ Math.abs(change) }}%</span>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'
import { ArrowUp, ArrowDown, Minus } from '@element-plus/icons-vue'

const props = defineProps({
  icon: {
    type: [String, Object],
    required: true
  },
  iconColor: {
    type: String,
    default: '#ffffff'
  },
  iconBg: {
    type: String,
    default: 'linear-gradient(135deg, #667eea 0%, #764ba2 100%)'
  },
  value: {
    type: [String, Number],
    required: true
  },
  label: {
    type: String,
    required: true
  },
  change: {
    type: Number,
    default: undefined
  },
  loading: {
    type: Boolean,
    default: false
  }
})

const changeClass = computed(() => {
  if (props.change > 0) return 'positive'
  if (props.change < 0) return 'negative'
  return 'neutral'
})
</script>

<style scoped>
.stat-card {
  background: white;
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.2);
  display: flex;
  align-items: center;
  gap: 20px;
  transition: all 0.3s ease;
  position: relative;
  overflow: hidden;
}

.stat-card::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  height: 4px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.12);
}

.stat-card.loading {
  opacity: 0.7;
}

.stat-icon {
  width: 60px;
  height: 60px;
  border-radius: 16px;
  display: flex;
  align-items: center;
  justify-content: center;
  flex-shrink: 0;
}

.stat-content {
  flex: 1;
}

.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #2d3748;
  line-height: 1;
  margin-bottom: 8px;
}

.loading-placeholder {
  height: 32px;
  background: linear-gradient(90deg, #f0f0f0 25%, #e0e0e0 50%, #f0f0f0 75%);
  background-size: 200% 100%;
  animation: loading 1.5s infinite;
  border-radius: 4px;
}

@keyframes loading {
  0% { background-position: 200% 0; }
  100% { background-position: -200% 0; }
}

.stat-label {
  font-size: 14px;
  color: #718096;
  font-weight: 500;
  margin-bottom: 8px;
}

.stat-change {
  display: flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  font-weight: 600;
}

.stat-change.positive {
  color: #48bb78;
}

.stat-change.negative {
  color: #f56565;
}

.stat-change.neutral {
  color: #a0aec0;
}
</style>
