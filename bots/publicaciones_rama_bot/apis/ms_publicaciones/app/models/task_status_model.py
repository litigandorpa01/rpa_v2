from pydantic import BaseModel
from typing import Literal

class TaskStatusModel(BaseModel):
    status: Literal["pending", "processing", "completed", "failed"]
    total: int
    published: int
