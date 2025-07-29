from deprecated import deprecated
import warnings

from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)

from llmbrick.core.brick import BaseBrick, BrickType

class TranslateBrick(BaseBrick[TranslateRequest, TranslateResponse]):
    """
    TranslateBrick: 基於 BaseBrick

    gRPC服務類型為'Translate'，用於統整資料、轉換或翻譯。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於統整資料並進行翻譯。
    - OutputStreaming: 用於統整資料並進行翻譯的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming

    """
    brick_type = BrickType.TRANSLATE

    # 僅允許這三種 handler
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="TranslateBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: TranslateBrick only supports unary and output_streaming handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("TranslateBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("TranslateBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="TranslateBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: TranslateBrick only supports unary and output_streaming handlers, input_streaming is not applicable.
        """
        warnings.warn("TranslateBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("TranslateBrick does not support input_streaming handler.")
