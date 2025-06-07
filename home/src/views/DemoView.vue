<template>
  <div class="demo-view">
    <div class="container">
      <div class="demo-header">
        <h1>红旗小学无纸化测试 - 题目演示</h1>
        <p>以下是系统中不同类型题目的展示效果</p>
      </div>
      
      <!-- 语文拼音题目演示 -->
      <div class="demo-section">
        <h2>语文 - 拼音练习</h2>
        <div class="question-card demo-card">
          <div class="question-header">
            <h3 class="question-title">拼音练习：声母b</h3>
            <div class="question-meta">
              <el-tag size="small" type="info">难度: 简单</el-tag>
              <el-tag size="small" type="success">类型: 拼音练习</el-tag>
            </div>
          </div>
          
          <div class="question-content">
            <p>请读出下面的拼音：</p>
            <h2 style="text-align: center; color: #409eff; margin: 20px 0;">
              ba &nbsp;&nbsp; bi &nbsp;&nbsp; bu &nbsp;&nbsp; bo
            </h2>
          </div>
          
          <div class="answer-section" v-if="showAnswers.pinyin">
            <h4 class="answer-title">
              <el-icon><Check /></el-icon>
              参考答案
            </h4>
            <div class="answer-content">
              ba读作巴，bi读作比，bu读作不，bo读作波
            </div>
          </div>
          
          <div class="demo-buttons">
            <el-button 
              v-if="!showAnswers.pinyin"
              type="success" 
              @click="showAnswers.pinyin = true"
              :icon="View"
            >
              查看答案
            </el-button>
            <el-button 
              v-else
              type="warning" 
              @click="showAnswers.pinyin = false"
              :icon="Hide"
            >
              隐藏答案
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 数学加法题目演示 -->
      <div class="demo-section">
        <h2>数学 - 加法练习</h2>
        <div class="question-card demo-card">
          <div class="question-header">
            <h3 class="question-title">10以内加法：5+3</h3>
            <div class="question-meta">
              <el-tag size="small" type="info">难度: 简单</el-tag>
              <el-tag size="small" type="success">类型: 加减法</el-tag>
            </div>
          </div>
          
          <div class="question-content">
            <p>计算下面的加法题：</p>
            <h1 style="text-align: center; color: #e6a23c; margin: 30px 0; font-size: 48px;">
              5 + 3 = ?
            </h1>
          </div>
          
          <div class="answer-section" v-if="showAnswers.math">
            <h4 class="answer-title">
              <el-icon><Check /></el-icon>
              参考答案
            </h4>
            <div class="answer-content">
              <strong style="font-size: 24px; color: #67c23a;">8</strong>
            </div>
            
            <div class="explanation-section">
              <h4 class="explanation-title">
                <el-icon><InfoFilled /></el-icon>
                解析
              </h4>
              <div class="explanation-content">
                5个苹果加上3个苹果，一共是8个苹果
              </div>
            </div>
          </div>
          
          <div class="demo-buttons">
            <el-button 
              v-if="!showAnswers.math"
              type="success" 
              @click="showAnswers.math = true"
              :icon="View"
            >
              查看答案
            </el-button>
            <el-button 
              v-else
              type="warning" 
              @click="showAnswers.math = false"
              :icon="Hide"
            >
              隐藏答案
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 语文识字题目演示 -->
      <div class="demo-section">
        <h2>语文 - 识字练习</h2>
        <div class="question-card demo-card">
          <div class="question-header">
            <h3 class="question-title">认识汉字</h3>
            <div class="question-meta">
              <el-tag size="small" type="info">难度: 较易</el-tag>
              <el-tag size="small" type="success">类型: 识字</el-tag>
            </div>
          </div>
          
          <div class="question-content">
            <p>请读出下面的汉字：</p>
            <div style="text-align: center; margin: 30px 0;">
              <span style="font-size: 60px; color: #f56c6c; margin: 0 20px;">太</span>
              <span style="font-size: 60px; color: #409eff; margin: 0 20px;">阳</span>
            </div>
          </div>
          
          <div class="answer-section" v-if="showAnswers.word">
            <h4 class="answer-title">
              <el-icon><Check /></el-icon>
              参考答案
            </h4>
            <div class="answer-content">
              太阳 (tài yáng)
            </div>
            
            <div class="explanation-section">
              <h4 class="explanation-title">
                <el-icon><InfoFilled /></el-icon>
                解析
              </h4>
              <div class="explanation-content">
                太阳是我们每天都能看到的，它给我们带来光明和温暖。
              </div>
            </div>
          </div>
          
          <div class="demo-buttons">
            <el-button 
              v-if="!showAnswers.word"
              type="success" 
              @click="showAnswers.word = true"
              :icon="View"
            >
              查看答案
            </el-button>
            <el-button 
              v-else
              type="warning" 
              @click="showAnswers.word = false"
              :icon="Hide"
            >
              隐藏答案
            </el-button>
          </div>
        </div>
      </div>
      
      <!-- 使用说明 -->
      <div class="demo-section">
        <h2>使用说明</h2>
        <div class="usage-card">
          <div class="usage-content">
            <h3>📱 无纸化测试流程</h3>
            <ol>
              <li><strong>老师操作</strong>：用手机打开系统，选择学期、年级、学科、分类</li>
              <li><strong>展示题目</strong>：点击"开始答题"，将手机屏幕展示给学生</li>
              <li><strong>学生答题</strong>：学生看题后口头回答</li>
              <li><strong>查看答案</strong>：老师点击"查看答案"进行讲解</li>
              <li><strong>继续练习</strong>：点击"下一题"获取新题目</li>
            </ol>
            
            <h3>🎯 系统特点</h3>
            <ul>
              <li>✅ <strong>手机优化</strong>：专为手机屏幕设计，字体大、按钮大</li>
              <li>✅ <strong>随机出题</strong>：避免重复，保持新鲜感</li>
              <li>✅ <strong>即时反馈</strong>：答案和解析随时查看</li>
              <li>✅ <strong>分类管理</strong>：按知识点精准练习</li>
              <li>✅ <strong>环保节能</strong>：无需打印，绿色教学</li>
            </ul>
          </div>
        </div>
      </div>
      
      <div class="demo-footer">
        <el-button type="primary" size="large" @click="$router.push('/')">
          返回首页开始测试
        </el-button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { reactive } from 'vue'
