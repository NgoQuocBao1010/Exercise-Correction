const video5 = document.getElementsByClassName("input_video5")[0];
const out5 = document.getElementsByClassName("output5")[0];
const controlsElement5 = document.getElementsByClassName("control5")[0];
const canvasCtx5 = out5.getContext("2d");

const fpsControl = new FPS();

const spinner = document.querySelector(".loading");
spinner.ontransitionend = () => {
    spinner.style.display = "none";
};

function zColor(data) {
    const z = clamp(data.from.z + 0.5, 0, 1);
    return `rgba(0, ${255 * z}, ${255 * (1 - z)}, 1)`;
}

function onResultsPose(results) {
    if (!results.poseLandmarks) return;

    document.body.classList.add("loaded");
    fpsControl.tick();

    canvasCtx5.save();
    canvasCtx5.clearRect(0, 0, out5.width, out5.height);
    canvasCtx5.drawImage(results.image, 0, 0, out5.width, out5.height);
    drawConnectors(canvasCtx5, results.poseLandmarks, POSE_CONNECTIONS, {
        color: (data) => {
            const x0 = out5.width * data.from.x;
            const y0 = out5.height * data.from.y;
            const x1 = out5.width * data.to.x;
            const y1 = out5.height * data.to.y;

            const z0 = clamp(data.from.z + 0.5, 0, 1);
            const z1 = clamp(data.to.z + 0.5, 0, 1);

            const gradient = canvasCtx5.createLinearGradient(x0, y0, x1, y1);
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
        canvasCtx5,
        Object.values(POSE_LANDMARKS_LEFT).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#FF0000" }
    );
    drawLandmarks(
        canvasCtx5,
        Object.values(POSE_LANDMARKS_RIGHT).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#00FF00" }
    );
    drawLandmarks(
        canvasCtx5,
        Object.values(POSE_LANDMARKS_NEUTRAL).map(
            (index) => results.poseLandmarks[index]
        ),
        { color: zColor, fillColor: "#AAAAAA" }
    );
    canvasCtx5.restore();
}

const pose = new Pose({
    locateFile: (file) => {
        return `https://cdn.jsdelivr.net/npm/@mediapipe/pose@0.2/${file}`;
    },
});
pose.onResults(onResultsPose);

const camera = new Camera(video5, {
    onFrame: async () => {
        await pose.send({ image: video5 });
    },
    width: 480,
    height: 480,
});
camera.start();

new ControlPanel(controlsElement5, {
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
            range: [0.5, 1],
            step: 0.01,
        }),
        new Slider({
            title: "Min Tracking Confidence",
            field: "minTrackingConfidence",
            range: [0.5, 1],
            step: 0.01,
        }),
    ])
    .on((options) => {
        video5.classList.toggle("selfie", options.selfieMode);
        pose.setOptions(options);
    });
