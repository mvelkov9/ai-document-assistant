import { createApp } from 'vue'
import '@fontsource/inter/400.css'
import '@fontsource/inter/500.css'
import '@fontsource/inter/600.css'
import '@fontsource/inter/700.css'
import '@fontsource/space-grotesk/400.css'
import '@fontsource/space-grotesk/500.css'
import '@fontsource/space-grotesk/700.css'
import App from './App.vue'
import { i18n } from './lib/i18n'
import router from './router'
import './assets/main.css'

createApp(App).use(i18n).use(router).mount('#app')
