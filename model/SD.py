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
            config['model']['name']['controlnet_scribble'], 
            local_files_only=True
            # torch_dtype=dtype
        )
        self.controlnet_seg = ControlNetModel.from_pretrained(
            config['model']['name']['controlnet_seg'],
            local_files_only=True
            # torch_dtype=dtype
        )
        self.controlnet_sub = [self.controlnet_scribble, self.controlnet_seg]
        self.controlnet_surr = [self.controlnet_scribble]

        #load sd
        self.sd_sub = StableDiffusionControlNetPipeline.from_pretrained(
            config['model']['name']['stable_diffusion'],
            controlnet= self.controlnet_sub,
            local_files_only=True
            # torch_dtype=dtype
        ).to('cpu')
        self.sd_pipe = StableDiffusionControlNetsPipeline.from_pretrained(
            config['model']['name']['stable_diffusion'],
            controlnet= self.controlnet_surr,
            local_files_only=True
            # torch_=dtype
        ).to('cpu')
        self.sd_pipe.register_addl_models(self.sd_sub)
        self.sd_pipe.schedule = DDIMScheduler_L.from_config(self.sd_pipe.scheduler.config)

    def prepare_image(self):
        mask_img=Image.open(f"./temp/{self.mask_img_uuid}.png")
        beautified_img=Image.open(f"./temp/{self.beautified_mask_uuid}.png")

        
        def calc_sub_surr(mask_im:Image, char_im:Image):
            # 根据mask和char的像素值，计算出sub和surr图像
            binarized_mask_im=np.array(mask_im.convert('L').point(lambda p: 255 if p > 128 else 0))
            binarized_char_im=np.array(char_im.convert('L').point(lambda p: 255 if p > 128 else 0))
            sub = binarized_mask_im & binarized_char_im
            surr = (~binarized_mask_im) & binarized_char_im
            return Image.fromarray(sub), Image.fromarray(surr)


        self.mask=transforms.ToTensor()(mask_img.convert("L")).squeeze().to(config['model']['device'])
        self.sub_image, self.surr_image=calc_sub_surr(mask_img, beautified_img)


    def init(self):
        # self.load_config()
        self.prepare_model()

    def worker(self, **kwargs):
        self.sub_prompt=kwargs.get('sub_prompt')
        self.surr_prompt=kwargs.get('surr_prompt')
        self.char_img_uuid=kwargs.get('char_img_uuid')
        self.mask_img_uuid=kwargs.get('mask_img_uuid')
        self.result_img_uuid=kwargs.get('result_img_uuid')
        self.beautified_mask_uuid=kwargs.get('beautified_mask_uuid')
        self.seed=kwargs.get('seed')
        self.lora=kwargs.get('lora')

        assert self.sub_prompt, f"found sub_prompt {self.sub_prompt}"
        assert self.surr_prompt, f"found surr_prompt {self.surr_prompt}"
        assert self.char_img_uuid, f"found char_img_uuid {self.char_img_uuid}"
        assert self.mask_img_uuid, f"found mask_img_uuid {self.mask_img_uuid}"
        assert self.result_img_uuid, f"found result_img_uuid {self.result_img_uuid}"
        assert self.beautified_mask_uuid, f"found beautified_mask_uuid {self.beautified_mask_uuid}"
        
        if not self.seed:
            self.seed=random.sample(range(100000),1)[0]
        if self.lora:
            try:
                self.sd_pipe.load_lora_weights(self.lora_path, weight_name=self.lora)
            except Exception as e:
                warnings.warn(f"Error loading lora, lora will be ignored. Error: {str(e)}")
        else:
            self.sd_pipe.unload_lora_weights()
        
        self.sd_pipe.to(config['model']['device'])
        self.sd_sub.to(config['model']['device'])
        self.prepare_image()

        def step_callback(step: int, timestep: int, latents: torch.FloatTensor):
            self.progress.value=step

        result_img = self.sd_pipe( 
            prompt = config['model']['SD']['prompt_template'].format(
                sub_prompt=self.sub_prompt,
                surr_prompts=', '.join(self.surr_prompt),
                positive_prompt=config['model']['SD']['positive_prompt'],
                negative_prompt=config['model']['SD']['negative_prompt'],
            ),
            image = [self.surr_image],
            height = self.sub_image.size[0], 
            width = self.sub_image.size[1], 
            num_inference_steps = config['model']['SD']['num_inference_steps'],
            guidance_scale = config['model']['SD']['guidance_scale'],
            negative_prompt = config['model']['SD']['negative_prompt'],
            generator = torch.manual_seed(self.seed),
            controlnet_conditioning_scale = [config['model']['SD']['controlnet_conditioning_scale']],

            addl_prompts = [self.sub_prompt],
            addl_images = [[self.sub_image] * len(self.controlnet_sub)],
            weights = [config['model']['SD']['weights']], 
            masks = [self.mask],
            addl_ctrlnet_conditioning_scale = [config['model']['SD']['addl_controlnet_conditioning_scale']],

            callback=step_callback,
            callback_steps=config['model']['SD']['callback_steps'],
        )
        result_img.images[0].save(f"./temp/{self.result_img_uuid}.png")

        self.sd_pipe.to('cpu')
        self.sd_sub.to('cpu')
        torch.cuda.empty_cache()
        return config['model']['SD']['num_inference_steps']