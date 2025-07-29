from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.grpc.llm import llm_pb2_grpc

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