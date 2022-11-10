// Default CSS
import "./assets/css/default.css";
import "./assets/css/reset.css";

// JS
import { createPinia } from "pinia";
import { createApp } from "vue";

import App from "./App.vue";
import router from "./router";

const app = createApp(App);

app.use(createPinia());
app.use(router);

app.mount("#app");
