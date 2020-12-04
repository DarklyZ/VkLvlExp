from vkbottle_types.objects import *
from .set_attr import SetAnnotations

@SetAnnotations(MessagesConversation, 'chat_settings')
class ChatSettings(BaseObject):
    owner_id: int
    admin_ids: list

@SetAnnotations(MessagesMessageAttachment, 'type')
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

SetAnnotations(WallWallComment, 'attachments').value(List[WallCommentAttachment], default = [])
SetAnnotations(WallWallpostFull, 'attachments').value(List[WallWallpostAttachment], default = [])

SetAnnotations(PhotosPhotoSizes, 'type').value(str)