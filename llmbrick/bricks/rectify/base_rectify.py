from deprecated import deprecated
import warnings
from llmbrick.protocols.models.bricks.rectify_types import (
    RectifyRequest,
    RectifyResponse,
)
from llmbrick.core.brick import BaseBrick, BrickType

class RectifyBrick(BaseBrick[RectifyRequest, RectifyResponse]):
    """
    RectifyBrick: 基於 BaseBrick

    gRPC服務類型為'rectify'，用於文本校正。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於校正文本。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    """
    brick_type = BrickType.RECTIFY

    allowed_handler_types = {"unary", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="RectifyBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: RectifyBrick only supports unary and get_service_info handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("RectifyBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("RectifyBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="RectifyBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: RectifyBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn("RectifyBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("RectifyBrick does not support input_streaming handler.")
    
    @deprecated(reason="RectifyBrick does not support output_streaming handler.")
    def output_streaming(self):
        """
        Deprecated: RectifyBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn("RectifyBrick does not support output_streaming handler.", DeprecationWarning)
        raise NotImplementedError("RectifyBrick does not support output_streaming handler.")