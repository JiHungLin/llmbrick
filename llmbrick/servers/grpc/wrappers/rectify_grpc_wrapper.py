from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.grpc.rectify import rectify_pb2_grpc
class RectifyGrpcWrapper(rectify_pb2_grpc.RectifyServiceServicer):
    """
    RectifyGrpcWrapper: gRPC服務包裝器，用於處理Rectify相關請求
    此類別繼承自rectify_pb2_grpc.RectifyServiceServicer，並實現了以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於處理Rectify請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    """

    def __init__(self, brick: RectifyBrick):
        if not isinstance(brick, RectifyBrick):
            raise TypeError("brick must be an instance of RectifyBrick")
        self.brick = brick

    def GetServiceInfo(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()

    def Unary(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.run_unary(request)

    def register(self, server):
        rectify_pb2_grpc.add_RectifyServiceServicer_to_server(self, server)