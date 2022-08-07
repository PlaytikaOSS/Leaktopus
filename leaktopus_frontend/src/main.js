import { createApp } from 'vue'
import App from './App.vue'
import router from './router'
import Config from './config.json'
import 'bootstrap/dist/css/bootstrap.min.css'
import 'bootstrap'
import './assets/css/reset.css'

/* import the fontawesome core */
import { library } from '@fortawesome/fontawesome-svg-core'
/* import font awesome icon component */
import { FontAwesomeIcon } from '@fortawesome/vue-fontawesome'
/* import specific icons */
import { faArrowsRotate } from '@fortawesome/free-solid-svg-icons'
/* add icons to the library */
library.add(faArrowsRotate)

const app = createApp(App)
app.component('font-awesome-icon', FontAwesomeIcon)

// Get the API URL from our configuration file.
let api_url
if (Config.LEAKTOPUS_API_URL === "$LEAKTOPUS_API_URL") {
    api_url = Config.LEAKTOPUS_API_URL
}
else {
    api_url = "http://localhost:8000/"
}
app.config.globalProperties.leaktopusApiUrl = api_url

app.use(router).mount('#app')

