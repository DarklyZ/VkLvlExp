from vkbottle_types.objects import *
from .set_anno import Annotation

class MessagesConversationChatSettings(MessagesConversationChatSettings):
    owner_id: int
    admin_ids: list

Annotation(MessagesConversation).chat_settings(MessagesConversationChatSettings)
Annotation(WallWallComment).attachments(List[WallCommentAttachment], default = [])
Annotation(WallWallpostFull).attachments(List[WallWallpostAttachment], default = [])
Annotation(MessagesClientInfo).button_actions(List[str])
Annotation(MessagesMessageAttachment).type(str)
Annotation(WallCommentAttachment).type(str)
Annotation(WallWallpostAttachment).type(str)
Annotation(PhotosPhotoSizes).type(str)