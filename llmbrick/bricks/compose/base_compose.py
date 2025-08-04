import warnings

from deprecated import deprecated

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.compose_types import (
    ComposeRequest,
    ComposeResponse,
)


class ComposeBrick(BaseBrick[ComposeRequest, ComposeResponse]):
    """
    ComposeBrick: 基於 BaseBrick

    gRPC服務類型為'Compose'，用於統整資料、轉換或翻譯。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於統整資料並進行翻譯。
    - OutputStreaming: 用於統整資料並進行翻譯的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming

    """

    brick_type = BrickType.COMPOSE

    # 僅允許這三種 handler
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    @deprecated(reason="ComposeBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: ComposeBrick only supports unary and output_streaming handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn(
            "ComposeBrick does not support bidi_streaming handler.",
            PendingDeprecationWarning,
        )
        raise NotImplementedError(
            "ComposeBrick does not support bidi_streaming handler."
        )

    @deprecated(reason="ComposeBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: ComposeBrick only supports unary and output_streaming handlers, input_streaming is not applicable.
        """
        warnings.warn(
            "ComposeBrick does not support input_streaming handler.", DeprecationWarning
        )
        raise NotImplementedError(
            "ComposeBrick does not support input_streaming handler."
        )

    @classmethod
    def toGrpcClient(cls, remote_address: str, **kwargs):
        """
        將 ComposeBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            **kwargs: 傳遞給 ComposeBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 ComposeBrick 實例
        """
        import grpc
        from llmbrick.protocols.grpc.compose import compose_pb2_grpc, compose_pb2
        from llmbrick.protocols.grpc.common import common_pb2

        # 建立 brick 實例
        brick = cls(**kwargs)

        @brick.unary()
        async def unary_handler(request: ComposeRequest) -> ComposeResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = compose_pb2_grpc.ComposeServiceStub(channel)

            # 轉換 Document 列表
            grpc_documents = []
            for doc in request.input_documents:
                grpc_doc = compose_pb2.Document()
                grpc_doc.doc_id = doc.doc_id
                grpc_doc.title = doc.title
                grpc_doc.snippet = doc.snippet
                grpc_doc.score = doc.score
                # metadata 是 google.protobuf.Struct
                grpc_doc.metadata.update(doc.metadata)
                grpc_documents.append(grpc_doc)

            # 建立 gRPC 請求
            grpc_request = compose_pb2.ComposeRequest()
            grpc_request.input_documents.extend(grpc_documents)
            grpc_request.target_format = request.target_format
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            response = await grpc_client.Unary(grpc_request)

            return ComposeResponse.from_pb2_model(response)

        @brick.output_streaming()
        async def output_streaming_handler(request: ComposeRequest):
            """異步流式輸出處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = compose_pb2_grpc.ComposeServiceStub(channel)

            # 轉換 Document 列表
            grpc_documents = []
            for doc in request.input_documents:
                grpc_doc = compose_pb2.Document()
                grpc_doc.doc_id = doc.doc_id
                grpc_doc.title = doc.title
                grpc_doc.snippet = doc.snippet
                grpc_doc.score = doc.score
                # metadata 是 google.protobuf.Struct
                grpc_doc.metadata.update(doc.metadata)
                grpc_documents.append(grpc_doc)

            # 建立 gRPC 請求
            grpc_request = compose_pb2.ComposeRequest()
            grpc_request.input_documents.extend(grpc_documents)
            grpc_request.target_format = request.target_format
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language

            async for response in grpc_client.OutputStreaming(grpc_request):
                yield ComposeResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = compose_pb2_grpc.ComposeServiceStub(channel)

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
                    )
                    for model in response.models
                ],
                error=ErrorDetail.from_pb2_model(response.error) if response.error else None,
            )

        return brick
