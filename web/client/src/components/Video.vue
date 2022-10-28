<script setup>
import { computed } from "vue";

const { videoName } = defineProps({
    videoName: String,
});

const url = computed(
    () => `http://127.0.0.1:8000/api/video/stream?video_name=${videoName}`
);
</script>

<template>
    <br />
    <a :href="`${url}`" target="_blank">{{ url }}</a>

    <!-- Video Player -->
    <div class="player">
        <video controls muted autoPlay>
            <source :src="`${url}`" type="video/mp4" />
        </video>
    </div>
</template>

<style lang="scss" scoped>
video {
    width: 400px;
}
</style>
