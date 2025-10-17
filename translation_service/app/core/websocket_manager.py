from typing import Dict, Set, List
from fastapi import WebSocket
import json
import asyncio
import logging

logger = logging.getLogger(__name__)
CHUNK_SIZE2 = 1024 * 1024  # 1MB chunks

class WebSocketManager:
    def __init__(self):
        # Store active connections by upload_id
        self.active_connections: Dict[str, Dict[str, Set[WebSocket]]] = {
            "upload": {},  # upload_id -> set of WebSockets for file upload
            "logs": {}  # upload_id -> set of WebSockets for logs
        }
        # Store upload session data
        self.upload_sessions: Dict[str, Dict] = {}

    async def connect(self, websocket: WebSocket, upload_id: str, connection_type: str):
        await websocket.accept()
        if upload_id not in self.active_connections[connection_type]:
            self.active_connections[connection_type][upload_id] = set()
        self.active_connections[connection_type][upload_id].add(websocket)
        logger.info(f"WebSocket connected for upload_id: {upload_id}, type: {connection_type}")

    def disconnect(self, websocket: WebSocket, upload_id: str, connection_type: str):
        if upload_id in self.active_connections[connection_type]:
            self.active_connections[connection_type][upload_id].discard(websocket)
            if not self.active_connections[connection_type][upload_id]:
                del self.active_connections[connection_type][upload_id]
        logger.info(f"WebSocket disconnected for upload_id: {upload_id}, type: {connection_type}")

    async def send_personal_message(self, message: str, websocket: WebSocket):
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending message to WebSocket: {e}")

    async def broadcast_to_type(self, message: str, upload_id: str, connection_type: str):
        if upload_id in self.active_connections[connection_type]:
            disconnected = set()
            for connection in self.active_connections[connection_type][upload_id].copy():
                try:
                    await connection.send_text(message)
                except Exception as e:
                    logger.error(f"Error broadcasting to WebSocket: {e}")
                    disconnected.add(connection)

            # Clean up disconnected connections
            for conn in disconnected:
                self.disconnect(conn, upload_id, connection_type)

    async def send_json_to_type(self, data: dict, upload_id: str, connection_type: str):
        message = json.dumps(data)
        await self.broadcast_to_type(message, upload_id, connection_type)

    def is_upload_socket_connected(self, upload_id: str) -> bool:
        return upload_id in self.active_connections["upload"] and len(self.active_connections["upload"][upload_id]) > 0

    def is_logs_socket_connected(self, upload_id: str) -> bool:
        return upload_id in self.active_connections["logs"] and len(self.active_connections["logs"][upload_id]) > 0

    def create_upload_session(self, upload_id: str, project_id: int, user_id: int, file_size: int):
        self.upload_sessions[upload_id] = {
            "project_id": project_id,
            "user_id": user_id,
            "file_size": file_size,
            "bytes_received": 0,
            "progress": 0,
            "status": "initialized",
            "file_path": None,
            "file_extension": None
        }

    def update_upload_progress(self, upload_id: str, bytes_received: int):
        if upload_id in self.upload_sessions:
            session = self.upload_sessions[upload_id]
            session["bytes_received"] = bytes_received
            if session["file_size"] > 0:
                session["progress"] = min(100, int((bytes_received / (session["file_size"] * CHUNK_SIZE2)) * 100))
            return session
        return None

    def get_upload_session(self, upload_id: str):
        return self.upload_sessions.get(upload_id)

    def complete_upload_session(self, upload_id: str, file_path: str):
        if upload_id in self.upload_sessions:
            self.upload_sessions[upload_id]["status"] = "completed"
            self.upload_sessions[upload_id]["progress"] = 100
            self.upload_sessions[upload_id]["file_path"] = file_path
            return self.upload_sessions[upload_id]
        return None

    def remove_upload_session(self, upload_id: str):
        if upload_id in self.upload_sessions:
            del self.upload_sessions[upload_id]


# Create a singleton instance
manager = WebSocketManager()