<script setup>
import { ref } from "vue";
import axios from "axios";
import Video from "../components/Video.vue";

const video = ref(null);
const video_processed = ref(null);

const onFileUpload = (event) => {
    const target = event.target;

    if (target && target.files) {
        video.value = target.files[0];
    }
};

const uploadToServer = async () => {
    if (!video.value) {
        alert("No file selected");
        return;
    }

    try {
        const response = await axios.post(
            "http://127.0.0.1:8000/api/video/upload",
            { file: video.value },
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        video_processed.value = response.data.file_name;
    } catch (e) {
        console.log("Error: ", e);
    }
};
</script>

<template>
    <template v-if="null">
        <Video></Video>
    </template>

    <input type="file" @change="onFileUpload($event)" accept="video/*" />
    <button @click="uploadToServer">Upload!</button>

    <h2>
        Processed Video: <span>{{ video_processed }}</span>
    </h2>

    <video v-if="video_processed">
        <source :src="`http://${video_processed}`" />
    </video>
</template>

<style lang="scss" scoped></style>
