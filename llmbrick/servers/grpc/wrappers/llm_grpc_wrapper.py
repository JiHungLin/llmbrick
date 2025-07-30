from typing import AsyncIterator
import grpc
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.grpc.llm import llm_pb2_grpc, llm_pb2
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/llm/llm.proto
# llm_pb2
# message Context {
#   string role = 1;              // 角色，如 "user", "system", "assistant"
#   string content = 2;           // 上下文內容
# }
# message LLMRequest {
#   string model_id = 1;          // 模型識別ID
#   string prompt = 2;            // 用戶輸入的提示文本
#   repeated Context context = 3; // 上下文信息列表
#   string client_id = 4;         // 識別呼叫系統/應用來源
#   string session_id = 5;        // 識別連續對話會話
#   string request_id = 6;        // 唯一請求ID
#   string source_language = 7;   // 輸入文本的原始語言
#   float temperature = 8;       // 溫度參數，用於控制生成文本的隨機性
#   int32 max_tokens = 9;        // 最大生成令牌數
# }
class LLMGrpcWrapper(llm_pb2_grpc.LLMServiceServicer):
    """
    LLMGrpcWrapper: 異步 gRPC 服務包裝器，用於處理LLM相關請求
    此類別繼承自llm_pb2_grpc.LLMServiceServicer，並實現了以下異步方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於生成模型回應。
    - OutputStreaming: 用於生成模型回應的流式輸出。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming
    """

    def __init__(self, brick: LLMBrick):
        if not isinstance(brick, LLMBrick):
            raise TypeError("brick must be an instance of LLMBrick")
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
        llm_pb2_grpc.add_LLMServiceServicer_to_server(self, server)