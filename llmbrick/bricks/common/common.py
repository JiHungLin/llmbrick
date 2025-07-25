from llmbrick.core.brick import BaseBrick
from llmbrick.protocols.models.common_types import (
    CommonRequest,
    CommonResponse,
    ServiceInfoResponse,
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


    def GetServiceInfo(self) -> ServiceInfoResponse:
        """
        與 gRPC 的 GetServiceInfo 方法對應，返回服務信息。方便內部使用。
        """
        return self.run_get_service_info()
    
    def Unary(self, request: CommonRequest) -> CommonResponse:
        """
        與 gRPC 的 Unary 方法對應，處理單次請求。方便內部使用。
        """
        return self.run_unary(request)
    
    def OutputStreaming(self, request: CommonRequest) -> CommonResponse:
        """
        與 gRPC 的 OutputStreaming 方法對應，處理流式回應。方便內部使用。
        """
        return self.run_output_streaming(request)
    
    def InputStreaming(self, request_iterator) -> CommonResponse:
        """
        與 gRPC 的 InputStreaming 方法對應，處理流式輸入。方便內部使用。
        """
        return self.run_input_streaming(request_iterator)

    def BidiStreaming(self, request_iterator) -> CommonResponse:
        """
        與 gRPC 的 BidiStreaming 方法對應，處理雙向流式請求。方便內部使用。
        """
        return self.run_bidi_streaming(request_iterator)
