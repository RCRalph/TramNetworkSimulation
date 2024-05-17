// Components
import App from './App.vue'

// Plugins
import vuetify from './plugins/vuetify'
import './plugins/leaflet'

// Composables
import { createApp } from 'vue'

const app = createApp(App)

app.use(vuetify).mount('#app')
