<template>
    <div class="container">
        <p ref="refTxt">{{ 
            progress.status !='Complete' ?
            `Preparing Mask - Step ${progress.progress}`:
            "Choose one of the masks below: "
        }}</p>
        <div ref="imageGroup" v-if="progress.status=='Complete'">
            <img v-for="uuid in result_uuids" :key="uuid" :src="`/temp/${uuid}.png`" :data-uuid="uuid" @click="handleClick"/>
        </div>
    </div>
</template>
<script>
import {inject, reactive, ref} from 'vue';
import { start_mask_gen, query_mask_status } from '@/api';

export default {
    setup(props, { emit }){
        // const emit=defineEmits();
        const progress=reactive({
            status:'',
            progress:0
        });

        const char_data = inject('char_data');
        // const refTxt=ref(null);
        // const imageGroup=ref(null);
        var result_uuids=ref([]);
        var job_uuid=ref(null);

        const initialize=async function(){
            var response=await start_mask_gen(char_data);
            result_uuids.value=response.uuid;
            job_uuid.value=response.job_uuid;
            const intervalId=setInterval(async ()=>{
                const status=await query_mask_status(job_uuid.value);
                progress.status=status.status;
                progress.progress=status.progress;
                if(status.status=='Complete'){
                    clearInterval(intervalId);
                }
            },3000)
        }

        const handleClick=function(event){
            const chossenUuid=event.target.dataset.uuid;
            console.log(`choosing mask uuid: ${chossenUuid}`);
            emit('complete', chossenUuid);
        }

        initialize();
        return {
            handleClick,
            progress,
            result_uuids,
        }
    }
}
</script>
<style scoped>
img {
    max-width: 100px;
    padding: 10px;
    display: inline-block;
}
</style>