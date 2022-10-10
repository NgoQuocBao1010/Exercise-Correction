<script setup>
import APIcall from "./components/APIcall.vue";
</script>

<template>
    <main>
        <RouterView />

        <APIcall />
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
