from datetime import datetime, date
from enum import Enum

from pydantic import BaseModel, Field, field_validator


# ---------------------------------------------------------------------------
# Enums
# ---------------------------------------------------------------------------


class CardColor(str, Enum):
    yellow = "yellow"
    purple = "purple"
    blue = "blue"
    red = "red"
    green = "green"
    orange = "orange"
    black = "black"
    sky = "sky"
    pink = "pink"
    lime = "lime"


class CoverBrightness(str, Enum):
    light = "light"
    dark = "dark"


class CoverSize(str, Enum):
    normal = "normal"


class CardRole(str, Enum):
    separator = "separator"
    board = "board"
    mirror = "mirror"
    link = "link"


# ---------------------------------------------------------------------------
# Nested models
# ---------------------------------------------------------------------------


class TrelloBadgesByType(BaseModel):
    board: float = 0
    card: float = 0


class TrelloBadgesAttachmentsByType(BaseModel):
    trello: TrelloBadgesByType = Field(default_factory=TrelloBadgesByType)


class CardBadges(BaseModel):
    votes: int = 0
    viewingMemberVoted: bool = False
    subscribed: bool = False
    fogbugz: str = ""
    checkItems: int = 0
    checkItemsChecked: int = 0
    comments: int = 0
    attachments: int = 0
    description: bool = False
    due: date | None = None
    dueComplete: bool = False
    start: date | None = None
    location: bool = False
    attachmentsByType: TrelloBadgesAttachmentsByType = Field(
        default_factory=TrelloBadgesAttachmentsByType
    )


class CardCover(BaseModel):
    color: CardColor | None = None
    idAttachment: str | None = Field(
        default=None,
        pattern=r"^[0-9a-fA-F]{24}$",
        description="Trello attachment ID used as cover.",
    )
    idUploadedBackground: bool | None = None
    size: CoverSize = CoverSize.normal
    brightness: CoverBrightness = CoverBrightness.light
    isTemplate: bool = False


class CardLabel(BaseModel):
    id: str = Field(pattern=r"^[0-9a-fA-F]{24}$", description="Label ID.")
    idBoard: str = Field(pattern=r"^[0-9a-fA-F]{24}$", description="Board ID.")
    name: str | None = Field(
        default=None,
        min_length=0,
        max_length=16384,
        description="Display name of the label.",
    )
    color: CardColor | None = Field(
        default=None,
        description="Label color. None means no color (label hidden on card front).",
    )


# ---------------------------------------------------------------------------
# Main Card model
# ---------------------------------------------------------------------------


