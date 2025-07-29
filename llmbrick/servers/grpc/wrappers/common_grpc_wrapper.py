from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.grpc.common import common_pb2_grpc

class CommonGrpcWrapper(common_pb2_grpc.CommonServiceServicer):
    """
    CommonGrpcWrapper: gRPC服務包裝器，用於處理通用請求
    此類別繼承自common_pb2_grpc.CommonServiceServicer，並實現了以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Unary: 用於處理單次請求。
    - OutputStreaming: 用於處理流式回應。
    - InputStreaming: 用於處理流式輸入。
    - BidiStreaming: 用於處理雙向流式請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Unary -> unary
    - OutputStreaming -> output_streaming
    - InputStreaming -> input_streaming
    - BidiStreaming -> bidi_streaming
    """

    def __init__(self, brick: CommonBrick):
        if not isinstance(brick, CommonBrick):
            raise TypeError("brick must be an instance of CommonBrick")
        self.brick = brick

    def GetServiceInfo(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()

    def Unary(self, request, context):
        # 假設 brick 有 run_unary 方法
        return self.brick.run_unary(request)

    def OutputStreaming(self, request, context):
        # 假設 brick 有 run_output_streaming 方法
        for response in self.brick.run_output_streaming(request):
            yield response

    def InputStreaming(self, request_iterator, context):
        # 假設 brick 有 run_input_streaming 方法
        return self.brick.run_input_streaming(request_iterator)

    # TODO: 可能會有問題，因為這個方法需要處理雙向流式請求，待測試
    def BidiStreaming(self, request_iterator, context):
        # 假設 brick 有 run_bidi_streaming 方法
        return self.brick.run_bidi_streaming(request_iterator)

    def register(self, server):
        common_pb2_grpc.add_CommonServiceServicer_to_server(self, server)