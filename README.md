# GlyphVerse

## Installation

### 1. Conda Environment
```bash
conda create -n glyph_verse python=3.8.20
conda activate glyph_verse
```

### 2. Python Dependencies
```bash
cd GlyphVerse
pip install -r requirements.txt
```
### 3. Download Pre-trained Models
```bash
cd model/model_weights
git clone https://huggingface.co/runwayml/stable-diffusion-v1-5
git clone https://huggingface.co/lllyasviel/sd-controlnet-depth
git clone https://huggingface.co/lllyasviel/sd-controlnet-scribble
git clone https://huggingface.co/lllyasviel/sd-controlnet-seg
```

### 4. Build Web UI
Make sure that [`Node.js`](https://nodejs.org/) has been installed on your system.
```bash
cd web
npm install
npm run build
```

### 5. Launch
```bash
cd ..
python main.py
```