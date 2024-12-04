<template>
    <div class="container">
        <AppHeader title="艺术字生成" />
        <MainInputBox @input="handleCharacterInput" />
        <CharVisualEditor char="好" @complete="console.log" />
    </div>
</template>

<script>
import AppHeader from './components/AppHeader.vue';
import MainInputBox from './components/MainInputBox.vue';
import CharVisualEditor from './components/CharVisualEditor.vue';
export default {
    name: 'App',
    components: {
        AppHeader,
        MainInputBox,
        CharVisualEditor,
    },
    props:{
        state:{
            type:Number,
            default:0,
            /*****
             * 0:开始界面
             * 1:正在请求
             * 2:划分字体偏旁
             */
            required:false
        }
    },
    methods: {
        handleCharacterInput(input) {
            console.log('Input:', input);
        }
    }
}
</script>

<style>
.container {
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
}
</style>
