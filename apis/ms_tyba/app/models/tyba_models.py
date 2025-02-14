from typing import List
from pydantic import BaseModel


class InvalidIDsModel(BaseModel):
    count: int
    ids: List[str]


# class ProcessFileResponseModel(BaseModel):
#     total_parsed_ids: int
    # invalid_ids: InvalidIDsModel
