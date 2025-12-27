from fastapi import FastAPI, Request
from core.policy import decide, Signals, Thresholds

app = FastAPI()

@app.post("/decide")
async def decide_endpoint(request: Request):
    payload = await request.json()
    s = Signals(**payload["signals"])
    th = Thresholds(**payload.get("thresholds", {}))
    decision, meta = decide(s, th)
    return {"decision": decision, "meta": meta}
