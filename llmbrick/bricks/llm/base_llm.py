from deprecated import deprecated
import warnings
from llmbrick.protocols.models.bricks.llm_types import (
    LLMRequest,
    LLMResponse,
)

from llmbrick.core.brick import BaseBrick, BrickType

class LLMBrick(BaseBrick[LLMRequest, LLMResponse]):
    """
    LLMBrick: 基於 BaseBrick，並支援 default_prompt 參數
    
    gRPC服務類型為'llm'，用於處理大型語言模型相關請求。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於生成模型回應。
    - OutputStreaming: 用於生成模型回應的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming

    """
    brick_type = BrickType.LLM
    # 僅允許這三種 handler
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}

    def __init__(self, default_prompt: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prompt = default_prompt

    @deprecated(reason="LLMBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: LLMBrick only supports unary and output_streaming handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("LLMBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("LLMBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="LLMBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: LLMBrick only supports unary and output_streaming handlers, input_streaming is not applicable.
        """
        warnings.warn("LLMBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("LLMBrick does not support input_streaming handler.")