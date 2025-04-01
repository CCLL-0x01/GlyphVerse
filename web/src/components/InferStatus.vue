<template>
    <div class="contents">
        <p ref="refTxt"> {{ progress.status }} - {{ progress.progress }} </p>
        <img ref="refImg" :src="`/temp/${result_uuid}.png`" v-if="progress.status === 'Complete'" />
    </div>
</template>

<script>
import { inject, nextTick, reactive, ref } from 'vue';
import { start_inference, query_status } from '../api';

export default {
    setup() {
        const progress = reactive({
            status: '',
            progress: 0,
        });

        const char_data = inject('char_data');
        const refTxt = ref(null);
        const refImg = ref(null);
        const result_uuid = ref(null);

        const initialize = async () => {
            result_uuid.value = await start_inference(char_data);
            console.log(result_uuid.value)
            const intervalId = setInterval(async () => {
                const status = await query_status(result_uuid.value);
                progress.status = status.status;
                progress.progress = status.progress;
                if (status.status === 'Complete') {
                    clearInterval(intervalId);
                }
            }, 3000);
        };
        nextTick(initialize)

        return {
            progress,
            refTxt,
            refImg,
            result_uuid,
        };
    },
};
</script>

<style scoped>


.container {
    border: 1px solid #ccc;
    border-radius: 30px;
    padding: 30px 60px;
    margin: 20px;
    animation: fadeIn 0.5s;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    color: white;
}

@keyframes fadeIn {
    from {
        opacity: 0;
        transform: scale(0.5);
    }

    to {
        opacity: 1;
        transform: scale(1);
    }
}

</style>