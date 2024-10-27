from datetime import datetime
from sqlalchemy.orm import Session
from db.models import Chat, ChatParticipant, Message


def get_private_chat(db: Session, user1_id: int, user2_id: int):
    return (
        db.query(Chat)
        .join(ChatParticipant, Chat.id == ChatParticipant.chat_id)
        .filter(
            Chat.is_private == True,
            ChatParticipant.user_id.in_([user1_id, user2_id]),
        )
        .group_by(Chat.id)
        .having(db.func.count(ChatParticipant.user_id) == 2)  # Проверка, что чат содержит двух участников
        .first()
    )


def create_private_chat(db: Session, user1_id: int, user2_id: int):
    chat = Chat(is_private=True)
    db.add(chat)
    db.commit()
    db.refresh(chat)

    db.add(ChatParticipant(chat_id=chat.id, user_id=user1_id))
    db.add(ChatParticipant(chat_id=chat.id, user_id=user2_id))
    db.commit()

    return chat


def save_message(db: Session, chat_id: int, user_id: int, content: str):
    message = Message(chat_id=chat_id, user_id=user_id, content=content, timestamp=datetime.utcnow())
    db.add(message)
    db.commit()
    db.refresh(message)
    return message


def fetch_chat_messages(db: Session, chat_id: int, limit: int = 20, offset: int = 0):
    return (
        db.query(Message)
        .filter(Message.chat_id == chat_id)
        .order_by(Message.timestamp)
        .offset(offset)
        .limit(limit)
        .all()
    )
