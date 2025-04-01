<template>
    <div class="container">
        <p ref="refTxt">{{ 
            progress.status !='Complete' ?
            `正在生成艺术字形 - 第${progress.progress}步`:
            "请在下面选择一个字形："
        }}</p>
        <div ref="imageGroup" v-if="progress.status=='Complete'">
            <img v-for="uuid in result_uuids" :key="uuid" :src="`/temp/${uuid}.png`" :data-uuid="uuid" @click="handleClick"/>
        </div>
    </div>

    <div class="container">
        <div ref="loraChooserContainer">
            <input type="checkbox" v-model="lora_enabled"/> 使用LoRA增强生成：
            <select :disabled="!lora_enabled" v-model="chosen_lora">
                <option v-for="lora in lora_list" :key="lora" >
                    {{lora}}
                </option>
            </select>
        </div>
    </div>
</template>
<script>
import {inject, reactive, ref} from 'vue';
import { start_mask_gen, query_mask_status, get_lora_list } from '@/api';

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

        var lora_enabled=ref(false);
        var lora_list=ref([]);
        var chosen_lora=ref('');

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
            },3000);

            lora_list.value=await get_lora_list();
        }

        const handleClick=function(event){
            const chosenUuid=event.target.dataset.uuid;
            console.log(`choosing mask uuid: ${chosenUuid}`);
            emit('complete', {
                "chosenUuid":chosenUuid,
                "lora_enabled":lora_enabled,
                "lora":chosen_lora
            });
        }

        initialize();
        return {
            handleClick,
            progress,
            result_uuids,
            lora_enabled,
            lora_list,
            chosen_lora
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