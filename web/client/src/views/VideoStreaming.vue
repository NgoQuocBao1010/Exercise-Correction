<script setup>
import { ref } from "vue";
import axios from "axios";
import Video from "../components/Video.vue";

const video = ref(null);
const processing = ref(false);
const videoName = ref(null);

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
        processing.value = true;
        const response = await axios.post(
            "http://127.0.0.1:8000/api/video/upload",
            { file: video.value },
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );

        videoName.value = response.data.file_name;
    } catch (e) {
        console.log("Error: ", e);
    } finally {
        processing.value = false;
    }
};
</script>

<template>
    <template v-if="null">
        <Video></Video>
    </template>

    <input type="file" @change="onFileUpload" accept="video/*" />
    <button @click="uploadToServer">Upload!</button>

    <h2 v-if="processing">Processing ...</h2>

    <Video v-if="videoName" :videoName="videoName"> </Video>
</template>

<style lang="scss" scoped></style>
