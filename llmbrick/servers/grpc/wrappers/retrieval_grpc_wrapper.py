from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.grpc.retrieval import retrieval_pb2_grpc
class RetrievalGrpcWrapper(retrieval_pb2_grpc.RetrievalServiceServicer):
    """
    RetrievalGrpcWrapper: gRPC服務包裝器，用於處理檢索相關請求
    此類別繼承自retrieval_pb2_grpc.RetrievalServiceServicer，並實現了以下方法：
    - GetServiceInfo: 用於獲取服務信息。
    - Retrieve: 用於處理檢索請求。

    gRPC服務與Brick的Handler對應表： (gRPC方法 -> Brick Handler)
    - GetServiceInfo -> get_service_info
    - Retrieve -> unary

    """

    def __init__(self, brick: RetrievalBrick):
        if not isinstance(brick, RetrievalBrick):
            raise TypeError("brick must be an instance of RetrievalBrick")
        self.brick = brick
    
    def get_service_info(self, request, context):
        # 假設 brick 有 run_get_service_info 方法
        return self.brick.run_get_service_info()

    def Retrieve(self, request, context):
        # 假設 brick 有 unary 方法
        return self.brick.unary(request)

    def register(self, server):
        retrieval_pb2_grpc.add_RetrievalServiceServicer_to_server(self, server)