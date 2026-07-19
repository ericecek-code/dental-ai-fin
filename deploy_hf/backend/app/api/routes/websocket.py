from fastapi import APIRouter, WebSocket
import json

router = APIRouter(tags=["websocket"])


@router.websocket("/ws/status/{job_id}")
async def job_status(websocket: WebSocket, job_id: str):
    await websocket.accept()
    await websocket.send_json({"job_id": job_id, "status": "queued"})
    await websocket.close()
