import hashlib
import time
import xml.etree.ElementTree as ET
from fastapi import FastAPI, Request, Query
from fastapi.responses import PlainTextResponse
from sentence_transformers import SentenceTransformer, util
from pathlib import Path
import pandas as pd
import torch

# === 企业微信配置 ===
TOKEN = "uUQFucKbdMjnsNSKBmqflwJzPI9"  # 企业微信后台自定义的 Token
ENCODING_AES_KEY = "dlyajhhsRWz4akQZj0iqTxK4FnuDeyNelCYujUqM68G"  # 可留空，如果是明文模式
CORP_ID = "ww5614ccf1c02e6d99"  # 企业 ID


# === 初始化 FastAPI 应用 ===
app = FastAPI()

# === 加载模型和 QA 数据 ===
current_dir = Path(__file__).parent
model_path = current_dir / "model" / "text2vec-base-chinese"
qa_file_path = current_dir / "QAs.xlsx"

model = SentenceTransformer(str(model_path))

def load_qa():
    df = pd.read_excel(qa_file_path)
    if 'Question' not in df.columns or 'Answer' not in df.columns:
        raise ValueError("Excel 必须包含 'Question' 和 'Answer' 列")
    questions = df['Question'].astype(str).tolist()
    answers = df['Answer'].astype(str).tolist()
    embeddings = model.encode(questions, convert_to_tensor=True)
    return questions, answers, embeddings

questions, answers, question_embeddings = load_qa()

# === 问答检索逻辑 ===
def search_qa(query: str, top_n: int = 5) -> str:
    query_embedding = model.encode(query, convert_to_tensor=True)
    similarities = util.cos_sim(query_embedding, question_embeddings)[0]
    top_indices = similarities.argsort(descending=True)[:top_n]

    results = [
        {
            'Question': questions[idx],
            'Answer': answers[idx],
            'Similarity': similarities[idx].item()
        }
        for idx in top_indices
    ]

    # Debug: Print results to verify structure
    print("Debug: Results structure:", results)
    return results

# === 企业微信：GET 验证 URL ===
@app.get("/wechat")
def wechat_verify(
    signature: str = Query(...),
    timestamp: str = Query(...),
    nonce: str = Query(...),
    echostr: str = Query(...)
):
    tmp_list = sorted([TOKEN, timestamp, nonce])
    tmp_str = ''.join(tmp_list)
    hashcode = hashlib.sha1(tmp_str.encode('utf-8')).hexdigest()
    if hashcode == signature:
        return PlainTextResponse(content=echostr)
    return PlainTextResponse(content="Invalid signature", status_code=403)

# === 企业微信：POST 消息接口 ===
@app.post("/wechat")
async def wechat_message(request: Request):
    body = await request.body()
    xml_data = ET.fromstring(body.decode())

    content = xml_data.find("Content").text
    from_user = xml_data.find("FromUserName").text
    to_user = xml_data.find("ToUserName").text

    reply_text = search_qa(content)

    now = int(time.time())
    response = f"""
    <xml>
        <ToUserName><![CDATA[{from_user}]]></ToUserName>
        <FromUserName><![CDATA[{to_user}]]></FromUserName>
        <CreateTime>{now}</CreateTime>
        <MsgType><![CDATA[text]]></MsgType>
        <Content><![CDATA[{reply_text}]]></Content>
    </xml>
    """
    return PlainTextResponse(content=response.strip(), media_type="application/xml")

# === 本地调试接口 ===
@app.get("/ask")
def ask(query: str, top_n: int = 5):
    result = search_qa(query, top_n)
    return result

# === 本地启动 ===
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
