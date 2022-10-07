<script setup>
import { computed, onMounted, ref, watch } from "vue";

const video = ref(null);
const camera = ref(null);
const control = ref(null);
const outputCanvas = ref(null);
const canvasCtx = computed(() => {
    if (outputCanvas.value) return outputCanvas.value.getContext("2d");

    return null;
});

const fpsControl = new FPS();

const pose = new Pose({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.2/${file}`;
    },
});
pose.onResults(onResultsPose);

function zColor(data) {
    const z = clamp(data.from.z + 0.5, 0, 1);
    return `rgba(0, ${255 * z}, ${255 * (1 - z)}, 1)`;
}

function onResultsPose(results) {
    if (!results.poseLandmarks) return;

    fpsControl.tick();

    canvasCtx.value.save();
    canvasCtx.value.clearRect(
        0,
        0,
        outputCanvas.value.width,
        outputCanvas.value.height
    );
    canvasCtx.value.drawImage(
        results.image,
        0,
        0,
        outputCanvas.value.width,
        outputCanvas.value.height
    );

    drawConnectors(canvasCtx.value, results.poseLandmarks, POSE_CONNECTIONS, {
        color: (data) => {
            const x0 = outputCanvas.value.width * data.from.x;
            const y0 = outputCanvas.value.height * data.from.y;
            const x1 = outputCanvas.value.width * data.to.x;
            const y1 = outputCanvas.value.height * data.to.y;

            const z0 = clamp(data.from.z + 0.5, 0, 1);
            const z1 = clamp(data.to.z + 0.5, 0, 1);

            const gradient = canvasCtx.value.createLinearGradient(
                x0,
                y0,
                x1,
                y1
            );
            gradient.addColorStop(
                0,
                `rgba(0, ${255 * z0}, ${255 * (1 - z0)}, 1)`
            );
            gradient.addColorStop(
                1.0,
                `rgba(0, ${255 * z1}, ${255 * (1 - z1)}, 1)`
            );
            return gradient;
        },
    });
    drawLandmarks(
        canvasCtx.value,
        Object.values(POSE_LANDMARKS_LEFT).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#FF0000" }
    );
    drawLandmarks(
        canvasCtx.value,
        Object.values(POSE_LANDMARKS_RIGHT).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#00FF00" }
    );
    drawLandmarks(
        canvasCtx.value,
        Object.values(POSE_LANDMARKS_NEUTRAL).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#AAAAAA" }
    );
    canvasCtx.value.restore();
}

function stopCamera() {
    camera.value = null;
}

onMounted(() => {
    camera.value = new Camera(video.value, {
        onFrame: async () => {
            await pose.send({ image: video.value });
        },
        width: 480,
        height: 480,
    });
    camera.value.start();

    new ControlPanel(control.value, {
        selfieMode: true,
        upperBodyOnly: false,
        smoothLandmarks: true,
        minDetectionConfidence: 0.5,
        minTrackingConfidence: 0.5,
    })
        .add([
            new StaticText({ title: "MediaPipe Pose" }),
            fpsControl,
            new Toggle({ title: "Selfie Mode", field: "selfieMode" }),
            new Toggle({ title: "Upper-body Only", field: "upperBodyOnly" }),
            new Toggle({ title: "Smooth Landmarks", field: "smoothLandmarks" }),
            new Slider({
                title: "Min Detection Confidence",
                field: "minDetectionConfidence",
                range: [0, 1],
                step: 0.01,
            }),
            new Slider({
                title: "Min Tracking Confidence",
                field: "minTrackingConfidence",
                range: [0, 1],
                step: 0.01,
            }),
        ])
        .on((options) => {
            video.value.classList.toggle("selfie", options.selfieMode);
            pose.setOptions(options);
        });
});
</script>

<template>
    <div class="container" style="margin-top: 20px">
        <div class="columns">
            <!-- WEBCAM INPUT -->
            <div class="column">
                <article class="panel is-info">
                    <p class="panel-heading">Webcam Input</p>
                    <div class="panel-block">
                        <video class="input_video5" ref="video"></video>
                    </div>
                </article>
            </div>

            <!-- MEDIAPIPE OUTPUT -->
            <div class="column">
                <article class="panel is-info">
                    <p class="panel-heading">Mediapipe Pose Detection</p>
                    <div class="panel-block">
                        <canvas
                            class="output5"
                            width="480px"
                            height="480px"
                            ref="outputCanvas"
                        ></canvas>
                    </div>
                </article>
            </div>
        </div>

        <button @click="stopCamera">Stop</button>

        <div style="visibility: hidden" class="control5" ref="control"></div>
    </div>
</template>

<style lang="scss" scoped></style>
