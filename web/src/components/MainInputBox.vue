<template>
    <div class="wrapper">
        <input type="text" class="input" placeholder="输入一个中国汉字" v-model="inputValue" @keyup.enter="handleClick"
            :disabled="!enabled">
        <Transition name="buttonTransition">
            <button v-if="enabled" class="button" id="go-button" @click="handleClick">Go</button>
        </Transition>
    </div>
</template>

<script>
export default {
    data() {
        return {
            inputValue: '',
            enabled: true
        };
    },
    methods: {
        //handleInput(event) {
        //    if (event.keyCode === 13) {
        //        this.$refs['go-button'].click();
        //    }
        //},
        handleClick() {
            //console.log(this.inputValue)
            if(this.inputValue == '' || !/[\u4e00-\u9fa5]/.test(this.inputValue.trim()) || this.inputValue.trim().length > 1) {
                alert('请输入一个汉字');
                return;
            }
            this.enabled = false;
            this.$emit('inputComplete', this.inputValue);
        }
    }
};
</script>

<style scoped>
.wrapper {
    display: flex;
    align-items: center;
    display: flex;
    align-items: center;
    background: white;
    border-radius: 30px;
    padding: 10px;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    /*animation: zoomIn 0.5s;*/
    width: 400px;
}

.input {
    border: none;
    outline: none;
    padding: 10px;
    font-size: 1.2em;
    flex-grow: 1;
    border-radius: 30px 0 0 30px;
    text-align: center;
}
.button {
    padding: 10px 20px;
    font-size: 1.2em;
    color: white;
    background-color: #4a90e2;
    border: none;
    border-radius: 0 30px 30px 0;
    cursor: pointer;
    transition: background-color 0.3s;
}
.buttonTransition-enter, .buttonTransition-leave-to {
    opacity: 0;
}
.buttonTransition-enter-active, .buttonTransition-leave-active {
    transition: opacity 0.3s ease-in;
}
@keyframes fadeIn {
    from { opacity: 0; transform: scale(0.3); }
    to { opacity: 1; transform: scale(1); }
}
.wrapper {
    animation: fadeIn 0.3s /* 应用动画 */
}
</style>