from typing import AsyncIterator
import grpc
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.protocols.grpc.guard import guard_pb2_grpc, guard_pb2
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/guard/guard.proto
# guard_pb2
# message GuardRequest {
#   string text = 1;              // 用戶輸入的文本
#   string client_id = 2;         // 識別呼叫系統
#   string session_id = 3;        // 識別連續對話會話
#   string request_id = 4;        // 唯一請求ID
#   string source_language = 5;   // 輸入文本的原始語言
# }


class GuardGrpcWrapper(guard_pb2_grpc.GuardServiceServicer):
    """
    GuardGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Guard相關請求
    此類別繼承自guard_pb2_grpc.GuardServiceServicer，並實現了以下異步方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """

    def __init__(self, brick: GuardBrick):
        if not isinstance(brick, GuardBrick):
            raise TypeError("brick must be an instance of GuardBrick")
        self.brick = brick
    
    async def GetServiceInfo(self, request, context):
        """異步獲取服務信息"""
        return await self.brick.run_get_service_info()
    
    async def Unary(self, request, context):
        """異步處理單次請求"""
        return await self.brick.run_unary(request)

    def register(self, server):
        guard_pb2_grpc.add_GuardServiceServicer_to_server(self, server)