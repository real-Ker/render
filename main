from fastapi import FastAPI, UploadFile, File
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.requests import Request
import pandas as pd
import os

app = FastAPI()

# 模板（前端页面）
templates = Jinja2Templates(directory="templates")

DATA_FILE = "data.csv"

# 首页（可视化界面）
@app.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

# 上传数据（设备 / 本地电脑用）
@app.post("/upload")
async def upload(file: UploadFile = File(...)):
    df = pd.read_csv(file.file)

    if os.path.exists(DATA_FILE):
        df.to_csv(DATA_FILE, mode="a", header=False, index=False)
    else:
        df.to_csv(DATA_FILE, index=False)

    return {"status": "uploaded"}

# 获取数据（前端用）
@app.get("/data")
def get_data():
    if not os.path.exists(DATA_FILE):
        return []

    df = pd.read_csv(DATA_FILE)
    return df.tail(50).to_dict(orient="records")