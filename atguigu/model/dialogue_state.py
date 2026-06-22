from sqlalchemy import TEXT,String
from sqlalchemy.orm import Mapped,mapped_column

from atguigu.model.base import BaseModel

class DialogueStateRecord(BaseModel):

    __tablename__ = "dialogue_states"
    sender_id: Mapped[str] = mapped_column(String(255), primary_key=True)
    state_json:Mapped[str] = mapped_column(TEXT, nullable=False,default='{}')

    