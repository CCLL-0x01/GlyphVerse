<template>
    <div v-if="!this.$data.promptsLoaded">
        <p>loading prompts...</p>
    </div>
    <div v-if="this.$data.promptsLoaded">
        <div>
            <div>
                <label for="sub_prompt">主体</label>
                <input id="sub_prompt" type="text" v-model="sub_prompt" placeholder="请输入主体" />
            </div>

            <div>
                <label>环境</label>
                <table>
                    <thead>
                        <tr>
                            <th>Prompt 内容</th>
                            <th>操作</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-for="(item, index) in surr_prompt" :key="index">
                            <td>
                                <input type="text" v-model="surr_prompt[index]" placeholder="请输入环境提示" />
                            </td>
                            <td>
                                <button @click="removePrompt(index)">删除</button>
                            </td>
                        </tr>
                    </tbody>
                </table>
                <button @click="addPrompt">添加环境</button>
            </div>

            <!--<button @click="submit">OK</button> -->
        </div>
    </div>
</template>

<script>
export default {
    data() {
        return {
            sub_prompt: "", 
            surr_prompt: [], 
            promptsLoaded:false, //prompts是否初始化
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
            this.surr_prompt.push(""); // 在数组末尾添加一个空字符串，表示新的提示
        },

        // 删除指定的环境提示
        removePrompt(index) {
            this.surr_prompt.splice(index, 1); // 根据索引删除对应的提示
        },

        // 提交时触发，通常会用来处理外部传递数据
        // submit() {
        //     this.$emit("complete", this.prompts);
        // },
        init(prompts){
            this.$data.sub_prompt=prompts.sub_prompt;
            this.$data.surr_prompt=prompts.surr_prompt;
            this.$data.promptsLoaded=true;
        },
    },
};
</script>

<style scoped>
table {
    width: 100%;
    border-collapse: collapse;
}

table th,
table td {
    padding: 8px;
    text-align: left;
    border: 1px solid #ccc;
}

button {
    margin-top: 10px;
    padding: 5px 10px;
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}

input[type="text"] {
    width: 100%;
    padding: 5px;
    border: 1px solid #ccc;
    margin-top: 5px;
}
</style>