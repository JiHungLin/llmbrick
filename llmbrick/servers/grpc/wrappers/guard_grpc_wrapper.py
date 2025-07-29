from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.protocols.grpc.guard import guard_pb2_grpc
class GuardGrpcWrapper(guard_pb2_grpc.GuardServiceServicer):
    """
    GuardGrpcWrapper: gRPC服務包裝器，用於處理Guard相關請求
    此類別繼承自guard_pb2_grpc.GuardServiceServicer，並實現了以下方法：
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
    
    def GetServiceInfo(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()
    
    def Unary(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.run_unary(request)

    def register(self, server):
        guard_pb2_grpc.add_GuardServiceServicer_to_server(self, server)