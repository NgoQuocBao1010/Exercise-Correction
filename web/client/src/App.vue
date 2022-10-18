<script setup></script>

<template>
    <main>
        <ul>
            <RouterLink :to="{ name: 'Home' }">Home</RouterLink>
            <RouterLink :to="{ name: 'Mediapipe' }">Mediapipe</RouterLink>
            <RouterLink :to="{ name: 'VideoStreaming' }">
                Video Streaming
            </RouterLink>
        </ul>

        <!-- Page View -->
        <RouterView />
    </main>
</template>

<style lang="scss">
body {
    height: 100vh;

    main {
        margin-inline: auto;
        width: 80vw;

        ul {
            margin-block: 2rem;
            display: flex;
            gap: 2rem;
        }
    }
}
</style>
