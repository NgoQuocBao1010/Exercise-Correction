<script setup>
import { ref, computed } from "vue";
import axios from "axios";

import Dropzone from "../components/Dropzone.vue";
import DropzoneLoading from "../components/DropzoneLoading.vue";

const EXERCISES = ["squat", "plank", "bicep_curl", "lunge"];

const submitData = ref({
    videoFile: null,
    exerciseType: null,
});
const processedData = ref(null);
const isProcessing = ref(false);
const summaryData = computed(() => {
    if (!processedData.value) return;

    let results = {
        total: 0,
        totalInString: "",
        details: {},
    };

    console.log(processedData.value);

    let totalErrors = processedData.value.details.length;
    results.total = totalErrors;
    if (totalErrors == 0 || totalErrors == 1)
        results.totalInString = `${totalErrors} error`;
    else results.totalInString = `${totalErrors} errors`;

    processedData.value.details.forEach((error) => {
        let stage = error.stage;
        results.details[stage] = results.details[stage]
            ? results.details[stage] + 1
            : 1;
    });

    return results;
});

const dummy = {
    processed: true,
    file_name: "video_20221111084857.mp4",
    details: [
        {
            stage: "knee too wide",
            frame: "http://127.0.0.1:8000/static/images/video_20221111084857_0.jpg",
        },
        {
            stage: "knee too tight",
            frame: "http://127.0.0.1:8000/static/images/video_20221111084857_1.jpg",
        },
    ],
};

const uploadToServer = async () => {
    if (!submitData.value.videoFile) {
        alert("No video selected");
        return;
    }

    if (!submitData.value.exerciseType) {
        alert("No exercise type selected");
        return;
    }

    processedData.value = null;
    try {
        isProcessing.value = true;
        const { data } = await axios.post(
            `http://127.0.0.1:8000/api/video/upload?type=${submitData.value.exerciseType}`,
            { file: submitData.value.videoFile },
            {
                headers: {
                    "Content-Type": "multipart/form-data",
                },
            }
        );
        processedData.value = data;
        console.log(data);
    } catch (e) {
        console.log("Error: ", e);
    } finally {
        isProcessing.value = false;
    }
};

const summary = (data) => {
    let results = {
        total: 0,
        totalInString: "",
        details: {},
    };

    let totalErrors = data.details.length;
    results.total = totalErrors;
    if (totalErrors == 0 || totalErrors == 1)
        results.totalInString = `${totalErrors} error`;
    else results.totalInString = `${totalErrors} errors`;

    data.details.forEach((error) => {
        let stage = error.stage;
        results.details[stage] = results.details[stage]
            ? results.details[stage] + 1
            : 1;
    });

    return results;
};

const summaryDummy = summary(dummy);
</script>

<template>
    <!-- Input section -->
    <section class="input-section">
        <Dropzone
            v-show="!isProcessing"
            @file-uploaded="(file) => (submitData.videoFile = file)"
        />
        <DropzoneLoading v-show="isProcessing" />

        <div class="right-container">
            <!-- exercises selection -->
            <div class="exercises-container">
                <p
                    class="exercise"
                    v-for="exercise in EXERCISES"
                    :class="{ active: submitData.exerciseType == exercise }"
                    @click="submitData.exerciseType = exercise"
                >
                    {{ exercise }}
                </p>
            </div>

            <button class="process-btn" @click="uploadToServer">
                <span>Process!</span>
            </button>
        </div>
    </section>

    <!-- Results section -->
    <section class="result-section" v-if="processedData">
        <ul class="tab-links">
            <li class="active">Summary</li>
            <li>Detail</li>
            <li>Full Video</li>
        </ul>

        <div class="tab-container">
            <p class="main">
                There are
                <span class="error-color">
                    {{ summaryData.totalInString }}
                </span>
                found.

                <!-- Icon -->
                <i
                    class="fa-solid fa-circle-exclamation error-color"
                    v-if="summaryData.total > 0"
                ></i>
                <i class="fa-solid fa-circle-check" v-else></i>
            </p>

            <ul class="errors" v-if="summaryData.total > 0">
                <li v-for="(total, error) in summaryData.details">
                    <i class="fa-solid fa-caret-right"></i>

                    {{ error }}: {{ total }}
                </li>
            </ul>
        </div>
    </section>
</template>

<style lang="scss" scoped>
.input-section {
    display: flex;
    gap: 1rem;

    * {
        flex: 1;
    }

    .right-container {
        display: flex;
        flex-direction: column;
        width: 100%;

        .exercises-container {
            display: flex;
            flex-wrap: wrap;
            gap: 1rem;
            margin-bottom: 1rem;

            .exercise {
                display: flex;
                justify-content: center;
                align-items: center;
                padding: 1rem 0;
                flex: 45%;
                color: var(--secondary-color);
                text-transform: uppercase;
                border: 3px solid var(--primary-color);
                border-radius: 0.3rem;
                cursor: pointer;
                transition: all 0.25s ease;

                &:hover {
                    box-shadow: 0 6px 18px 0 rgba(#000, 0.1);
                    transform: translateY(-6px);
                }

                &.active {
                    background-color: var(--primary-color);
                    font-weight: 700;
                }
            }
        }

        .process-btn {
            border: none;
            background-color: var(--primary-color);
            padding: 1.25rem 0;

            color: whitesmoke;
            font-size: 1.25rem;
            font-weight: 700;
            cursor: pointer;
            border-radius: 8px;
            transition: all 0.25s ease;

            &:hover {
                box-shadow: 0 6px 18px 0 rgba(#000, 0.1);
                color: var(--primary-color);
                border-color: transparent;
                background-color: transparent;
            }
        }
    }
}

.result-section {
    margin: 2rem 0;

    .tab-links {
        display: flex;

        li {
            width: 6em;
            padding: 0.75rem 1rem;
            padding-right: 1.2rem;
            background-color: rgb(180, 179, 179);
            border-top-left-radius: 1rem;
            border-top-right-radius: 1rem;
            font-size: 1rem;
            text-transform: uppercase;
            cursor: pointer;
            transition: all 0.2s ease;

            &.active {
                background-color: var(--primary-color);
            }

            &:hover {
                background-color: rgba($color: #41b883, $alpha: 0.4);
            }
        }
    }

    .tab-container {
        padding: 1rem 2rem;
        border: 3px solid var(--primary-color);

        p.main {
            font-size: 1.5rem;
            margin: 1rem 0;

            i {
                font-size: 1.5rem;
            }
        }

        ul.errors {
            li {
                margin: 0.75rem 0;
                font-size: 1.2rem;
                text-transform: capitalize;

                i {
                    margin-right: 1rem;
                }
            }
        }
    }

    .error-color {
        color: red;
    }
}
</style>
