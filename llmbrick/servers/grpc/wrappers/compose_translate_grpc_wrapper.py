from llmbrick.bricks.compose.base_compose_translate import ComposeTranslateBrick
from llmbrick.protocols.grpc.translate import compose_translate_pb2_grpc
class ComposeTranslateGrpcWrapper(compose_translate_pb2_grpc.ComposeTranslateServiceServicer):
    """
    ComposeTranslateGrpcWrapper: gRPC服務包裝器，用於處理Compose Translate相關請求
    此類別繼承自compose_translate_pb2_grpc.ComposeTranslateServiceServicer, 並實現了以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - ComposeTranslate: 用於處理Compose Translate請求。
    - ComposeTranslateStream: 用於處理Compose Translate的流式請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - ComposeTranslate -> unary
    - ComposeTranslateStream -> output_streaming
    """

    def __init__(self, brick: ComposeTranslateBrick):
        if not isinstance(brick, ComposeTranslateBrick):
            raise TypeError("brick must be an instance of ComposeTranslateBrick")
        self.brick = brick
    
    def get_service_info(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()
    
    def ComposeTranslate(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.unary(request)
    
    def ComposeTranslateStream(self, request, context):
        # 假設 brick 有 output_streaming 方法
        for response in self.brick.output_streaming(request):
            yield response

    def register(self, server):
        compose_translate_pb2_grpc.add_ComposeTranslateServiceServicer_to_server(self, server)