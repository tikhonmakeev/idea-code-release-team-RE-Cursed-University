from fastapi import APIRouter, WebSocket, Depends, WebSocketDisconnect
from app.core.dependencies import get_connection_manager_singleton
from app.core.logger import get_websocket_logger

router = APIRouter(prefix="/ws")
ws_logger = get_websocket_logger()

@router.websocket("/ws/{client_id}")
async def websocket_endpoint(websocket: WebSocket, client_id: int, manager: Depends(get_connection_manager_singleton)):
    await manager.connect(websocket)
    ws_logger.info(f"Client #{client_id} connected", extra={"websocket": websocket})

    try:
        while True:
            data = await websocket.receive_text()
            # В логи первые 100 символов
            ws_logger.info(f"Received message from client #{client_id}: {data[:100]}", extra={"websocket": websocket})

            # TODO: бизнес - логика
            await manager.send_personal_message(f"You wrote: {data}", websocket)
    except WebSocketDisconnect as e:
        ws_logger.info(f"Client #{client_id} disconnected: {str(e)}", extra={"websocket": websocket})

        manager.disconnect(websocket)

    except Exception as e:
        ws_logger.error(f"Error with client #{client_id}: {str(e)}",
                       extra={"websocket": websocket}, exc_info=True)
        try:
            await websocket.close(code=1011, reason="Server error")
        except:
            pass
        finally:
            manager.disconnect(websocket)
