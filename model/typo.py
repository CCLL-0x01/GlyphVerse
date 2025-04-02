from util.worker import EventlessWorker
from util.path import get_model_path
from config import config

import random
from uuid import uuid4

import torch
import numpy as np
from diffusers import StableDiffusionDepth2ImgPipeline
from controlnet_aux import HEDdetector
from PIL import Image
from typing import List

class MaskBeautifier(EventlessWorker):
    '''Suggest beautified mask generated with semtypo
    makesure set self.char_img_uuid, self.mask_img_uuid before call self.worker()'''
    
    def load_models(self):
        self.scribble_preprocess = HEDdetector.from_pretrained(
            pretrained_model_or_path='lllyasviel/Annotators',
            filename='ControlNetHED.pth', 
            # torch_dtype=torch.float16 #TODO:dtype
        ).to(self.device)
        self.d2i=StableDiffusionDepth2ImgPipeline.from_pretrained(
            pretrained_model_name_or_path=self.d2i_name,
            # torch_dtype=torch.float16, #TODO:dtype
            device=self.device,
            local_files_only=True
        ).to(self.device)

    def load_config(self):
        self.device=config['model']['device']
        self.d2i_name=config['model']['name']['sd_depth']
        self.dtype=config['model']['dtype']
        self.gen_num=config['model']['typo']['gen_num']
        self.prompt_template=config['model']['prompts']['typo_prompt_template']
        self.negative_prompt=config['model']['prompts']['negative_prompt']
        self.strength=config['model']['typo']['strength']
        self.guidance_scale=config['model']['typo']['guidance_scale']
        self.positive_prompt=config['model']['prompts']['positive_prompt']

    def load_images(self):
        assert self.char_img_uuid
        assert self.mask_img_uuid
        mask_img=Image.open(f"./temp/{self.mask_img_uuid}.png").convert('L')
        char_img=Image.open(f"./temp/{self.char_img_uuid}.png").convert('L')
        mask_array=np.array(mask_img).astype(np.bool_)
        char_array=np.array(char_img).astype(np.bool_)

        sub_array=np.where(mask_array & char_array, 255,0).astype(np.uint8)
        surr_array=np.where((~mask_array)&char_array, 255,0).astype(np.uint8)
        self.sub_img=Image.fromarray(sub_array).convert('RGB')
        self.surr_img=Image.fromarray(surr_array).convert('RGB')

        assert self.sub_img.size == self.surr_img.size

    def init(self):
        self.load_config()
        self.load_models()
    
    def worker(self,**kwargs):
        self.char_img_uuid=kwargs['char_img_uuid']
        self.mask_img_uuid=kwargs['mask_img_uuid']
        self.sub_prompt=kwargs['sub_prompt']
        self.surr_prompt=kwargs['surr_prompt']
        self.result_img_uuids=kwargs['result_img_uuids']

        self.load_images()

        progress=0
        # surr img
        surr_scribble=self.scribble_preprocess(
            self.surr_img,
            detect_resolution=500, #TODO: allow to customize img size 
            image_resolution=500,
        )
        # surr_scribble.save(f'./temp/{self.surr_result_uuid}.png')
        new_surr_array=np.array(surr_scribble.convert('L').resize((500,500))).astype(np.uint8)
        progress+=1
        self.progress.value+=1

        # sub img 
        W, H = self.sub_img.size
        for result_uuid  in self.result_img_uuids:
            sub_depth=self.d2i(
                prompt= self.prompt_template.format(
                    sub_prompt=self.sub_prompt,
                    positive_prompt=self.positive_prompt
                ),
                image=self.sub_img, 
                guidance_scale=self.guidance_scale,
                height=H,
                width=W,
                negative_prompt=self.negative_prompt, 
                strength=self.strength,
                generator=torch.manual_seed(random.randint(0,1000-1))
            ).images[0]
            # sub_depth.save(f'./temp/{result_uuid}.png')
            new_sub_array=np.array(sub_depth.convert('L').resize((500,500))).astype(np.uint8)
            new_img=Image.fromarray(np.where(new_sub_array> new_surr_array, new_sub_array, new_surr_array)).convert('RGB')
            new_img.save(f'./temp/{result_uuid}.png')
            progress+=1
            self.progress.value=progress
        return progress


