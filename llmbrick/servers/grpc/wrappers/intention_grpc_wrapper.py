from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.protocols.grpc.intention import intention_pb2_grpc

class IntentionGrpcWrapper(intention_pb2_grpc.IntentionServiceServicer):
    """
    IntentionGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Intention相關請求
    此類別繼承自intention_pb2_grpc.IntentionServiceServicer，並實現了以下異步方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """

    def __init__(self, brick: IntentionBrick):
        if not isinstance(brick, IntentionBrick):
            raise TypeError("brick must be an instance of IntentionBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        """異步獲取服務信息"""
        return await self.brick.run_get_service_info()
    
    async def Unary(self, request, context):
        """異步處理單次請求"""
        return await self.brick.run_unary(request)

    def register(self, server):
        intention_pb2_grpc.add_IntentionServiceServicer_to_server(self, server)