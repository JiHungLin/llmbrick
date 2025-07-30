from typing import AsyncIterator
import grpc
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.grpc.retrieval import retrieval_pb2_grpc, retrieval_pb2
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/retrieval/retrieval.proto
# retrieval_pb2
# message RetrievalRequest {
#   string query = 1;              // 用戶輸入的查詢文本
#   int32 max_results = 2;        // 最大返回結果數量
#   string client_id = 3;         // 識別呼叫系統
#   string session_id = 4;        // 識別連續對話會話
#   string request_id = 5;        // 唯一請求ID
#   string source_language = 6;   // 輸入文本的原始語言
# }

class RetrievalGrpcWrapper(retrieval_pb2_grpc.RetrievalServiceServicer):
    """
    RetrievalGrpcWrapper: 異步 gRPC 服務包裝器，用於處理檢索相關請求
    此類別繼承自retrieval_pb2_grpc.RetrievalServiceServicer，並實現了以下異步方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於處理檢索請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """

    def __init__(self, brick: RetrievalBrick):
        if not isinstance(brick, RetrievalBrick):
            raise TypeError("brick must be an instance of RetrievalBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        """異步獲取服務信息"""
        return await self.brick.run_get_service_info()

    async def Unary(self, request, context):
        """異步處理單次請求"""
        return await self.brick.run_unary(request)

    def register(self, server):
        retrieval_pb2_grpc.add_RetrievalServiceServicer_to_server(self, server)