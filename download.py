from sentence_transformers import SentenceTransformer
from pathlib import Path
import os

# 设置目标路径
current_dir = Path.cwd()
cache_dir = current_dir / "model" / "shibing624_text2vec_base_chinese"
os.makedirs(cache_dir, exist_ok=True)

# 下载并加载模型，指定缓存路径
model = SentenceTransformer("shibing624/text2vec-base-chinese", cache_folder=cache_dir)
print(f"模型已下载并保存到：{cache_dir}")
