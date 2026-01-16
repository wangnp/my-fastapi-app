from fastapi import FastAPI
import apixx
from pydantic import BaseModel
from response import Response

app = FastAPI()

@app.get("/")
def hello_world():
    return {"message": "Hello from FastAPI on Vercel!"}


# --- 数据模型 (JSON) ---
class SearchItem(BaseModel):
    keyword: str
    page: int


# --- 接口 1: 处理 JSON 格式 ---
@app.post("/search")
async def search(item: SearchItem):
    print(f"收到 JSON 数据: {item}")
    result = apixx.feishu_search(item.keyword, item.page)
    return Response.success(data=result)

#
# # --- 启动入口 ---
# if __name__ == "__main__":
#     import uvicorn
#     print("服务启动中...")
#     uvicorn.run(app, host="0.0.0.0", port=8000)