from llmbrick.bricks.intention_guard.base_intention_guard import IntentionGuardBrick
from llmbrick.protocols.grpc.intention import intention_guard_pb2_grpc
class IntentionGuardGrpcWrapper(intention_guard_pb2_grpc.IntentionGuardServiceServicer):
    """
    IntentionGuardGrpcWrapper: gRPC服務包裝器，用於處理Intention Guard相關請求
    此類別繼承自intention_guard_pb2_grpc.IntentionGuardServiceServicer，並實現了以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於檢查用戶意圖。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary

    """

    def __init__(self, brick: IntentionGuardBrick):
        if not isinstance(brick, IntentionGuardBrick):
            raise TypeError("brick must be an instance of IntentionGuardBrick")
        self.brick = brick
    
    def get_service_info(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()
    
    def Unary(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.unary(request)

    def register(self, server):
        intention_guard_pb2_grpc.add_IntentionGuardServiceServicer_to_server(self, server)