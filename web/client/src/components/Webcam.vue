<script setup>
import { ref, watch } from "vue";

const camera = ref(null);
const picture = ref(null);

const getVideo = () => {
    navigator.mediaDevices
        .getUserMedia({ video: true })
        .then((stream) => {
            let video = camera.value;
            video.srcObject = stream;
            video.play();
        })
        .catch((err) => console.log(err));
};

const takeSnapshot = () => {
    const width = 500;
    const height = 500;

    let video = camera.value;

    picture.value.width = width;
    picture.value.height = height;

    let ctx = picture.value.getContext("2d");
    ctx.drawImage(video, 0, 0, width, height);
};

watch(camera, () => {
    getVideo();
});
</script>

<template>
    <div class="camera">
        <div class="camera__wrapper">
            <video ref="camera"></video>
        </div>

        <button @click="takeSnapshot">SNAP!</button>
    </div>

    <div class="result">
        <canvas ref="picture"></canvas>
    </div>
</template>

<style lang="scss" scoped>
.camera {
    background-color: rgba(0, 255, 255, 0.5);
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    gap: 2rem;

    &__wrapper {
        width: 60%;
        overflow: hidden;

        video {
            width: 100%;
            height: auto;
        }
    }
}

.result {
    margin-top: 2rem;
}
</style>
