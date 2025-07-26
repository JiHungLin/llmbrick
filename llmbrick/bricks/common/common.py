from llmbrick.core.brick import BaseBrick
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest,
    CommonResponse,
)

class CommonBrick(BaseBrick[CommonRequest, CommonResponse]):
    """
    CommonBrick: 基於 BaseBrick 的通用服務，提供基本的請求和回應結構。
    gRPC服務類型為'Common'，用於處理通用請求。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於處理單次請求。
    - OutputStreaming: 用於處理流式回應。
    - InputStreaming: 用於處理流式輸入。
    - BidiStreaming: 用於處理雙向流式請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming
    - InputStreaming -> input_streaming
    - BidiStreaming -> bidi_streaming
    """
    grpc_service_type = "Common"
