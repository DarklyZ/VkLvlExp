from vkbottle_types.objects import *
from .set_anno import annotation

class ChatSettings(BaseObject):
    owner_id: int
    admin_ids: list

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

class ClientInfoButtonActions(enum.Enum):
    TEXT = "text"
    VKPAY = "vkpay"
    OPEN_APP = "open_app"
    LOCATION = "location"
    OPEN_LINK = "open_link"
    OPEN_PHOTO = "open_photo"
    CALLBACK = "callback"
    INTENT_SUBSCRIBE = "intent_subscribe"
    INTENT_UNSUBSCRIBE = "intent_unsubscribe"

annotation(MessagesConversation, "chat_settings", ChatSettings)
annotation(MessagesMessageAttachment, "type", MessagesMessageAttachmentType)
annotation(MessagesClientInfo, "button_actions", List[ClientInfoButtonActions])
annotation(WallWallComment, "attachments", List[WallCommentAttachment], default = [])
annotation(WallWallpostFull, "attachments", List[WallWallpostAttachment], default = [])
annotation(PhotosPhotoSizes, "type", str)