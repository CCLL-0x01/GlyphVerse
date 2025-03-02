<template>
    <div>
        <div v-if="!this.$data.promptsLoaded" class="container">
            <p class="loading-text">loading prompts...</p>
        </div>
        <div v-if="this.$data.promptsLoaded">
            <div class="container-container">
                <div class="container">
                    <label for="sub_prompt" class="fade-in">主体</label>
                    <input id="sub_prompt" type="text" v-model="sub_prompt" placeholder="请输入主体" class="fade-in" />
                </div>

                <div class="container">
                    <label class="fade-in">环境</label>
                    <table valign="center" class="fade-in">
                        
                            <tr v-for="(item, index) in surr_prompt" :key="index">
                                <td>
                                    <input type="text" v-model="surr_prompt[index]" placeholder="请输入环境提示" />
                                </td>
                                <td>
                                    <button @click="removePrompt(index)">删除</button>
                                </td>
                            </tr>
                        
                    </table>
                    <button @click="addPrompt" class="fade-in">添加环境</button>
                </div>
            </div>
        </div>
    </div>
</template>


<script>
export default {
    data() {
        return {
            sub_prompt: "",
            surr_prompt: [],
            promptsLoaded: false, //prompts是否初始化
        };
    },
    computed: {
        // 向外暴露的prompts，包含主体和所有的环境提示
        prompts() {
            return {
                sub_prompt: this.sub_prompt,
                surr_prompt: this.surr_prompt,
            };
        }
    },
    methods: {
        // 增加环境提示
        addPrompt() {
            // this.surr_prompt.push("");
            // this.$nextTick(() => {
            //     const rows = this.$el.querySelectorAll('tr');
            //     const newRow = rows[rows.length - 1];
            //     newRow.classList.add('fade-in');
            // });
            this.surr_prompt.push(""); // 在数组末尾添加一个空字符串，表示新的提示
        },

        // 删除指定的环境提示
        removePrompt(index) {
            this.surr_prompt.splice(index, 1); // 根据索引删除对应的提示
            // const row = this.$el.querySelectorAll('tr')[index];
            // row.classList.add('fade-out');
            // setTimeout(() => {
            //     this.surr_prompt.splice(index, 1);
            // }, 200); // Match the duration of the fadeOut animation
        },

        // 提交时触发，通常会用来处理外部传递数据
        // submit() {
        //     this.$emit("complete", this.prompts);
        // },
        init(prompts) {
            this.$data.sub_prompt = prompts.sub_prompt;
            this.$data.surr_prompt = prompts.surr_prompt;
            this.$data.promptsLoaded = true;
        },
    },
};
</script>

<style scoped>
@keyframes fadeOut {
    from {
        opacity: 1;
        transform: scale(1);
    }

    to {
        opacity: 0;
        transform: scale(0.5);
    }
}

.fade-out {
    animation: fadeOut 0.2s forwards;
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

@keyframes slideIn {
    from {
        transform: translateY(-20px);
        opacity: 0;
    }

    to {
        transform: translateY(0);
        opacity: 1;
    }
}

.fade-in {
    animation: fadeIn 0.5s;
}

.fade-out {
    animation: fadeOut 0.5s forwards;
}

/* .fade-enter-active,
.fade-leave-active {
    transition: opacity 0.5s, transform 0.5s;
}

.fade-enter,
.fade-leave-to


    {
    opacity: 0;
    transform: scale(0.5);
} */

.loading-text {
    animation: slideIn 0.5s;
}

table {
    width: 100%;
    border-collapse: collapse;
}

table th,
table td {
    padding: 8px;
    text-align: left;
    border: none;
}

button {
    margin-top: 10px;
    padding: 10px 20px;
    background-color: #4a90e2;
    border: none;
    border-radius: 30px;
    cursor: pointer;
    color: white;
    transition: background-color 0.3s;
}

button:hover {
    background-color: #7ebaff;
}

input[type="text"] {
    width: 80%;
    padding: 10px;
    border: none;
    margin-top: 5px;
    background-color: white;
    color: #333;
    margin-left: 15px;
    border-radius: 30px;
    text-align: center;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
}

#sub_prompt {
    width: 90%;
}

input[type="text"]:focus {
    outline: none;
    border-color: #4a90e2;
}

label {
    display: block;
    font-size: larger;
    margin-left: 13px;
    color: white;
    text-align: center;
}

.container {
    text-align: center;
    margin: 10px;
    padding: 15px;
    color: white;
    border: 1px solid #ccc;
    border-radius: 30px;
    width: 100%;
    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2);
    animation: fadeIn 0.5s;
}

.container-container {
    display: flex;
    flex-direction: column;
    align-items: center;
    width: 100%;
    height: 100%;
}
</style>