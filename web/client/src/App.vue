<script setup>
import Webcam from "./components/Webcam.vue";
</script>

<template>
    <main>
        <h1>Hello from Quoc Bao</h1>

        <Webcam />
    </main>
</template>

<style lang="scss">
body {
    height: 100vh;
    background-color: black;

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
