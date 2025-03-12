from typing import Annotated

from pydantic import BaseModel, ConfigDict
from pydantic.types import conint

class PubStartRequest(BaseModel):
    batch_size: Annotated[int, conint(gt=0)]  # Mayor que 0
    batch_pub_time: Annotated[int, conint(ge=10)]  # Mayor o igual a 10
    interval_days: Annotated[int, conint(gt=0)]  # Mayor que 0

    model_config = ConfigDict(extra="forbid")  # No permite recibir otros campos


class PubStartResponse(BaseModel):
    task_id:str
    total_dispatch: int
