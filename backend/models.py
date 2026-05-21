from sqlalchemy import Column, String, BigInteger, Text, DateTime, Boolean, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, SmallInteger, ARRAY, Float, Index
from database import Base
import datetime

# All ids are hashed

class Users(Base):
    __tablename__ = "users"

    user_id = Column(String(64), primary_key=True)
 
    username = Column(String, nullable=False)
    picture = Column(String, nullable=True)

class User_Server(Base):
    __tablename__ = "user_server"

    user_id = Column(String(64))
    server_id = Column(String(64))

    server_username = Column(String, nullable=True)
    server_picture = Column(String, nullable=True)
    latest_message_id = Column(BigInteger, nullable=True)

    __table_args__ = (
        PrimaryKeyConstraint('user_id', 'server_id'),
    )

class Servers(Base):
    __tablename__ = "servers"

    server_id = Column(String(64), primary_key=True)
    name = Column(String, nullable=False)
    picture = Column(String, nullable=True)


class Messages(Base):
    __tablename__ = "messages"

    message_id = Column(String(64), primary_key=True)
    text_content = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(String(64), nullable=False)
    server_id = Column(String(64), nullable=False)
    
    # message_id to which the message responds
    responds_to = Column(String(64), nullable=True)
    is_processed = Column(Boolean, default=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'server_id'],                # this table's columns
            ['users.user_id', 'servers.server_id'],    # dest cols
            ondelete="CASCADE"
        ),
    )


class MultimediaContent(Base):
    __tablename__ = "multimedia_content"

    message_id = Column(String(64), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False)
    index = Column(SmallInteger, nullable=False)

    type = Column(String, nullable=False)        # "image", "gif", "video"
    embedding = Column(ARRAY(Float), nullable=True)
    ocr_text = Column(Text, nullable=True)

    # Composite PK
    __table_args__ = (
        PrimaryKeyConstraint('message_id', 'index'),
    )


class Mentions(Base):
    __tablename__ = "mentions"

    message_id = Column(String(64), ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), nullable=False) # Mentioned user's id

    # Composite PK
    __table_args__ = (
        PrimaryKeyConstraint('message_id', 'user_id'),
    )

# Indexes
messages_processed_index = Index('processed', Messages.is_processed)
messages_server_index = Index('server', Messages.server_id)