import { Check, InfoFilled, View, Hide } from '@element-plus/icons-vue'

const showAnswers = reactive({
  pinyin: false,
  math: false,
  word: false
})
</script>

<style scoped>
.demo-view {
  min-height: calc(100vh - 80px);
  padding: 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
}

.container {
  max-width: 800px;
  margin: 0 auto;
}

.demo-header {
  text-align: center;
  margin-bottom: 40px;
  color: white;
}

.demo-header h1 {
  font-size: 28px;
  margin-bottom: 10px;
  text-shadow: 0 2px 4px rgba(0, 0, 0, 0.3);
}

.demo-header p {
  font-size: 16px;
  opacity: 0.9;
}

.demo-section {
  margin-bottom: 40px;
}

.demo-section h2 {
  color: white;
  font-size: 22px;
  margin-bottom: 20px;
  text-shadow: 0 1px 2px rgba(0, 0, 0, 0.3);
}

.question-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.question-header {
  margin-bottom: 25px;
}

.question-title {
  font-size: 20px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
}

.question-meta {
  display: flex;
  gap: 10px;
  flex-wrap: wrap;
}

.question-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  margin-bottom: 25px;
  padding: 20px;
  background: #f8f9fa;
  border-radius: 12px;
  border-left: 4px solid #409eff;
}

.answer-section {
  margin-top: 30px;
  padding-top: 25px;
  border-top: 2px solid #e1e8ed;
}

.answer-title,
.explanation-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  margin-bottom: 15px;
}

.answer-content,
.explanation-content {
  font-size: 16px;
  line-height: 1.8;
  color: #2c3e50;
  padding: 20px;
  background: #f0f9ff;
  border-radius: 12px;
  border-left: 4px solid #67c23a;
}

.explanation-section {
  margin-top: 20px;
}

.explanation-content {
  background: #fff7e6;
  border-left-color: #e6a23c;
}

.demo-buttons {
  display: flex;
  justify-content: center;
  margin-top: 25px;
}

.usage-card {
  background: rgba(255, 255, 255, 0.95);
  border-radius: 16px;
  padding: 30px;
  box-shadow: 0 8px 32px rgba(0, 0, 0, 0.1);
  backdrop-filter: blur(10px);
}

.usage-content h3 {
  color: #2c3e50;
  margin-bottom: 15px;
  font-size: 18px;
}

.usage-content ol,
.usage-content ul {
  color: #2c3e50;
  line-height: 1.8;
  margin-bottom: 25px;
}

.usage-content li {
  margin-bottom: 8px;
}

.demo-footer {
  text-align: center;
  margin-top: 40px;
}

@media (max-width: 768px) {
  .demo-view {
    padding: 15px 10px;
  }
  
  .question-card {
    padding: 20px 15px;
  }
  
  .question-title {
    font-size: 18px;
  }
  
  .question-content {
    font-size: 15px;
    padding: 15px;
  }
  
  .demo-header h1 {
    font-size: 24px;
  }
  
  .demo-section h2 {
    font-size: 20px;
  }
}
</style>
