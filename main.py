from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import pandas as pd

app = FastAPI()

# 前端页面
templates = Jinja2Templates(directory="templates")

# 👉 用内存存数据（替代 CSV 文件）
data_store = []

# 首页（网页）
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(
    request=request,
    name="index.html",
    context={}
)

# 上传数据（设备 / 本地电脑）
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    try:
        df = pd.read_csv(file.file)

        # 转成字典
        records = df.to_dict(orient="records")

        # 加入全局数据
        data_store.extend(records)

        return {
            "status": "uploaded",
            "received_rows": len(records),
            "total_rows": len(data_store)
        }

    except Exception as e:
        return {"status": "error", "message": str(e)}

# 获取数据（前端用）
@app.get("/data")
def get_data():
    # 返回最新50条
    return data_store[-50:]
