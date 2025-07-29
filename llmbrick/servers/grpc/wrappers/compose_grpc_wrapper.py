from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.grpc.compose import compose_pb2_grpc
class ComposeGrpcWrapper(compose_pb2_grpc.ComposeServiceServicer):
    """
    ComposeGrpcWrapper: gRPC服務包裝器，用於處理Compose相關請求
    此類別繼承自compose_pb2_grpc.ComposeServiceServicer, 並實現了以下方法：
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

    def GetServiceInfo(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()
    
    def Unary(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.run_unary(request)

    def OutputStreaming(self, request, context):
        # 假設 brick 有 output_streaming 方法
        for response in self.brick.run_output_streaming(request):
            yield response

    def register(self, server):
        compose_pb2_grpc.add_ComposeServiceServicer_to_server(self, server)