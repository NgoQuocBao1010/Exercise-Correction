<script setup>
import { ref, computed, onMounted } from "vue";

const { videoName, startAt } = defineProps({
    videoName: String,
    startAt: {
        required: false,
        type: Number,
    },
});
const url = computed(
    () => `http://127.0.0.1:8000/api/video/stream?video_name=${videoName}`
);

const video = ref(null);
const videoContainer = ref(null);
onMounted(() => {
    if (startAt) video.value.currentTime = startAt;
});

const handleVideoLoad = () => {
    videoContainer.value.scrollIntoView({ behavior: "smooth", block: "end" });
};
</script>

<template>
    <!-- Video Player -->
    <div class="player" ref="videoContainer">
        <video
            controls
            muted
            autoPlay
            ref="video"
            @loadeddata="handleVideoLoad"
        >
            <source :src="`${url}`" type="video/mp4" />
        </video>
    </div>
</template>

<style lang="scss" scoped>
video {
    width: 100%;
}
</style>
