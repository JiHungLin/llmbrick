from deprecated import deprecated
import warnings
from llmbrick.core.brick import BaseBrick
from llmbrick.protocols.models.bricks.guard_types import (
    GuardRequest,
    GuardResponse,
)
class GuardBrick(BaseBrick[GuardRequest, GuardResponse]):
    """
    GuardBrick: 基於 BaseBrick

    gRPC服務類型為'guard'，用於意圖保護。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """
    grpc_service_type = "guard"

    allowed_handler_types = {"unary", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="GuardBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: GuardBrick only supports unary and get_service_info handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("GuardBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("GuardBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="GuardBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: GuardBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn("GuardBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("GuardBrick does not support input_streaming handler.")
    

    @deprecated(reason="GuardBrick does not support output_streaming handler.")
    def output_streaming(self):
        """
        Deprecated: GuardBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn("GuardBrick does not support output_streaming handler.", DeprecationWarning)
        raise NotImplementedError("GuardBrick does not support output_streaming handler.")