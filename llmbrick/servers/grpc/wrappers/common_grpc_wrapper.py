from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.grpc.common import common_pb2_grpc

class CommonGrpcWrapper(common_pb2_grpc.CommonServiceServicer):
    """
    CommonGrpcWrapper: 異步 gRPC 服務包裝器，用於處理通用請求
    此類別繼承自common_pb2_grpc.CommonServiceServicer，並實現了以下異步方法：
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

    async def InputStreaming(self, request_iterator, context):
        """異步處理流式輸入"""
        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield request
        
        return await self.brick.run_input_streaming(async_request_iterator())

    async def BidiStreaming(self, request_iterator, context):
        """異步處理雙向流式請求"""
        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield request
        
        async for response in self.brick.run_bidi_streaming(async_request_iterator()):
            yield response

    def register(self, server):
        common_pb2_grpc.add_CommonServiceServicer_to_server(self, server)