<script setup>
import { drawConnectors, drawLandmarks } from "@mediapipe/drawing_utils";
import { Pose, POSE_CONNECTIONS } from "@mediapipe/pose";
import { Camera } from "@mediapipe/camera_utils";

import { onMounted, ref } from "vue";

const loadCamera = ref(false);
const container = ref(null);
const ctx = ref(null);
const canvas = ref(null);
const canvasWidth = ref(null);
const canvasHeight = ref(null);
const video = ref(null);
const camera = ref(null);

// Initialize Mediapipe
const onMediapipeResults = (results) => {
    const videoWidthHeightRatio =
        video.value.videoHeight / video.value.videoWidth;

    canvasWidth.value = results.image.width;
    canvasHeight.value = results.image.height;

    ctx.value.save();

    // Draw to canvas
    try {
        ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);

        ctx.value.globalCompositeOperation = "destination-atop";

        ctx.value.drawImage(
            results.image,
            0,
            0,
            canvas.value.width,
            canvas.value.height
        );
    } catch (e) {
        console.log("ERROR DRAW TO CANVAS", e);
    }

    ctx.value.globalCompositeOperation = "source-over";

    // Get pose landmarks
    if (results.poseLandmarks) {
        // Draw Landmarks and Connectors
        drawConnectors(ctx.value, results.poseLandmarks, POSE_CONNECTIONS, {
            color: "#85929E",
            lineWidth: 5,
            visibilityMin: 0.65,
        });

        drawLandmarks(ctx.value, results.poseLandmarks, {
            color: "#48C9B0",
            lineWidth: 5,
            visibilityMin: 0.65,
        });
    } else {
    }

    ctx.value.restore();
};

const initMediapipe = () => {
    const pose = new Pose({
        locateFile: (file) => {
            return `https://cdn.jsdelivr.net/npm/@mediapipe/pose/${file}`;
        },
    });

    // Arguments for mediapipe
    pose.setOptions({
        modelComplexity: 1,
        smoothLandmarks: true,
        enableSegmentation: true,
        smoothSegmentation: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
    });

    pose.onResults(onMediapipeResults);

    camera.value = new Camera(video.value, {
        onFrame: async () => {
            await pose.send({
                image: video.value,
            });

            if (!loadCamera.value) {
                loadCamera.value = true;
                console.log("LOADED WEBCAM");
            }
        },
    });
    camera.value.start();
};

const stopCamera = () => {
    camera.value.stop();
    ctx.value.clearRect(0, 0, canvas.value.width, canvas.value.height);
};

onMounted(() => {
    ctx.value = canvas.value.getContext("2d");

    try {
        initMediapipe();
    } catch (e) {
        console.log("ERROR INIT MEDIAPIPE");
    }
});
</script>

<template>
    <p v-if="!loadCamera">Loading ...</p>
    <div class="container" style="margin-top: 20px" ref="container">
        <video
            ref="video"
            autoplay
            width="100%"
            height="100%"
            style="display: none"
        ></video>

        <canvas
            ref="canvas"
            :width="canvasWidth"
            :height="canvasHeight"
        ></canvas>
    </div>

    <button @click="stopCamera">Stop</button>
</template>

<style lang="scss" scoped>
.container {
    width: 70%;
    margin-inline: auto;
    border: 1px solid black;
}
</style>
