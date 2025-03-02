<template>
    <div>
        <p ref="refTxt"> {{ progress.status }} - {{ progress.progress }} </p>
        <img ref="refImg" :src="`/temp/${result_uuid}.png`" v-if="progress.status === 'Complete'" />
    </div>
</template>

<script>
import { inject, reactive, ref } from 'vue';
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
            const intervalId = setInterval(async () => {
                const status = await query_status(result_uuid.value);
                progress.status = status.status;
                progress.progress = status.progress;
                if (status.status === 'Complete') {
                    clearInterval(intervalId);
                }
            }, 3000);
        };

        initialize();

        return {
            progress,
            refTxt,
            refImg,
            result_uuid,
        };
    },
};
</script>