class Card(BaseModel):
    """Represents a Trello Card object cloned from the Trello API."""

    id: str = Field(
        pattern=r"^[0-9a-fA-F]{24}$",
        description="Unique 24-character hex identifier of the card.",
        examples=["5abbe4b7ddc1b351ef961414"],
    )
    idShort: int = Field(description="Short integer ID scoped to the board.")
    idBoard: str = Field(
        pattern=r"^[0-9a-fA-F]{24}$",
        description="ID of the board this card belongs to.",
        examples=["5abbe4b7ddc1b351ef961414"],
    )
    idList: str = Field(
        pattern=r"^[0-9a-fA-F]{24}$",
        description="ID of the list this card is in.",
        examples=["5abbe4b7ddc1b351ef961415"],
    )
    idAttachmentCover: str | None = Field(
        default=None,
        pattern=r"^[0-9a-fA-F]{24}$",
        description="ID of the attachment used as the card cover.",
        examples=["5abbe4b7ddc1b351ef961415"],
    )
    mirrorSourceId: str | None = Field(
        default=None,
        pattern=r"^[0-9a-fA-F]{24}$",
        description="ID of the source card when this is a mirror card.",
    )

    # Identity
    name: str = Field(description="Name/title of the card.", examples=["👋 What? Why? How?"])
    shortLink: str = Field(description="Short alphanumeric link token.", examples=["H0TZyzbK"])
    shortUrl: str = Field(description="Short URL to the card.", examples=["https://trello.com/c/H0TZyzbK"])
    url: str = Field(
        description="Full URL to the card.",
        examples=["https://trello.com/c/H0TZyzbK/4-what-why-how"],
    )

    # Content
    desc: str = Field(default="", description="Description body of the card.")
    descData: dict = Field(
        default_factory=dict,
        description="Structured data for the description (e.g. emoji references).",
    )

    # State
    closed: bool = Field(default=False, description="Whether the card is archived.")
    subscribed: bool = Field(default=False, description="Whether the viewer is subscribed to the card.")
    manualCoverAttachment: bool = Field(
        default=False,
        description="Whether the cover attachment was set manually.",
    )

    # Dates
    dateLastActivity: datetime = Field(
        description="Timestamp of the last activity on the card.",
        examples=["2019-09-16T16:19:17.156Z"],
    )
    due: date | None = Field(default=None, description="Due date of the card.")
    dueReminder: str | None = Field(
        default=None,
        description="Reminder offset before due date (e.g. '-1' for no reminder).",
    )

    # Location
    address: str | None = Field(default=None, description="Physical address attached to the card.")
    locationName: str | None = Field(default=None, description="Location name attached to the card.")
    coordinates: str | None = Field(
        default=None,
        description="Lat/long coordinates as a string (e.g. '37.7749,-122.4194').",
    )

    # Position
    pos: float = Field(description="Position of the card in its list.", examples=[65535])

    # Role
    cardRole: CardRole | None = Field(
        default=None,
        description="Special role of the card (separator, board, mirror, link).",
    )
    creationMethod: str | None = Field(
        default=None, description="How the card was created (e.g. 'assisted')."
    )

    # Relations
    idMembers: list[str] = Field(
        default_factory=list,
        description="List of member IDs assigned to the card.",
    )
    idMembersVoted: list[str] = Field(
        default_factory=list,
        description="List of member IDs who voted on the card.",
    )
    idChecklists: list[str] = Field(
        default_factory=list,
        description="List of checklist IDs on the card.",
    )
    idLabels: list[str] = Field(
        default_factory=list,
        description="List of label IDs on the card.",
    )
    labels: list[CardLabel] = Field(
        default_factory=list,
        description="Expanded label objects on the card.",
    )
    checkItemStates: list[str] = Field(
        default_factory=list,
        description="States of check items across all checklists.",
    )

    # Rich sub-objects
    badges: CardBadges = Field(
        default_factory=CardBadges,
        description="Aggregated badge counts for comments, attachments, votes, etc.",
    )
    cover: CardCover = Field(
        default_factory=CardCover,
        description="Card cover configuration.",
    )
    limits: dict = Field(
        default_factory=dict,
        description="Rate-limit metadata for card attachments and other resources.",
    )

    @field_validator("idMembers", "idMembersVoted", "idChecklists", "idLabels", mode="before")
    @classmethod
    def validate_trello_id_list(cls, values: list) -> list[str]:
        """Accept both raw TrelloID strings and nested dicts with an 'id' key."""
        result: list[str] = []
        for item in values:
            if isinstance(item, str):
                result.append(item)
            elif isinstance(item, dict) and "id" in item:
                result.append(item["id"])
        return result

    model_config = {
        "populate_by_name": True,
        "str_strip_whitespace": True,
        "json_schema_extra": {
            "example": {
                "id": "5abbe4b7ddc1b351ef961414",
                "idShort": 4,
                "idBoard": "5abbe4b7ddc1b351ef961414",
                "idList": "5abbe4b7ddc1b351ef961415",
                "idAttachmentCover": None,
                "mirrorSourceId": None,
                "name": "👋 What? Why? How?",
                "shortLink": "H0TZyzbK",
                "shortUrl": "https://trello.com/c/H0TZyzbK",
                "url": "https://trello.com/c/H0TZyzbK/4-what-why-how",
                "desc": "Hey there, welcome to our board!",
                "descData": {},
                "closed": False,
                "subscribed": False,
                "manualCoverAttachment": False,
                "dateLastActivity": "2019-09-16T16:19:17.156Z",
                "due": None,
                "dueReminder": None,
                "address": None,
                "locationName": None,
                "coordinates": None,
                "pos": 65535,
                "cardRole": None,
                "creationMethod": None,
                "idMembers": [],
                "idMembersVoted": [],
                "idChecklists": [],
                "idLabels": [],
                "labels": [],
                "checkItemStates": [],
                "badges": {},
                "cover": {},
                "limits": {},
            }
        },
    }
