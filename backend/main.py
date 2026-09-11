
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pypinyin import lazy_pinyin, Style
from snownlp import SnowNLP
from storage import init_db, save_record, get_history 

  

app = FastAPI()

init_db() # 初始化数据库

 # → 添加CORS授权
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # → 允许的源
    allow_methods=["GET", "POST"],# → 允许的方法
)



profile = {
    "heroTitle": "关于我",  # → 临时加的标记，验证完删掉
    "heroSubtitle": "项目，创意，灵感，心得，我的作品",
    "featuredWork": {
        "kicker": "作品",
        "title": "文字实验室",
        "copy": "拼音和情绪，挖掘中文里的细节",
        "linkLabel": "打开作品",
    },
    "identity": {
        "motto": "已识乾坤大，尤怜草木青",
        "learning": "零到全栈",
    },
}



class AnalyzeRequest(BaseModel):
    text: str

def get_sentiment(score: float):
    # 阈值列表，从高到低排序
    rules = [
        (0.9, "极度积极"),
        (0.75, "很积极"),
        (0.6, "偏积极"),
        (0.4, "中性"),
        (0.25, "偏消极"),
        (0.1, "很消极"),
    ]
    label = "极度消极"
    for threshold, text in rules:
        if score >= threshold:
            label = text
            break
    return {"score": score, "label": label}


@app.get("/api/profile")
def get_profile():
    return profile

@app.post("/api/analyze")
def analyze(req: AnalyzeRequest):
    text = req.text
    score = round(SnowNLP(text).sentiments, 2)
    result = {
        "text": text,
        "score": score,
        "label": get_sentiment(score)["label"],
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),  # ← 新增
    }
    save_record(result)                                                          # ← 存档到文件
    return result


@app.get("/api/history")
def history():
    return get_history(10)                                                         # ← 获取历史记录并返回
