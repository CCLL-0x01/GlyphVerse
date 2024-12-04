<template>
    <h1 class="title">{{ title }}</h1>
</template>

<script>
export default {
    props: {
        title: {
            type: String,
            required: true
        }
    }
};
</script>

<style scoped>
@keyframes fade{
    from{
        opacity: 0;
        transform: scale(0.5);
    }
    to{
        opacity: 1;
        transform: scale(1);
    }
}

.title {
    color: white;
    font-size: 3em;
    text-shadow: 2px 2px 10px rgba(0, 0, 0, 0.5);
    animation: fade 0.3s;
}

</style>