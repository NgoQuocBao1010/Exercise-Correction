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

    <!-- Footer -->
    <footer>
        <a
            href="https://twitter.com/ngohquocbao1010"
            target="_blank"
            class="twitter"
        >
            @NgoQuocBao
        </a>

        <a
            href="https://github.com/NgoQuocBao1010/Exercise-Correction"
            target="_blank"
            class="github"
        >
            <i class="fa-brands fa-github"></i>
        </a>
    </footer>
</template>

<style lang="scss">
body {
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

    footer {
        width: 90vw;
        border-top: 1px solid var(--primary-color);
        position: fixed;
        bottom: 0;
        left: 50%;
        transform: translateX(-50%);
        margin-inline: auto;
        padding: 0.3rem 0;
        text-align: center;

        a {
            font-family: var(--font-family);
            color: var(--primary-color);
        }

        .twitter {
            font-weight: 700;
        }

        .github {
            font-size: 1.2rem;
            margin-left: 1rem;
        }
    }
}
</style>
