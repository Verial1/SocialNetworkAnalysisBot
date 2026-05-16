from sqlalchemy import Column, String, BigInteger, Text, DateTime, Boolean, ForeignKey, PrimaryKeyConstraint, ForeignKeyConstraint, SmallInteger, ARRAY, Float
from .database import Base
import datetime

# All ids are hash

class Users(Base):
    __tablename__ = "users"

    user_id = Column(String(64), nullable=False)
    server_id = Column(String(64), ForeignKey("servers.server_id", ondelete="CASCADE"), nullable=False)
    
    server_username = Column(String, nullable=False)
    server_picture = Column(String, nullable=True)

    # Composite PK
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

    message_id = Column(BigInteger, primary_key=True)
    text_content = Column(Text, nullable=True)
    date = Column(DateTime, default=datetime.datetime.now)
    user_id = Column(String(64), nullable=False)
    server_id = Column(String(64), ForeignKey("servers.server_id", ondelete="CASCADE"), nullable=False)
    
    # message_id to which the message responds
    responds_to = Column(BigInteger, nullable=True)
    is_processed = Column(Boolean, default=False)

    __table_args__ = (
        ForeignKeyConstraint(
            ['user_id', 'server_id'],                # this table's columns
            ['users.user_id', 'users.server_id'],    # dest cols
            ondelete="CASCADE"
        ),
    )


class MultimediaContent(Base):
    __tablename__ = "multimedia_content"

    message_id = Column(BigInteger, ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False)
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

    message_id = Column(BigInteger, ForeignKey("messages.message_id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String(64), nullable=False) # Mentioned user's id

    # Composite PK
    __table_args__ = (
        PrimaryKeyConstraint('message_id', 'user_id'),
    )