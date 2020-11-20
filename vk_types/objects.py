from vkbottle_types.objects import *

class ChatSettings(BaseModel):
    owner_id: int
    admin_ids: list

class MessagesConversation(MessagesConversation):
    chat_settings: Optional[ChatSettings] = None
