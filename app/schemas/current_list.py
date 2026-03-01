from datetime import date, datetime

from pydantic import BaseModel, ConfigDict


class AddCurrentListRequest(BaseModel):
    list_id: str


class CurrentListResponse(BaseModel):
    id: int
    list_id: str

    model_config = ConfigDict(from_attributes=True)


class CardInCurrentList(BaseModel):
    """Card fields exposed inside a current-list cards response."""

    id: str
    name: str
    desc: str
    due: date | None
    url: str
    short_url: str
    pos: float
    closed: bool
    id_list: str
    id_board: str
    date_last_activity: datetime
    labels: list
    badges: dict

    model_config = ConfigDict(from_attributes=True)


class CurrentListWithCards(BaseModel):
    """A Trello list that is marked current, together with its cards."""

    list_id: str
    list_name: str
    cards: list[CardInCurrentList]
