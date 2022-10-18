import { createRouter, createWebHistory } from "vue-router";

const router = createRouter({
    history: createWebHistory(import.meta.env.BASE_URL),
    routes: [
        {
            path: "/",
            name: "Home",
            component: () => import("../views/Home.vue"),
        },
        {
            path: "/mediapipe",
            name: "Mediapipe",
            component: () => import("../views/Mediapipe.vue"),
        },
        {
            path: "/video",
            name: "VideoStreaming",
            component: () => import("../views/VideoStreaming.vue"),
        },
    ],
});

export default router;
