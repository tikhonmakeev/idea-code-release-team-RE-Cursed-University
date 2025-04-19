import logging
from logging import LoggerAdapter


class WebSocketLoggerAdapter(LoggerAdapter):

    def process(self, msg, kwargs):
        try:
            websocket = kwargs["extra"]["websocket"]
        except KeyError:
            return msg, kwargs
        if websocket.request is None:
            return msg, kwargs

        xff = websocket.request_headers.get("X-Forwarded-For", "no-xff")
        return f"{websocket.id} {xff} {msg}", kwargs


def setup_logging():
    logging.basicConfig(
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        level=logging.INFO,
    )

def get_websocket_logger():
    return WebSocketLoggerAdapter(logging.getLogger("websockets.server"), None)