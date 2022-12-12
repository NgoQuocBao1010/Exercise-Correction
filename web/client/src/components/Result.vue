<script setup>
import { ref, computed } from "vue";

import Video from "./Video.vue";

const { data } = defineProps(["data"]);
const summaryData = computed(() => {
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
});
const selectedDisplay = ref("summary");
const videoStart = ref(0);

const jumpToVideoLocation = (second) => {
    selectedDisplay.value = "video";
    videoStart.value = second;
};
</script>

<template>
    <section class="result-section">
        <!-- Navigators -->
        <ul class="tab-links">
            <li
                :class="{ active: selectedDisplay == 'summary' }"
                @click="() => (selectedDisplay = 'summary')"
            >
                Summary
            </li>
            <li
                :class="{ active: selectedDisplay == 'detail' }"
                @click="() => (selectedDisplay = 'detail')"
            >
                Detail
            </li>
            <li
                :class="{ active: selectedDisplay == 'video' }"
                @click="() => (selectedDisplay = 'video')"
            >
                Full Video
            </li>
        </ul>

        <!-- Contents -->
        <div class="tab-container">
            <!-- Summary content -->
            <template v-if="selectedDisplay == 'summary'">
                <!-- Display Counter or other information -->
                <p class="main" v-if="data.counter">
                    <span class="info-color" v-if="data.type != 'bicep_curl'">
                        Counter: {{ data.counter }}
                    </span>

                    <span class="info-color" v-else>
                        Left arm counter: {{ data.counter.left_counter }} -
                        Right arm counter: {{ data.counter.right_counter }}
                    </span>
                </p>

                <!-- Display error -->
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
            </template>

            <!-- Detail Content -->
            <KeepAlive>
                <template v-if="selectedDisplay == 'detail'">
                    <div
                        class="box-error"
                        v-for="(error, index) in data.details"
                    >
                        <p>
                            {{ index + 1 }}. {{ error.stage }} at
                            <span
                                class="error-time"
                                @click="jumpToVideoLocation(error.timestamp)"
                            >
                                {{ error.timestamp }} second
                            </span>
                        </p>
                        <img :src="`${error.frame}`" />
                        <hr />
                    </div>
                </template>
            </KeepAlive>

            <!-- Full Video content -->
            <KeepAlive>
                <template v-if="selectedDisplay == 'video'">
                    <div class="video-container">
                        <Video
                            :video-name="data.file_name"
                            :start-at="videoStart"
                        ></Video>
                    </div>
                </template>
            </KeepAlive>
        </div>
    </section>
</template>

<style lang="scss" scoped>
.result-section {
    margin-top: 2rem;
    margin-bottom: 5rem;

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

        .box-error {
            margin-bottom: 2rem;

            p {
                font-size: 1.2rem;
                text-transform: capitalize;
                margin-bottom: 0.5rem;
            }

            img {
                width: 500px;
            }

            span.error-time {
                color: rgb(85, 149, 171);
                cursor: pointer;
            }

            hr {
                background-color: var(--primary-color);
                color: var(--primary-color);
            }
        }

        .video-container {
            width: 80%;
            margin-inline: auto;
            display: flex;
            justify-content: center;
            align-items: center;
        }
    }

    .error-color {
        color: red;
    }

    .info-color {
        color: rgb(55, 194, 55);
    }
}
</style>
