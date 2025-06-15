<template>
  <div id="app" class="min-h-screen bg-gradient-to-br from-gray-50 to-blue-50">
    <!-- Header组件 -->
    <Header />

    <!-- 主要内容区域 -->
    <main class="container mx-auto px-4 py-6">
      <router-view />
    </main>



    <!-- 配置对话框 -->
    <ConfigDialog />
  </div>
</template>

<script setup>
import { onMounted } from 'vue'
import Header from './components/Header.vue'
import ConfigDialog from './components/ConfigDialog.vue'
import { useConfigStore } from './stores/config'

const configStore = useConfigStore()

onMounted(async () => {
  // 初始化时加载基础数据
  await configStore.loadAllData()
})
</script>

<style scoped>
#app {
  font-family: 'Microsoft YaHei', 'PingFang SC', 'Hiragino Sans GB', sans-serif;
}
</style>
