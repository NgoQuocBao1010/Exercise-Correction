<script setup></script>

<template>
    <!-- Navbar -->
    <nav>
        <RouterLink :to="{ name: 'Home' }" class="nav__header">
            Exercise Correction
        </RouterLink>
    </nav>

    <!-- Main Content -->
    <main>
        <!-- Page View -->
        <RouterView />
    </main>
</template>

<style lang="scss">
body {
    // background-color: black;

    nav {
        margin: 3rem 0;
        text-align: center;

        .nav__header {
            font-size: 2rem;
            font-family: var(--font-family);
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 1px;
            color: var(--primary-color);
        }
    }

    main {
        margin-inline: auto;
        width: 90vw;
    }
}
</style>
