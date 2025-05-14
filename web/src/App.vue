<template>
    <div class="container-main">
        <AppHeader title="艺术字生成" />
        <MainInputBox @inputComplete="handleCharacterInput" />
        <div class="contents">
            <div class="two-col">
                <CharVisualEditor class="left-col" ref="editRef" @complete="handleCharEditComplete" v-if="[1,2,3].includes(state.state)" />
                <PromptEditor class="right-col" ref="promptRef" v-if="[2,3].includes(state.state)"/>
            <!--v-show=state.promptLoaded -->
            </div>

            <button class="generate-button" v-if="state.state === 3" @click="handleGenerate">生成</button>
        </div>
        <MaskInferStatus v-if="state.state == 4" @complete="handleMaskGenerate"/>
        <InferStatus v-if="state.state === 5" />
    </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import MainInputBox from './components/MainInputBox.vue';
import CharVisualEditor from './components/CharVisualEditor.vue';
import PromptEditor from './components/PromptEditor.vue';
import InferStatus from './components/InferStatus.vue';
import { reactive, ref, nextTick, provide } from 'vue';
import { generate_character_prompt, upload_img_data } from './api';
import MaskInferStatus from './components/MaskInferStatus.vue';

export default {
    name: 'App',
    components: {
        AppHeader,
        MainInputBox,
        CharVisualEditor,
        PromptEditor,
        InferStatus,
        MaskInferStatus
    },
    setup() {
        // 创建响应式的 state 对象
        const state = reactive({
            state: 0,
            // loadingPrompt: "",
            promptsLoaded: false,
            changeState(s) {
                state.state = s;
            },
            // showLoading(s) {
            //     state.loadingPrompt = s;
            // },
            // hideLoading() {
            //     state.loadingPrompt = '';
            // }
        });

        const char_data = reactive({
            char: "",
            prompts: {
                sub_prompt: "",
                surr_prompt: [],
            },
            mask: "",
            beautified_mask: "",
            char_img: "",
            lora: ""
        });

        provide('char_data', char_data);

        const editRef = ref(null);
        const promptRef = ref(null);

        // 主要处理逻辑
        const handleCharacterInput = async function (input) {
            console.log('Input:', input);
            char_data.char = input;
            // state.showLoading('Loading prompts...');

            state.changeState(1);
            console.log(editRef.value);
            nextTick(function () {
                //显示char visual editor编辑器
                console.log(editRef.value);
                editRef.value.init(input);
                editRef.value.render();
                state.changeState(2);
            });
            char_data.prompts = await generate_character_prompt(char_data.char);
            nextTick(function(){
                promptRef.value.init(char_data.prompts);
                state.promptsLoaded=true;
            })

            // // 更新 state 状态
            // state.changeState(1);
            // nextTick(function(){
            //     editRef.value.render();
            //     editRef.value.char=input;
            // });
        };

        const handleCharEditComplete = async function () {
            var char_img_uuid = await upload_img_data(editRef.value.$data.charImgData);
            var mask_uuid = await upload_img_data(editRef.value.$data.maskData);
            char_data.mask=mask_uuid;
            char_data.char_img = char_img_uuid;
            state.changeState(3);
        }
        
        const handleGenerate = function () {
            char_data.prompts.sub_prompt=promptRef.value.prompts.sub_prompt;
            char_data.prompts.surr_prompt=promptRef.value.prompts.surr_prompt;
            console.log(char_data);
            state.changeState(4);
        }

        const handleMaskGenerate = function (data){
            var {chosenUuid, lora_enabled, lora} = data;
            char_data.beautified_mask=chosenUuid;
            char_data.lora=lora_enabled.value?lora:null;
            console.log(`beautified: ${chosenUuid}`);
            state.changeState(5);
        }

        return {
            handleCharacterInput,
            handleGenerate,
            state,
            editRef,
            handleCharEditComplete,
            char_data,
            // handlePromptEditComplete,
            promptRef,
            handleMaskGenerate
        };
    },
};
</script>

<style>

.container-main {

    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;

}

body {
    display: flex;
    flex-direction: column;
    justify-content: center;
    align-items: center;
    height: 100vh;
    margin: 0;
    background: linear-gradient(to right, #4a90e2, #9013fe);
    font-family: Arial, sans-serif;
    overflow-y:auto;
}

.two-col {
    display: flex;
    justify-content: space-between;
    width: 80vw;
}

.left-col {
    display: inline-block;
    width: 45%;
}

.right-col {
    display: inline-block;
    width: 45%;
}

.contents {
    margin: 5%;
    display: flex;
    flex-direction: column;
    align-items: center;
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

.generate-button:hover {
    background-color: #ff00cc;
}

.generate-button {
    margin-top: 20px;
    padding: 20px 30px;
    border: none;
    border-radius: 30px;
    cursor: pointer;
    color: white;
    transition: background-color 0.3s;
    background-color: #aa49ff;
    font-size: xx-large;
}
</style>
