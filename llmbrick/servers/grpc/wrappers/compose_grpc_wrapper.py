from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.grpc.compose import compose_pb2_grpc

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