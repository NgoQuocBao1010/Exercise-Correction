<script setup>
import Webcam from "./components/Webcam.vue";
</script>

<template>
    <main>
        <RouterView />
    </main>
</template>

<style lang="scss">
body {
    height: 100vh;

    main {
        margin-inline: auto;
        width: 80vw;
    }

    h1 {
        color: white;
        text-align: center;
    }
}
</style>
