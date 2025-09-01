from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest, IntentionResponse, IntentionResult
)
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail, ServiceInfoResponse, ModelInfo
)
from llmbrick.core.error_codes import ErrorCodes

class MyIntentionBrick(IntentionBrick):
    """
    MyIntentionBrick is a custom brick that extends the IntentionBrick functionality.
    It provides intent classification capabilities with confidence scores.
    """

    def __init__(self, model_name: str = "demo_model", res_prefix: str = "my_intention", **kwargs):
        super().__init__(**kwargs)
        self.model_name = model_name
        self.res_prefix = res_prefix
        # 定義簡單的意圖映射示例
        self.intent_patterns = {
            "你好": "greet",
            "hello": "greet",
            "hi": "greet",
            "再見": "goodbye",
            "bye": "goodbye",
            "查詢": "query",
            "search": "query",
            "幫助": "help",
            "help": "help"
        }

    @unary_handler
    async def process(self, input_data: IntentionRequest) -> IntentionResponse:
        """
        處理輸入文本並返回意圖分類結果
        """
        if not input_data.text:
            return IntentionResponse(
                error=ErrorDetail(
                    code=ErrorCodes.PARAMETER_INVALID,
                    message="Input text is required."
                )
            )
        
        # 示範用簡單意圖判斷邏輯
        text = input_data.text.lower()
        found_intent = None
        for pattern, intent in self.intent_patterns.items():
            if pattern in text:
                found_intent = intent
                break
        
        if found_intent:
            result = IntentionResult(
                intent_category=found_intent,
                confidence=0.9  # 簡單示例使用固定信心值
            )
        else:
            result = IntentionResult(
                intent_category="unknown",
                confidence=0.3
            )

        return IntentionResponse(
            results=[result],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )

    @get_service_info_handler
    async def get_service_info_method(self) -> ServiceInfoResponse:
        """
        返回服務資訊
        """
        model_info = ModelInfo(
            model_id=self.model_name,
            version="1.0",
            supported_languages=["en", "zh"],
            support_streaming=False,  # IntentionBrick 不支援串流
            description="A simple intention classification model supporting basic intents like greet, goodbye, query, and help."
        )

        return ServiceInfoResponse(
            service_name=f"{self.res_prefix}Service",
            version="1.0",
            models=[model_info],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
        )