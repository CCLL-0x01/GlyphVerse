from util.worker import Worker
from util.path import get_model_path
from config import config

import json
import random

import torch
import numpy as np
from torchvision import transforms
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

from PIL import Image

from .controlnets import StableDiffusionControlNetsPipeline
from .DDIMScheduler_L import DDIMScheduler_L #?

class IMGGenerator(Worker):
    '''
    generate img with diffusion
    '''

    def __init__(
            self,
            sub_prompt:str, 
            surr_prompt:str, #comma separate str
            char_img_uuid:str,
            mask_img_uuid:str,
            result_img_uuid:str,
            seed:int=random.sample(range(100000),1)[0],
        ):
        super().__init__()
        self.sub_prompt=sub_prompt
        self.surr_prompt=surr_prompt
        self.char_img_uuid=char_img_uuid
        self.mask_img_uuid=mask_img_uuid
        self.result_img_uuid=result_img_uuid
        self.seed=seed



    def worker(self):
        self.load_config()
        #检查参数
        # assert self.sub_prompt
        # assert self.surr_prompt

        self.prepare_image()
        self.prepare_model()

        #callback
        def step_callback(step: int, timestep: int, latents: torch.FloatTensor):
            self.progress.value=step

        #pipeline
        result_img = self.sd_pipe( #TODO move to config
            prompt = ', '.join(self.surr_prompt),
            image = [self.surr_image],
            height = self.sub_image.size[0], 
            width = self.sub_image.size[1], 
            num_inference_steps = 50,
            guidance_scale = 15, 
            negative_prompt = self.negative_prompt,
            generator = torch.manual_seed(self.seed),
            controlnet_conditioning_scale = [0.97],

            addl_prompts = [self.sub_prompt],
            addl_images = [[self.sub_image] * len(self.controlnet_sub)],
            weights = [0.85],
            masks = [self.mask],
            addl_ctrlnet_conditioning_scale = [1.1],
            callback=step_callback,
            callback_steps=1,
        )
        result_img.images[0].save(f"./temp/{self.result_img_uuid}.png")
    # def on_step(self,fn):
    #     self.callback=fn
    def load_config(self):
        self.device = config["model"]["device"]
        self.dtype=config["model"].get("dtype","float16")
        self.sd_name = config["model"]["name"]["stable_diffusion"]
        self.scr_name= config["model"]["name"]["controlnet_scribble"]
        self.seg_name= config["model"]["name"]["controlnet_scribble"]
        self.positive_prompt=config["model"]["positive_prompt"]
        self.negative_prompt=config["model"]["negative_prompt"]
        
    def prepare_model(self):
        # load control net
        self.controlnet_scribble = ControlNetModel.from_pretrained(
            self.scr_name, 
            # torch_dtype=dtype
        )
        self.controlnet_seg = ControlNetModel.from_pretrained(
            self.seg_name,
            # torch_dtype=dtype
        )
        self.controlnet_sub = [self.controlnet_scribble, self.controlnet_seg]
        self.controlnet_surr = [self.controlnet_scribble]

        #load sd
        self.sd_sub = StableDiffusionControlNetPipeline.from_pretrained(
            self.sd_name,
            controlnet= self.controlnet_sub,
            # torch_dtype=dtype
        ).to(device=self.device)
        self.sd_pipe = StableDiffusionControlNetsPipeline.from_pretrained(
            self.sd_name,
            controlnet= self.controlnet_surr,
            # torch_=dtype
        ).to(device=self.device)
        self.sd_pipe.register_addl_models(self.sd_sub)
        self.sd_pipe.schedule = DDIMScheduler_L.from_config(self.sd_pipe.scheduler.config)
        # sd_pipe.load_lora_weights('./loras', weight_name='pytorch_lora_weights.safetensors')
    def prepare_image(self):
        mask_img=Image.open(f"./temp/{self.mask_img_uuid}.png")
        char_img=Image.open(f"./temp/{self.char_img_uuid}.png")

        
        def calc_sub_surr(mask_im, char_im):
            # 根据mask和char的像素值，计算出sub和surr图像
            mask_pixels=mask_im.load()
            char_pixels=char_im.load()

            sub_im=Image.new("L", mask_im.size)
            sub_pixels=sub_im.load()
            surr_im=Image.new("L", mask_im.size)
            surr_pixels=surr_im.load()
            
            for i in range(sub_im.size[0]):
                for j in range(sub_im.size[1]):
                    mask_r,mask_g,mask_b,mask_a=mask_pixels[i,j]
                    if mask_a == 0:
                        mask_gray=0
                    else:
                        mask_gray=(mask_r+mask_g+mask_b)/3
                        if mask_gray < 128:
                            mask_gray = 0
                        else:
                            mask_gray = 255

                    char_r,char_g,char_b,char_a=char_pixels[i,j]
                    if char_a == 0:
                        char_gray=0
                    else:
                        char_gray=(char_r+char_g+char_b)/3
                        if char_gray < 128:
                            char_gray = 0
                        else:
                            char_gray = 255
                    
                    # sub = mask & char
                    # surr = (~mask) & char

                    if mask_gray==0 and char_gray==0:
                        sub_pixels[i,j]=0
                        surr_pixels[i,j]=0
                    elif mask_gray==0 and char_gray==255:
                        sub_pixels[i,j]=0
                        surr_pixels[i,j]=255
                    elif mask_gray==255 and char_gray==0:
                        sub_pixels[i,j]=0
                        surr_pixels[i,j]=0
                    elif mask_gray==255 and char_gray==255:
                        sub_pixels[i,j]=255
                        surr_pixels[i,j]=0
                    else:
                        print("error")
                        exit(-1)
            
            return sub_im, surr_im

        self.mask=transforms.ToTensor()(mask_img.convert("L")).squeeze().to(self.device)
        self.sub_image, self.surr_image=calc_sub_surr(mask_img, char_img)

        #load image test
        
        # text_name="蔷=rose"
        # with open(f"./test/LLM/{text_name}.json", "r") as f:
        #     text_data = json.load(f)

        # self.sub_prompt = text_data['sub_prompt']
        # self.surr_prompt = text_data['surr_prompt']

        # sub_img_path = "test/CCG/蔷=rose/sub_4.jpg"
        # surr_img_path = "test/CCG/蔷=rose/surr.jpg"

        # sub_img = load_image(sub_img_path)
        # surr_img = load_image(surr_img_path)

        # mask_img_path = "test/CCG/蔷=rose/mask.jpg"
        # self.mask_img = load_image(mask_img_path).convert("L")
        # self.mask = transforms.ToTensor()(self.mask_img).squeeze().to(self.device)

        # self.sub_image = IMGGenerator.resize_image(sub_img, res=128)
        # self.surr_image = IMGGenerator.resize_image(surr_img, res=128)
        # self.seed = random.sample(range(100000),1)[0]

    @staticmethod
    def resize_image(input_image, res=300):
        W, H = input_image.size
        H, W = float(H), float(W)
        H = int(np.round(H / 64.0)) * 64
        W = int(np.round(W / 64.0)) * 64
        if res is None:
            size_ = (W, H)
        else:
            k = res / min(W, H)
            size_ = (int(W * k), int(H * k))

        img_rsz = input_image.resize(size_)
        return img_rsz
