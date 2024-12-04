import { createApp, reactive } from 'vue'
import App from './App.vue'

// 建立vue app
const app = createApp(App);
app.mount('#app');

// 状态管理
const state = reactive({
    state: 0,
});
app.provide(state);

// api