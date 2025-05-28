import pandas as pd
from fastapi import FastAPI
from sentence_transformers import SentenceTransformer, util
from pathlib import Path

# 预加载模型和数据
current_dir = Path(__file__).parent
model_path = current_dir / "model" / "text2vec-base-chinese"
#QAfile_path = current_dir / "qa_chinese_optimized.xlsx"
QAfile_path = current_dir / "QAs.xlsx"


# 加载模型
model = SentenceTransformer(str(model_path))

# 读取Excel文件
try:
    df = pd.read_excel(QAfile_path)
    if 'Question' not in df.columns or 'Answer' not in df.columns:
        raise ValueError("XLSX must contain 'Question' and 'Answer' columns")
    questions = df['Question'].tolist()
    answers = df['Answer'].tolist()
except Exception as e:
    raise ValueError(f"Error reading XLSX: {str(e)}")

app = FastAPI()


@app.get("/ask")
async def ask_question(query: str, top_n: int = 5):
    # 编码查询和问题
    query_embedding = model.encode(query, convert_to_tensor=True)
    question_embeddings = model.encode(questions, convert_to_tensor=True)

    # 计算余弦相似度
    similarities = util.cos_sim(query_embedding, question_embeddings)[0]

    # 获取最相似的top_n个索引和分数
    top_indices = similarities.argsort(descending=True)[:top_n]

    results = [
        {
            'Question': questions[idx],
            'Answer': answers[idx],
            'Similarity': similarities[idx].item()
        }
        for idx in top_indices
    ]

    return {"results": results}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000) 
