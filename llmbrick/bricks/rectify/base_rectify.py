import warnings

from deprecated import deprecated

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.rectify_types import (
    RectifyRequest,
    RectifyResponse,
)


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
        warnings.warn(
            "RectifyBrick does not support bidi_streaming handler.",
            PendingDeprecationWarning,
        )
        raise NotImplementedError(
            "RectifyBrick does not support bidi_streaming handler."
        )

    @deprecated(reason="RectifyBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: RectifyBrick only supports unary and get_service_info handlers, input_streaming is not applicable.
        """
        warnings.warn(
            "RectifyBrick does not support input_streaming handler.", DeprecationWarning
        )
        raise NotImplementedError(
            "RectifyBrick does not support input_streaming handler."
        )

    @deprecated(reason="RectifyBrick does not support output_streaming handler.")
    def output_streaming(self):
        """
        Deprecated: RectifyBrick only supports unary and get_service_info handlers, output_streaming is not applicable.
        """
        warnings.warn(
            "RectifyBrick does not support output_streaming handler.",
            DeprecationWarning,
        )
        raise NotImplementedError(
            "RectifyBrick does not support output_streaming handler."
        )

    @classmethod
    def toGrpcClient(cls, remote_address: str, **kwargs):
        """
        將 RectifyBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            **kwargs: 傳遞給 RectifyBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 RectifyBrick 實例
        """
        import grpc

        from llmbrick.protocols.grpc.rectify import rectify_pb2_grpc, rectify_pb2
        from llmbrick.protocols.grpc.common import common_pb2

        # 建立 brick 實例
        brick = cls(**kwargs)

        @brick.unary()
        async def unary_handler(request: RectifyRequest) -> RectifyResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = rectify_pb2_grpc.RectifyServiceStub(channel)

            # 建立 gRPC 請求
            grpc_request = rectify_pb2.RectifyRequest()
            grpc_request.text = request.text
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            response = await grpc_client.Unary(grpc_request)

            # 將 protobuf 回應轉換為 RectifyResponse
            return RectifyResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = rectify_pb2_grpc.RectifyServiceStub(channel)

            request = common_pb2.ServiceInfoRequest()
            response = await grpc_client.GetServiceInfo(request)
            models = [
                ModelInfo(
                    model_id=model.model_id,
                    version=model.version,
                    supported_languages=list(model.supported_languages),
                    support_streaming=model.support_streaming,
                    description=getattr(model, "description", ""),
                )
                for model in response.models
            ]
            return ServiceInfoResponse(
                service_name=response.service_name,
                version=response.version,
                models=models,
                error=ErrorDetail.from_pb2_model(response.error) if response.error else None,
            )

        return brick
