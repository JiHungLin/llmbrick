import warnings

from deprecated import deprecated

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)


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
        warnings.warn(
            "TranslateBrick does not support bidi_streaming handler.",
            PendingDeprecationWarning,
        )
        raise NotImplementedError(
            "TranslateBrick does not support bidi_streaming handler."
        )

    @deprecated(reason="TranslateBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: TranslateBrick only supports unary and output_streaming handlers, input_streaming is not applicable.
        """
        warnings.warn(
            "TranslateBrick does not support input_streaming handler.",
            DeprecationWarning,
        )
        raise NotImplementedError(
            "TranslateBrick does not support input_streaming handler."
        )

    @classmethod
    def toGrpcClient(cls, remote_address: str, **kwargs):
        """
        將 TranslateBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            **kwargs: 傳遞給 TranslateBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 TranslateBrick 實例
        """
        import grpc

        from llmbrick.protocols.grpc.translate import translate_pb2_grpc, translate_pb2
        from llmbrick.protocols.grpc.common import common_pb2

        # 建立 brick 實例
        brick = cls(**kwargs)

        @brick.unary()
        async def unary_handler(request: TranslateRequest) -> TranslateResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = translate_pb2_grpc.TranslateServiceStub(channel)

            # 建立 gRPC 請求
            grpc_request = translate_pb2.TranslateRequest()
            grpc_request.text = request.text
            grpc_request.model_id = request.model_id
            grpc_request.target_language = request.target_language
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            response = await grpc_client.Unary(grpc_request)

            # 將 protobuf 回應轉換為 TranslateResponse
            return TranslateResponse.from_pb2_model(response)

        @brick.output_streaming()
        async def output_streaming_handler(request: TranslateRequest):
            """異步流式輸出處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = translate_pb2_grpc.TranslateServiceStub(channel)

            # 建立 gRPC 請求
            grpc_request = translate_pb2.TranslateRequest()
            grpc_request.text = request.text
            grpc_request.model_id = request.model_id
            grpc_request.target_language = request.target_language
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            async for response in grpc_client.OutputStreaming(grpc_request):
                yield TranslateResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = translate_pb2_grpc.TranslateServiceStub(channel)

            request = common_pb2.ServiceInfoRequest()
            response = await grpc_client.GetServiceInfo(request)
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
