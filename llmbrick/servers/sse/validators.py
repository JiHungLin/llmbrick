from llmbrick.protocols.models.http.conversation import ConversationSSERequest, Message
from llmbrick.core.exceptions import ValidationException

class ConversationSSERequestValidator:
    """
    SSE請求的業務邏輯驗證器
    """

    @staticmethod
    def validate(request: ConversationSSERequest, allowed_models=None, max_message_length=10000, max_messages_count=100):
        """
        綜合驗證入口
        """
        ConversationSSERequestValidator.validate_messages(request.messages, max_message_length, max_messages_count)
        ConversationSSERequestValidator.validate_model_name(request.model, allowed_models)

    @staticmethod
    def validate_messages(messages, max_message_length=10000, max_messages_count=100):
        if not messages:
            raise ValidationException("Messages cannot be empty")
        
        # 檢查訊息數量限制
        if len(messages) > max_messages_count:
            raise ValidationException(f"Too many messages: {len(messages)} > {max_messages_count}")
        
        # 檢查訊息長度
        for i, msg in enumerate(messages):
            if len(msg.content) > max_message_length:
                raise ValidationException(f"Message {i} too long: {len(msg.content)} > {max_message_length}")
        
        # 檢查是否有多個system message
        system_messages = [m for m in messages if m.role == "system"]
        if len(system_messages) > 1:
            raise ValidationException("Only one system message allowed")
        
        # 檢查最後一則訊息必須是user
        if messages[-1].role != "user":
            raise ValidationException("Last message must be from user")
        
        # 檢查訊息角色的有效性
        valid_roles = {"system", "user", "assistant"}
        for i, msg in enumerate(messages):
            if msg.role not in valid_roles:
                raise ValidationException(f"Invalid role '{msg.role}' in message {i}")

    @staticmethod
    def validate_model_name(model, allowed_models=None):
        if allowed_models is None:
            allowed_models = ["gpt-4o", "gpt-3.5-turbo", "sonar"]
        if model not in allowed_models:
            raise ValidationException(f"Unsupported model: {model}")