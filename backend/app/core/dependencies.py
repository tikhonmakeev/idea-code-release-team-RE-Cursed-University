from app.routers.websockets.connectionManager import ConnectionManager

# Синглтон
_connection_manager = ConnectionManager()

def get_connection_manager_singleton() -> ConnectionManager:
    return _connection_manager
