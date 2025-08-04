import warnings

from deprecated import deprecated

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.models.bricks.common_types import (
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
)
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse


class LLMBrick(BaseBrick[LLMRequest, LLMResponse]):
    """
    LLMBrick: 基於 BaseBrick，並支援 default_prompt 參數

    gRPC服務類型為'llm'，用於處理大型語言模型相關請求。
    gRPC提中以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於生成模型回應。
    - OutputStreaming: 用於生成模型回應的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming

    """

    brick_type = BrickType.LLM
    # 僅允許這三種 handler
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}

    def __init__(self, default_prompt: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prompt = default_prompt

    @deprecated(reason="LLMBrick does not support bidi_streaming handler.")
    def bidi_streaming(self):
        """
        Deprecated: LLMBrick only supports unary and output_streaming handlers, input_streaming and bidi_streaming are not applicable.
        """
        warnings.warn(
            "LLMBrick does not support bidi_streaming handler.",
            PendingDeprecationWarning,
        )
        raise NotImplementedError("LLMBrick does not support bidi_streaming handler.")

    @deprecated(reason="LLMBrick does not support input_streaming handler.")
    def input_streaming(self):
        """
        Deprecated: LLMBrick only supports unary and output_streaming handlers, input_streaming is not applicable.
        """
        warnings.warn(
            "LLMBrick does not support input_streaming handler.", DeprecationWarning
        )
        raise NotImplementedError("LLMBrick does not support input_streaming handler.")

    @classmethod
    def toGrpcClient(cls, remote_address: str, default_prompt: str = "", **kwargs):
        """
        將 LLMBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            default_prompt: 預設提示詞
            **kwargs: 傳遞給 LLMBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 LLMBrick 實例
        """
        import grpc

        from llmbrick.protocols.grpc.llm import llm_pb2_grpc, llm_pb2
        from llmbrick.protocols.grpc.common import common_pb2



        # 建立 brick 實例
        brick = cls(default_prompt=default_prompt, **kwargs)

        @brick.unary()
        async def unary_handler(request: LLMRequest, context=None) -> LLMResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = llm_pb2_grpc.LLMServiceStub(channel)
            # 轉換 Context 列表
            grpc_contexts = []
            for ctx in request.context:
                grpc_context = llm_pb2.Context()
                grpc_context.role = ctx.role
                grpc_context.content = ctx.content
                grpc_contexts.append(grpc_context)

            # 建立 gRPC 請求
            grpc_request = llm_pb2.LLMRequest()
            grpc_request.model_id = request.model_id
            grpc_request.prompt = request.prompt
            grpc_request.context.extend(grpc_contexts)
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language
            grpc_request.temperature = request.temperature
            grpc_request.max_tokens = request.max_tokens

            response = await grpc_client.Unary(grpc_request)

            # 將 protobuf 回應轉換為 LLMResponse
            return LLMResponse.from_pb2_model(response)

        @brick.output_streaming()
        async def output_streaming_handler(request: LLMRequest, context=None):
            """異步流式輸出處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = llm_pb2_grpc.LLMServiceStub(channel)

            # 轉換 Context 列表
            grpc_contexts = []
            for ctx in request.context:
                grpc_context = llm_pb2.Context()
                grpc_context.role = ctx.role
                grpc_context.content = ctx.content
                grpc_contexts.append(grpc_context)

            # 建立 gRPC 請求
            grpc_request = llm_pb2.LLMRequest()
            grpc_request.model_id = request.model_id
            grpc_request.prompt = request.prompt
            grpc_request.context.extend(grpc_contexts)
            grpc_request.client_id = request.client_id
            grpc_request.session_id = request.session_id
            grpc_request.request_id = request.request_id
            grpc_request.source_language = request.source_language
            grpc_request.temperature = request.temperature
            grpc_request.max_tokens = request.max_tokens

            async for response in grpc_client.OutputStreaming(grpc_request):
                yield LLMResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""
            
            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = llm_pb2_grpc.LLMServiceStub(channel)

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
                        description=model.description,
                    )
                    for model in response.models
                ],
                error=ErrorDetail.from_pb2_model(response.error) if response.error else None,
            )

        return brick
