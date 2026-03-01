from pydantic import BaseModel, Field


class TrelloList(BaseModel):
    """Represents a Trello List object cloned from the Trello API."""

    id: str = Field(
        pattern=r"^[0-9a-fA-F]{24}$",
        description="Unique 24-character hex identifier of the list.",
        examples=["5abbe4b7ddc1b351ef961414"],
    )
    idBoard: str = Field(
        description="ID of the board this list belongs to.",
        examples=["5abbe4b7ddc1b351ef961414"],
    )
    name: str = Field(
        description="Display name of the list.",
        examples=["Things to buy today"],
    )
    closed: bool = Field(default=False, description="Whether the list is archived.")
    subscribed: bool = Field(
        default=False, description="Whether the viewer is subscribed to the list."
    )
    pos: float = Field(description="Position of the list on the board.", examples=[16384])
    softLimit: str | None = Field(
        default=None, description="Optional soft card limit set on the list."
    )
    limits: dict = Field(
        default_factory=dict,
        description="Rate-limit metadata for the list.",
    )

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "id": "5abbe4b7ddc1b351ef961414",
                "idBoard": "5abbe4b7ddc1b351ef961413",
                "name": "Things to buy today",
                "closed": False,
                "subscribed": False,
                "pos": 16384,
                "softLimit": None,
                "limits": {},
            }
        },
    }
