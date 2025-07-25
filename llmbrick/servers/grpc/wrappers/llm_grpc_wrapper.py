from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.grpc.llm import llm_pb2_grpc
class LLMGrpcWrapper(llm_pb2_grpc.LLMServiceServicer):
    """
    LLMGrpcWrapper: gRPC服務包裝器，用於處理LLM相關請求
    此類別繼承自llm_pb2_grpc.LLMServiceServicer，並實現了以下方法：
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
    
    def get_service_info(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()

    def Unary(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.unary(request)

    def OutputStreaming(self, request, context):
        # 假設 brick 有 output_streaming 方法
        for response in self.brick.output_streaming(request):
            yield response

    def register(self, server):
        llm_pb2_grpc.add_LLMServiceServicer_to_server(self, server)