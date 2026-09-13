import uuid
from datetime import datetime, timezone
from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from pypinyin import lazy_pinyin, Style
from snownlp import SnowNLP
from storage import init_db, save_record, get_history 
from fastapi import Request, Response
  

app = FastAPI()

init_db() # 初始化数据库

 # → 添加CORS授权
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # → 允许的源
    allow_methods=["GET", "POST"],# → 允许的方法
    allow_credentials=True,  
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


def get_session_id(request: Request, response: Response) -> str:
    sid = request.cookies.get("session_id")      # 先看有没有纸条
    if not sid:                                  # 第一次来，没有——发一张
        sid = uuid.uuid4().hex                    # 一串随机、不重复的 id
        response.set_cookie(
            "session_id", sid,
            httponly=True, samesite="lax",
            max_age=60 * 60 * 24 * 30,            # 记 30 天
        )
    return sid

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
def analyze(req: AnalyzeRequest, request: Request, response: Response):
    sid = get_session_id(request, response)
    text = req.text
    score = round(SnowNLP(text).sentiments, 2)
    result = {
        "text": text,
        "score": score,
        "label": get_sentiment(score)["label"],
        "pinyin": " ".join(lazy_pinyin(text, style=Style.TONE)),
        "created_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
    }
    save_record(sid, result)          # 存的时候盖上这个会话的记号
    return result                     # ← 返回体一个字没变，session_id 只走 cookie

@app.get("/api/history")
def history(request: Request, response: Response, limit: int = 10):
    sid = get_session_id(request, response)
    return get_history(sid, limit)    # 只回这个会话自己的
