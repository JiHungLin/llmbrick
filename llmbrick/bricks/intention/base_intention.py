from deprecated import deprecated
import warnings
from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.intention_types import (
    IntentionRequest,
    IntentionResponse,
)
class IntentionBrick(BaseBrick[IntentionRequest, IntentionResponse]):
    """
    IntentionBrick: 基於 BaseBrick

    gRPC服務類型為'intention'，用於意圖保護。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """
    brick_type = BrickType.INTENTION

    allowed_handler_types = {"unary", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="IntentionBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: IntentionBrick only supports unary and get_service_info handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("IntentionBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("IntentionBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="IntentionBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: IntentionBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn("IntentionBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("IntentionBrick does not support input_streaming handler.")
    

    @deprecated(reason="IntentionBrick does not support output_streaming handler.")
    def output_streaming(self):
        """
        Deprecated: IntentionBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn("IntentionBrick does not support output_streaming handler.", DeprecationWarning)
        raise NotImplementedError("IntentionBrick does not support output_streaming handler.")