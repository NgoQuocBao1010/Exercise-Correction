<script setup>
import axios from "axios";
import { ref } from "vue";

const result = ref("...");

const callApiExample = async () => {
    try {
        const response = await axios.get("http://127.0.0.1:8000/api");

        result.value = JSON.stringify(response.data);
    } catch (e) {
        console.log(e);
        result.value = "ERROR";
    }
};
</script>

<template>
    <p>{{ result }}</p>
    <button @click="callApiExample">Call API</button>
</template>

<style lang="scss" scoped></style>
