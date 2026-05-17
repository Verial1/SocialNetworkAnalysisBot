from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, ConfigDict

class Server(BaseModel):
    server_id: str
    name: str
    picture: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class User(BaseModel):
    user_id: str
    server_id: str
    server_username: str
    server_picture: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class Multimedia(BaseModel):
    index: int
    type: str
    embedding: Optional[List[float]] = None
    ocr_text: Optional[str] = None

    model_config = ConfigDict(extra="ignore")

class Message(BaseModel):
    message_id: str
    user_id: str
    server_id: str
    text_content: Optional[str] = None
    responds_to: Optional[str] = None
    date: datetime
    
    mentions: List[str] = []
    media: List[Multimedia] = []

    is_processed: Optional[bool] = False

    model_config = ConfigDict(extra="ignore")