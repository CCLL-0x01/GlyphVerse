from util.worker import EventlessWorker
from util.path import get_model_path
from config import config
import warnings
import json
import random

import torch
import numpy as np
from torchvision import transforms
from diffusers import StableDiffusionControlNetPipeline, ControlNetModel

from PIL import Image

from .controlnets import StableDiffusionControlNetsPipeline
from .DDIMScheduler_L import DDIMScheduler_L


class IMGGenerator(EventlessWorker):
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
        ).to('cpu')
        self.sd_pipe = StableDiffusionControlNetsPipeline.from_pretrained(
            self.sd_name,
            controlnet= self.controlnet_surr,
            # torch_=dtype
        ).to('cpu')
        self.sd_pipe.register_addl_models(self.sd_sub)
        self.sd_pipe.schedule = DDIMScheduler_L.from_config(self.sd_pipe.scheduler.config)

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

    def load_config(self):
        self.device = config["model"]["device"]
        self.dtype=config["model"].get("dtype","float16")
        self.sd_name = config["model"]["name"]["stable_diffusion"]
        self.scr_name= config["model"]["name"]["controlnet_scribble"]
        self.seg_name= config["model"]["name"]["controlnet_scribble"]
        self.positive_prompt=config["model"]["prompts"]["positive_prompt"]
        self.negative_prompt=config["model"]["prompts"]["negative_prompt"]
        self.num_inference_steps=config["model"]["inference"]["num_inference_steps"]
        self.guidance_scale=config["model"]["inference"]["guidance_scale"]
        self.controlnet_conditioning_scale=config["model"]["inference"]["controlnet_conditioning_scale"]
        self.weights=config["model"]["inference"]["weights"]
        self.addl_controlnet_conditioning_scale=config["model"]["inference"]["addl_controlnet_conditioning_scale"]
        self.callback_steps=config["model"]["inference"]["callback_steps"]
        self.lora_path=config["lora"]["path"]

    def init(self):
        self.load_config()
        self.prepare_model()

    def worker(self, **kwargs):
        self.sub_prompt=kwargs.get('sub_prompt')
        self.surr_prompt=kwargs.get('surr_prompt')
        self.char_img_uuid=kwargs.get('char_img_uuid')
        self.mask_img_uuid=kwargs.get('mask_img_uuid')
        self.result_img_uuid=kwargs.get('result_img_uuid')
        self.seed=kwargs.get('seed')
        self.lora=kwargs.get('lora')

        assert self.sub_prompt, f"found sub_prompt {self.sub_prompt}"
        assert self.surr_prompt, f"found surr_prompt {self.surr_prompt}"
        assert self.char_img_uuid, f"found char_img_uuid {self.char_img_uuid}"
        assert self.mask_img_uuid, f"found mask_img_uuid {self.mask_img_uuid}"
        assert self.result_img_uuid, f"found result_img_uuid {self.result_img_uuid}"
        if not self.seed:
            self.seed=random.sample(range(100000),1)[0]
        if self.lora:
            try:
                self.sd_pipe.load_lora_weights(self.lora_path, weight_name=self.lora)
            except Exception as e:
                warnings.warn(f"Error loading lora, lora will be ignored. Error: {str(e)}")
        else:
            self.sd_pipe.unload_lora_weights()
        
        self.sd_pipe.to(self.device)
        self.sd_sub.to(self.device)
        self.prepare_image()

        def step_callback(step: int, timestep: int, latents: torch.FloatTensor):
            self.progress.value=step

        result_img = self.sd_pipe( 
            prompt = ', '.join(self.surr_prompt)+', '+self.positive_prompt,
            image = [self.surr_image],
            height = self.sub_image.size[0], 
            width = self.sub_image.size[1], 
            num_inference_steps = self.num_inference_steps,
            guidance_scale = self.guidance_scale,
            negative_prompt = self.negative_prompt,
            generator = torch.manual_seed(self.seed),
            controlnet_conditioning_scale = [self.controlnet_conditioning_scale],

            addl_prompts = [self.sub_prompt],
            addl_images = [[self.sub_image] * len(self.controlnet_sub)],
            weights = [self.weights], 
            masks = [self.mask],
            addl_ctrlnet_conditioning_scale = [self.addl_controlnet_conditioning_scale],

            callback=step_callback,
            callback_steps=self.callback_steps,
        )
        result_img.images[0].save(f"./temp/{self.result_img_uuid}.png")

        self.sd_pipe.to('cpu')
        self.sd_sub.to('cpu')
        torch.cuda.empty_cache()
        return self.num_inference_steps