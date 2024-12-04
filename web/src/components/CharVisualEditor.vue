<template>
    <canvas :width="width" :height="height" ref="canvas" 
    @mousedown="handleMousedown" @mousemove="handleMousemove" @mouseup="handleMouseup"
    @touchstart.prevent="handleMousedown" @touchmove.prevent="handleMousemove" @touchend.prevent="handleMouseup"></canvas>
    <div class="confirm-btns" v-if="state==2">
        <button @click="handleConfirmBtn ">√</button>
        <button @click="handleResetBtn">×</button>
    </div>
</template>

<script>
export default {
    data() {
        return {
            width: this.$props.size,
            height: this.$props.size,
            userPath: [],
            state: 0, // 0: 未开始, 1: 绘制中, 2: 完成, 3:确认

        };
    },
    props: { 
        char: { 
            type: String, 
            required: true,
        },
        size:{
            type: Number,
            default:500,
            required:false,
        }
    },
    methods: {
        getPath(){
            return this.$data.userPath;
        },
        reset(){
            this.$data.userPath = [];
            this.$data.state = 0;
            this.render();
        },
        renderChar() {
            var ctx = this.$refs.canvas.getContext("2d");
            ctx.font = this.$data.width+"px 楷体";
            ctx.textAlign = "center";
            ctx.textBaseline = "middle";
            var measureData = ctx.measureText(this.$props.char);
            //console.log(measureData);
            var rect_x = this.$data.width / 2 - measureData.actualBoundingBoxLeft;
            var rect_y = this.$data.height / 2 - measureData.actualBoundingBoxAscent;
            var rect_w = measureData.actualBoundingBoxRight + measureData.actualBoundingBoxLeft;
            var rect_h = measureData.actualBoundingBoxAscent + measureData.actualBoundingBoxDescent;
            ctx.fillStyle = "black";
            ctx.fillRect(rect_x, rect_y, rect_w, rect_h);
            //console.log(rect_x, rect_y, rect_w, rect_h);
            ctx.fillStyle = "white";
            ctx.fillText(this.$props.char,this.$data.width/2,this.$data.height/2);
            //ctx.fillRect(0, 0, this.$data.width/2, this.$data.height/2);
        },
        renderIncompletedPath() {
            var ctx = this.$refs.canvas.getContext("2d");

            // 绘制实线部分
            ctx.beginPath(); // 开始新的路径
            ctx.strokeStyle = "red";
            ctx.setLineDash([]); // 设置实线样式
            ctx.lineWidth = 2;
            for (let i = 0; i < this.$data.userPath.length; i++) {
                const point = this.$data.userPath[i];
                if (i === 0) {
                    ctx.moveTo(point.x, point.y);
                } else {
                    ctx.lineTo(point.x, point.y);
                }
            }
            ctx.stroke(); // 描边实线部分

            // 绘制虚线封闭部分
            ctx.beginPath(); // 开始新的路径用于绘制虚线
            ctx.setLineDash([10, 5]); // 设置虚线样式
            ctx.strokeStyle = "rgba(200, 0, 0, 0.5)";
            ctx.moveTo(this.$data.userPath[this.$data.userPath.length - 1].x, this.$data.userPath[this.$data.userPath.length - 1].y); // 从路径的最后一个点开始
            ctx.lineTo(this.$data.userPath[0].x, this.$data.userPath[0].y); // 连接到路径的起始点
            ctx.stroke(); // 描边虚线部分
        },
        renderPath(){
            var ctx = this.$refs.canvas.getContext("2d");
            ctx.beginPath();
            ctx.strokeStyle = "red";
            ctx.setLineDash([]); // 设置实线样式
            ctx.lineWidth = 2;
            ctx.moveTo(this.$data.userPath[0].x, this.$data.userPath[0].y);
            for (let i = 1; i < this.$data.userPath.length; i++) {
                const point = this.$data.userPath[i];
                ctx.lineTo(point.x, point.y);
            }
            ctx.closePath();
            ctx.stroke();
        },
        render() {
            var ctx=this.$refs.canvas.getContext("2d");
            ctx.clearRect(0, 0, this.$data.width, this.$data.height);
            this.renderChar();
            if (this.$data.state === 2) {
                this.renderPath();
            } else if (this.$data.state === 1) {
                this.renderIncompletedPath();
            }
        },
        isSupported() {
            return !!document.createElement("canvas").getContext;
        },
        handleMousedown() {
            if (this.$data.state == 0) {
                this.$data.userPath = [];
                this.$data.state = 1;
            }
        },
        handleMouseup() {
            if (this.$data.state == 1) {
                this.$data.state = 2;
                this.render();
            }
        },
        handleMousemove(e) {
            if (this.$data.state == 1) {
                this.$data.userPath.push({ x: e.offsetX, y: e.offsetY });
                //console.log("mousemove", this.$data.userPath);
                this.render();
            }
        },
        handleConfirmBtn() { 
            this.$data.state = 3;
            this.$emit("complete", this.getPath());
        },
        handleResetBtn() { 
            this.reset();
        },
    },
    mounted() {
        //console.log(this.isSupported());
        if (this.isSupported()) {
            //this.$data.char = "你好";
            
            this.renderChar();
        } else {
            throw new Error("浏览器不支持canvas");
        }
    },
};
</script>

<style scoped>
canvas {
    border: 1px solid #000;
}
</style>
