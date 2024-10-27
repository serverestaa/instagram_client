from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Depends, HTTPException, status
from sqlalchemy.orm import Session

from auth.oauth2 import get_current_user, get_websocket_user
from db.database import get_db
from db.db_chat import get_private_chat, create_private_chat, save_message, fetch_chat_messages
from typing import List

from db.models import Chat, ChatParticipant, DbUser

router = APIRouter(prefix="/chat", tags=["chat"])


class ConnectionManager:
    def __init__(self):
        self.active_connections: dict[int, List[WebSocket]] = {}

    async def connect(self, websocket: WebSocket, chat_id: int):
        await websocket.accept()
        if chat_id not in self.active_connections:
            self.active_connections[chat_id] = []
        self.active_connections[chat_id].append(websocket)

    def disconnect(self, websocket: WebSocket, chat_id: int):
        if chat_id in self.active_connections:
            self.active_connections[chat_id].remove(websocket)
            if not self.active_connections[chat_id]:
                del self.active_connections[chat_id]

    async def broadcast(self, message: str, chat_id: int):
        if chat_id in self.active_connections:
            for connection in self.active_connections[chat_id]:
                await connection.send_text(message)


manager = ConnectionManager()


@router.websocket("/ws/{other_user_id}")
async def private_chat(websocket: WebSocket, other_user_id: int, db: Session = Depends(get_db),
                       current_user=Depends(get_websocket_user)):
    chat = get_private_chat(db, user1_id=current_user.id, user2_id=other_user_id)
    chat_id = chat.id if chat else None

    if chat:
        await manager.connect(websocket, chat_id)
    try:
        while True:
            data = await websocket.receive_text()
            if not chat:
                chat = create_private_chat(db, user1_id=current_user.id, user2_id=other_user_id)
                chat_id = chat.id
                await manager.connect(websocket, chat_id)
            message = save_message(db, chat_id=chat_id, user_id=current_user.id, content=data)
            await manager.broadcast(f"{message.user.username}: {message.content}", chat_id)
    except WebSocketDisconnect:
        if chat_id:
            manager.disconnect(websocket, chat_id)
            await manager.broadcast("A user has disconnected.", chat_id)


@router.get("/user_chats")
def get_user_chats(db: Session = Depends(get_db), current_user: DbUser = Depends(get_current_user)):
    chats = (
        db.query(Chat)
        .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
        .filter(ChatParticipant.user_id == current_user.id)
        .all()
    )
    return [
        {
            "chat_id": chat.id,
            "name": chat.name,
            "participant_count": len(chat.participants)
        }
        for chat in chats
    ]


@router.get("/{chat_id}/messages")
def get_chat_messages(chat_id: int, db: Session = Depends(get_db), current_user: DbUser = Depends(get_current_user),
                      limit: int = 20, offset: int = 0):
    chat_participant = db.query(ChatParticipant).filter_by(chat_id=chat_id, user_id=current_user.id).first()
    if not chat_participant:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Not authorized to view this chat.")

    messages = fetch_chat_messages(db, chat_id=chat_id, limit=limit, offset=offset)
    return [{"user_id": msg.user_id, "content": msg.content, "timestamp": msg.timestamp} for msg in messages]
