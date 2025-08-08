##
##    Access the LLM from UI
##

from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from agent_manager import AgentManager

app = FastAPI()

@app.get("/", response_class=HTMLResponse)
def homepage():
    with open("index.html") as f:
        return HTMLResponse(content=f.read())

class AnalyzeRequest(BaseModel):
    text: str

@app.post("/analyze")
async def analyze(data: AnalyzeRequest):
    try:
        manager = AgentManager(data.text)
        result = await manager.run()
        return JSONResponse(content=result)
    except Exception as e:
        return JSONResponse(status_code=500, content={"error": str(e)})
