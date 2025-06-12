<template>
  <div class="analytics-chart">
    <div class="chart-header">
      <h3>{{ title }}</h3>
      <div class="chart-controls" v-if="showControls">
        <el-select v-model="chartType" @change="updateChart" size="small">
          <el-option label="柱状图" value="bar" />
          <el-option label="饼图" value="pie" />
          <el-option label="折线图" value="line" />
        </el-select>
      </div>
    </div>
    <div class="chart-container" :style="{ height: height }">
      <v-chart 
        :option="chartOption" 
        :loading="loading"
        :autoresize="true"
        @click="handleChartClick"
      />
    </div>
  </div>
</template>

<script setup>
import { ref, computed, watch, onMounted } from 'vue'
import { use } from 'echarts/core'
import { CanvasRenderer } from 'echarts/renderers'
import { BarChart, PieChart, LineChart } from 'echarts/charts'
import {
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
} from 'echarts/components'
import VChart from 'vue-echarts'

// 注册必要的组件
use([
  CanvasRenderer,
  BarChart,
  PieChart,
  LineChart,
  TitleComponent,
  TooltipComponent,
  LegendComponent,
  GridComponent
])

const props = defineProps({
  title: {
    type: String,
    required: true
  },
  data: {
    type: Array,
    default: () => []
  },
  type: {
    type: String,
    default: 'bar',
    validator: (value) => ['bar', 'pie', 'line'].includes(value)
  },
  height: {
    type: String,
    default: '300px'
  },
  loading: {
    type: Boolean,
    default: false
  },
  showControls: {
    type: Boolean,
    default: true
  },
  xAxisKey: {
    type: String,
    default: 'name'
  },
  yAxisKey: {
    type: String,
    default: 'value'
  },
  colors: {
    type: Array,
    default: () => [
      '#667eea', '#764ba2', '#f093fb', '#f5576c',
      '#4facfe', '#00f2fe', '#43e97b', '#38f9d7',
      '#ffecd2', '#fcb69f', '#a8edea', '#fed6e3'
    ]
  }
})

const emit = defineEmits(['chart-click'])

const chartType = ref(props.type)

// 计算图表配置
const chartOption = computed(() => {
  if (!props.data || props.data.length === 0) {
    return {
      title: {
        text: '暂无数据',
        left: 'center',
        top: 'center',
        textStyle: {
          color: '#999',
          fontSize: 14
        }
      }
    }
  }

  const baseOption = {
    tooltip: {
      trigger: chartType.value === 'pie' ? 'item' : 'axis',
      backgroundColor: 'rgba(255, 255, 255, 0.95)',
      borderColor: '#e4e7ed',
      borderWidth: 1,
      textStyle: {
        color: '#606266'
      }
    },
    color: props.colors
  }

  switch (chartType.value) {
    case 'bar':
      return {
        ...baseOption,
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: props.data.map(item => item[props.xAxisKey]),
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          axisLabel: {
            color: '#606266'
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          axisLabel: {
            color: '#606266'
          },
          splitLine: {
            lineStyle: {
              color: '#f5f7fa'
            }
          }
        },
        series: [{
          type: 'bar',
          data: props.data.map(item => item[props.yAxisKey]),
          itemStyle: {
            borderRadius: [4, 4, 0, 0]
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }]
      }

    case 'pie':
      return {
        ...baseOption,
        legend: {
          orient: 'vertical',
          left: 'left',
          textStyle: {
            color: '#606266'
          }
        },
        series: [{
          type: 'pie',
          radius: ['40%', '70%'],
          center: ['60%', '50%'],
          data: props.data.map(item => ({
            name: item[props.xAxisKey],
            value: item[props.yAxisKey]
          })),
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowOffsetX: 0,
              shadowColor: 'rgba(0, 0, 0, 0.5)'
            }
          },
          label: {
            formatter: '{b}: {c} ({d}%)'
          }
        }]
      }

    case 'line':
      return {
        ...baseOption,
        grid: {
          left: '3%',
          right: '4%',
          bottom: '3%',
          containLabel: true
        },
        xAxis: {
          type: 'category',
          data: props.data.map(item => item[props.xAxisKey]),
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          axisLabel: {
            color: '#606266'
          }
        },
        yAxis: {
          type: 'value',
          axisLine: {
            lineStyle: {
              color: '#e4e7ed'
            }
          },
          axisLabel: {
            color: '#606266'
          },
          splitLine: {
            lineStyle: {
              color: '#f5f7fa'
            }
          }
        },
        series: [{
          type: 'line',
          data: props.data.map(item => item[props.yAxisKey]),
          smooth: true,
          lineStyle: {
            width: 3
          },
          itemStyle: {
            borderWidth: 2
          },
          emphasis: {
            itemStyle: {
              shadowBlur: 10,
              shadowColor: 'rgba(0, 0, 0, 0.3)'
            }
          }
        }]
      }

    default:
      return baseOption
  }
})

// 监听数据变化
watch(() => props.data, () => {
  updateChart()
}, { deep: true })

// 更新图表
function updateChart() {
  // 图表会自动重新渲染
}

// 处理图表点击事件
function handleChartClick(params) {
  emit('chart-click', params)
}

onMounted(() => {
  updateChart()
})
</script>

<style scoped>
.analytics-chart {
  background: rgba(255, 255, 255, 0.9);
  backdrop-filter: blur(10px);
  border-radius: 16px;
  padding: 24px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  border: 1px solid rgba(255, 255, 255, 0.2);
  transition: all 0.3s ease;
}

.analytics-chart:hover {
  transform: translateY(-2px);
  box-shadow: 0 12px 40px rgba(0, 0, 0, 0.15);
}

.chart-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.chart-header h3 {
  margin: 0;
  font-size: 18px;
  font-weight: 600;
  color: #2d3748;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  -webkit-background-clip: text;
  -webkit-text-fill-color: transparent;
  background-clip: text;
}

.chart-controls {
  display: flex;
  gap: 12px;
  align-items: center;
}

.chart-container {
  width: 100%;
  min-height: 200px;
}

/* 深色模式支持 */
.dark .analytics-chart {
  background: rgba(45, 55, 72, 0.9);
  border-color: rgba(255, 255, 255, 0.1);
}

.dark .chart-header h3 {
  color: #e2e8f0;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .analytics-chart {
    padding: 16px;
  }
  
  .chart-header {
    flex-direction: column;
    gap: 12px;
    align-items: flex-start;
  }
  
  .chart-header h3 {
    font-size: 16px;
  }
}
</style>
