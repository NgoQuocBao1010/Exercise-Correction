<script setup></script>

<template>
    <div class="player">
        <video controls muted autoPlay>
            <source src="http://127.0.0.1:8000/api/video" type="video/mp4" />
        </video>
    </div>
</template>

<style lang="scss" scoped>
video {
    width: 400px;
}
</style>
