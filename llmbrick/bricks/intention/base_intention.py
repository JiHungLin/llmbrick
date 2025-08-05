import warnings

from deprecated import deprecated

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
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
        warnings.warn(
            "IntentionBrick does not support bidi_streaming handler.",
            PendingDeprecationWarning,
        )
        raise NotImplementedError(
            "IntentionBrick does not support bidi_streaming handler."
        )

    @deprecated(reason="IntentionBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: IntentionBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn(
            "IntentionBrick does not support input_streaming handler.",
            DeprecationWarning,
        )
        raise NotImplementedError(
            "IntentionBrick does not support input_streaming handler."
        )

    @deprecated(reason="IntentionBrick does not support output_streaming handler.")
    def output_streaming(self):
        """
        Deprecated: IntentionBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn(
            "IntentionBrick does not support output_streaming handler.",
            DeprecationWarning,
        )
        raise NotImplementedError(
            "IntentionBrick does not support output_streaming handler."
        )

    @classmethod
    def toGrpcClient(cls, remote_address: str, **kwargs):
        """
        將 IntentionBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            **kwargs: 傳遞給 IntentionBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 IntentionBrick 實例
        """
        import grpc

        from llmbrick.protocols.grpc.intention import intention_pb2_grpc, intention_pb2
        from llmbrick.protocols.grpc.common import common_pb2

        # 建立 brick 實例
        brick = cls(**kwargs)

        @brick.unary()
        async def unary_handler(request: IntentionRequest) -> IntentionResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = intention_pb2_grpc.IntentionServiceStub(channel)

            # 建立 gRPC 請求
            grpc_request = intention_pb2.IntentionRequest()
            grpc_request.text = request.text
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            response = await grpc_client.Unary(grpc_request)
            return IntentionResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""
            
            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = intention_pb2_grpc.IntentionServiceStub(channel)

            request = common_pb2.ServiceInfoRequest()
            response = await grpc_client.GetServiceInfo(request)
            # 處理 error 欄位
            return ServiceInfoResponse(
                service_name=response.service_name,
                version=response.version,
                models=[
                    ModelInfo(
                        model_id=model.model_id,
                        version=model.version,
                        supported_languages=list(model.supported_languages),
                        support_streaming=model.support_streaming,
                        description=getattr(model, "description", ""),
                    )
                    for model in response.models
                ],
                error=ErrorDetail.from_pb2_model(response.error) if response.error else None,
            )

        return brick
