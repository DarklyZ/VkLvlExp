from vkbottle_types.objects import *
from .set_attr import SetAttr

@SetAttr(MessagesConversation, 'chat_settings')
class ChatSettings(BaseObject):
    owner_id: int
    admin_ids: list

@SetAttr(MessagesMessageAttachment, 'type')
class MessagesMessageAttachmentType(enum.Enum):
    PHOTO = "photo"
    AUDIO = "audio"
    VIDEO = "video"
    DOC = "doc"
    POLL = "poll"
    LINK = "link"
    MARKET = "market"
    MARKET_ALBUM = "market_album"
    GIFT = "gift"
    STICKER = "sticker"
    STORY = "story"
    WALL = "wall"
    WALL_REPLY = "wall_reply"
    ARTICLE = "article"
    GRAFFITI = "graffiti"
    AUDIO_MESSAGE = "audio_message"

SetAttr(WallWallComment, 'attachments').set(List[WallCommentAttachment], default = [])
SetAttr(WallWallpostFull, 'attachments').set(List[WallWallpostAttachment], default = [])