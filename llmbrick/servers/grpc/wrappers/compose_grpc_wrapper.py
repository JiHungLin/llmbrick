from typing import AsyncIterator
import grpc
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.grpc.compose import compose_pb2_grpc, compose_pb2
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/compose/compose.proto
# compose_pb2
# message ComposeRequest {
#   repeated Document input_documents = 1;
#   string target_format = 2;    // 例: "json", "html", "markdown"
#   string client_id = 3;      // 識別呼叫系統/應用來源
#   string session_id = 4;     // 識別連續對話會話
#   string request_id = 5;     // 唯一請求ID，用於追蹤和除錯
#   string source_language = 6; // 輸入文件原始語言，如未提供可視為 target_language 相同
# }
class ComposeGrpcWrapper(compose_pb2_grpc.ComposeServiceServicer):
    """
    ComposeGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Compose相關請求
    此類別繼承自compose_pb2_grpc.ComposeServiceServicer, 並實現了以下異步方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於處理Compose請求。
    - OutputStreaming: 用於處理Compose的流式請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming
    """

    def __init__(self, brick: ComposeBrick):
        if not isinstance(brick, ComposeBrick):
            raise TypeError("brick must be an instance of ComposeBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        """異步獲取服務信息"""
        return await self.brick.run_get_service_info()
    
    async def Unary(self, request, context):
        """異步處理單次請求"""
        return await self.brick.run_unary(request)

    async def OutputStreaming(self, request, context):
        """異步處理流式回應"""
        async for response in self.brick.run_output_streaming(request):
            yield response

    def register(self, server):
        compose_pb2_grpc.add_ComposeServiceServicer_to_server(self, server)