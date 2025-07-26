from deprecated import deprecated
import warnings
from llmbrick.core.brick import BaseBrick
from llmbrick.protocols.models.bricks.retrieval_types import (
    RetrievalRequest,
    RetrievalResponse,
)

class RetrievalBrick(BaseBrick[RetrievalRequest, RetrievalResponse]):
    """
    RetrievalBrick: 基於 BaseBrick

    gRPC服務類型為'retrieval'，用於檢索相關信息。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢索數據。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """
    grpc_service_type = "retrieval"

    allowed_handler_types = {"unary", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="RetrievalBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: RetrievalBrick only supports unary and get_service_info handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn("RetrievalBrick does not support bidi_streaming handler.", PendingDeprecationWarning)
        raise NotImplementedError("RetrievalBrick does not support bidi_streaming handler.")
    
    @deprecated(reason="RetrievalBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: RetrievalBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn("RetrievalBrick does not support input_streaming handler.", DeprecationWarning)
        raise NotImplementedError("RetrievalBrick does not support input_streaming handler.")
    
    @deprecated(reason="RetrievalBrick does not support output_streaming handler.") 
    def output_streaming(self):
        """
        Deprecated: RetrievalBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn("RetrievalBrick does not support output_streaming handler.", DeprecationWarning)
        raise NotImplementedError("RetrievalBrick does not support output_streaming handler.")