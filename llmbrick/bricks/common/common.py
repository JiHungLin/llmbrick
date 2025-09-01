import grpc
from google.protobuf import struct_pb2

from llmbrick.core.brick import BaseBrick, BrickType
from llmbrick.protocols.grpc.common import common_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest,
    CommonResponse,
    ErrorDetail,
    ServiceInfoResponse,
    ModelInfo
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

    brick_type = BrickType.COMMON

    @classmethod
    def toGrpcClient(cls, remote_address: str, **kwargs): # noqa: C901
        """
        將 CommonBrick 轉換為異步 gRPC 客戶端。

        Args:
            remote_address: gRPC 伺服器地址，格式為 "host:port"
            **kwargs: 傳遞給 CommonBrick 建構子的額外參數

        Returns:
            配置為異步 gRPC 客戶端的 CommonBrick 實例
        """
        from llmbrick.protocols.grpc.common import common_pb2

        # 建立 brick 實例
        brick = cls(**kwargs)

        @brick.unary()
        async def unary_handler(request: struct_pb2.Struct) -> CommonResponse:
            """異步單次請求處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = common_pb2_grpc.CommonServiceStub(channel)
            # 建立 gRPC 請求
            grpc_request = common_pb2.CommonRequest()
            grpc_request.data.update(request.data)

            response = await grpc_client.Unary(grpc_request)

            return CommonResponse.from_pb2_model(response)

        @brick.output_streaming()
        async def output_streaming_handler(request: struct_pb2.Struct):
            """異步流式輸出處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = common_pb2_grpc.CommonServiceStub(channel)
            # 建立 gRPC 請求
            grpc_request = common_pb2.CommonRequest()
            grpc_request.data.update(request.data)

            async for response in grpc_client.OutputStreaming(grpc_request):
                # 將 protobuf 回應轉換為 CommonResponse
                yield CommonResponse.from_pb2_model(response)

        @brick.input_streaming()
        async def input_streaming_handler(request_stream) -> CommonResponse:
            """異步流式輸入處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = common_pb2_grpc.CommonServiceStub(channel)
            async def grpc_request_generator():
                async for req in request_stream:
                    grpc_request = common_pb2.CommonRequest()
                    grpc_request.data.update(req.data)
                    yield grpc_request

            response = await grpc_client.InputStreaming(grpc_request_generator())

            return CommonResponse.from_pb2_model(response)

        @brick.bidi_streaming()
        async def bidi_streaming_handler(request_stream):
            """異步雙向流式處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = common_pb2_grpc.CommonServiceStub(channel)
            async def grpc_request_generator():
                async for req in request_stream:
                    grpc_request = common_pb2.CommonRequest()
                    grpc_request.data.update(req.data)
                    yield grpc_request

            async for response in grpc_client.BidiStreaming(grpc_request_generator()):
                yield CommonResponse.from_pb2_model(response)

        @brick.get_service_info()
        async def get_service_info_handler() -> ServiceInfoResponse:
            """異步服務信息處理器"""

            # 建立異步 gRPC 通道和客戶端
            channel = grpc.aio.insecure_channel(remote_address)
            grpc_client = common_pb2_grpc.CommonServiceStub(channel)
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

        # 儲存通道引用以便後續清理

        return brick
