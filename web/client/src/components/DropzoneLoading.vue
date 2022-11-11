<script setup></script>

<template>
    <div class="dropzone">
        <div class="loading-animation">
            <div class="dot"></div>
            <div class="dot"></div>
            <div class="dot"></div>
        </div>

        Processing ...
    </div>
</template>

<style lang="scss" scoped>
.dropzone {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    border: 0.2rem dashed var(--primary-color);
    padding: 2rem;
    border-radius: 0.25rem;
    background-color: #fff;
    font-size: 1.25rem;
    transition: 0.25s background-color ease-in-out;
    cursor: pointer;

    &-icon {
        display: block;
        font-size: 3rem;
        margin: 0 auto 1.5rem;
        color: var(--primary-color);
    }

    &-input {
        display: none;
    }
}

.loading-animation {
    display: flex;
    gap: 1rem;
    margin-bottom: 2rem;

    .dot {
        display: inline-block;
        width: 20px;
        aspect-ratio: 1 / 1;
        border-radius: 100%;
        background-color: var(--primary-color);
    }
}

.loading-animation .dot:nth-last-child(1) {
    animation: loading 0.6s 0.1s linear infinite;
}
.loading-animation .dot:nth-last-child(2) {
    animation: loading 0.6s 0.2s linear infinite;
}
.loading-animation .dot:nth-last-child(3) {
    animation: loading 0.6s 0.3s linear infinite;
}

@keyframes loading {
    0% {
        transform: translate(0, 0);
    }
    50% {
        transform: translate(0, 15px);
    }
    100% {
        transform: translate(0, 0);
    }
}
</style>
