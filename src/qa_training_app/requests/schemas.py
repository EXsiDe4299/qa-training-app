from dataclasses import dataclass

from pydantic import BaseModel


@dataclass
class RequestItem:
    id: int
    title: str
    description: str
    author_id: int
    author_username: str


class CreateRequest(BaseModel):
    title: str
    description: str


class RequestResponse(BaseModel):
    id: int
    title: str
    description: str
    author_id: int
    author_username: str
