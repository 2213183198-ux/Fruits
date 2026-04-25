import asyncio
import base64
import binascii
import time

from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse

from backend.app.api.presenters import present_prediction
from backend.app.core.errors import AppError
from backend.app.core.runtime import runtime


router = APIRouter(include_in_schema=False)


@router.get("/")
def read_root() -> FileResponse:
    return FileResponse(runtime.get_index_file(), media_type="text/html; charset=utf-8")


@router.get("/api")
def read_api_root() -> dict[str, object]:
    return runtime.get_api_index()


@router.websocket("/ws/webcam")
async def webcam_stream(websocket: WebSocket) -> None:
    await websocket.accept()
    await websocket.send_json(
        {
            "type": "ready",
            "message": "webcam websocket connected",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        }
    )

    try:
        while True:
            message = await websocket.receive_json()
            frame_id = message.get("frame_id")
            message_type = str(message.get("type") or "")

            if message_type == "ping":
                await websocket.send_json({"type": "pong", "frame_id": frame_id})
                continue

            if message_type != "frame":
                await websocket.send_json(
                    {
                        "type": "error",
                        "frame_id": frame_id,
                        "message": "unsupported message type",
                    }
                )
                continue

            image_base64 = str(message.get("image_base64") or "")
            if "," in image_base64:
                image_base64 = image_base64.split(",", 1)[1]

            try:
                frame_bytes = base64.b64decode(image_base64, validate=True)
            except (binascii.Error, ValueError):
                await websocket.send_json(
                    {
                        "type": "error",
                        "frame_id": frame_id,
                        "message": "invalid base64 image payload",
                    }
                )
                continue

            imgsz = int(message.get("imgsz") or runtime.settings.default_image_size)
            conf = float(message.get("conf") or runtime.settings.default_confidence)
            started_at = time.perf_counter()

            try:
                prediction = await asyncio.to_thread(runtime.predict_webcam_frame, frame_bytes, imgsz, conf)
                payload = present_prediction(prediction).model_dump()
                await websocket.send_json(
                    {
                        "type": "prediction",
                        "frame_id": frame_id,
                        "latency_ms": round((time.perf_counter() - started_at) * 1000, 2),
                        "data": payload,
                    }
                )
            except AppError as exc:
                await websocket.send_json(
                    {
                        "type": "error",
                        "frame_id": frame_id,
                        "message": exc.message,
                        "code": exc.code,
                    }
                )
    except WebSocketDisconnect:
        return
