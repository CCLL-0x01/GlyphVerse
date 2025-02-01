import os

def get_model_path(directory):
    safetensors_files = [f for f in os.listdir(directory) if f.endswith('.safetensors')]
    
    if len(safetensors_files) == 1:
        return os.path.join(directory, safetensors_files[0])
    elif len(safetensors_files) == 0:
        raise FileNotFoundError("No .safetensors file found in the directory.")
    else:
        raise FileExistsError("Multiple .safetensors files found in the directory.")

# 示例用法
if __name__ == "__main__":
    directory = "./test"
    try:
        file_path = get_model_path(directory)
        print(f"Found .safetensors file: {file_path}")
    except (FileNotFoundError, FileExistsError) as e:
        print(e)
