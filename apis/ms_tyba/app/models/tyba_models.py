from typing import List
from pydantic import BaseModel


class InvalidIDsModel(BaseModel):
    count: int
    ids: List[str]


class ProcessFileResponseModel(BaseModel):
    task_id:str
    file_name:str
    total_ids: int
    invalid_ids: InvalidIDsModel
