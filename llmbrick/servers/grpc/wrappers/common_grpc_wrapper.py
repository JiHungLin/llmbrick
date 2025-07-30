from typing import AsyncIterator
import grpc
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.grpc.common import common_pb2_grpc, common_pb2
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse, ServiceInfoResponse
from google.protobuf import struct_pb2

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

    async def GetServiceInfo(self, _, context):
        """異步獲取服務信息"""
        result = await self.brick.run_get_service_info()
        if result is None:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details('Service info not implemented!')
            raise NotImplementedError('Service info not implemented!')
        if not isinstance(result, ServiceInfoResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid service info response type!')
            raise TypeError('Invalid service info response type!')  
        response = common_pb2.ServiceInfoResponse(result.to_dict())
        # response.service_name = result.get("service_name", "")
        # response.version = result.get("version", "")
        # for model in result.get("models", []):
        #     model_info = response.models.add()
        #     model_info.name = model.get("name", "")
        #     model_info.version = model.get("version", "")
        #     # 根據 ModelInfo 的定義補充其他欄位

        # if "error" in result and result["error"] is not None:
        #     response.error.code = result["error"].get("code", 0)
        #     response.error.message = result["error"].get("message", "")

        return response

    async def Unary(self, request: CommonRequest, context):
        """異步處理單次請求"""
        result: CommonResponse = await self.brick.run_unary(request)
        error_data = common_pb2.ErrorDetail()
        if not isinstance(result, CommonResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid unary response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = 'Invalid unary response type!'
            error_data.detail = 'The response from the brick is not of type CommonResponse.'
            return common_pb2.CommonResponse(error=error_data)

        data = struct_pb2.Struct()
        data.update(result.to_dict().get("data", {}))

        error_data.code = 0
        error_data.message = ""
        error_data.detail = ""
        response = common_pb2.CommonResponse(data=data, error=error_data)

        return response

    async def OutputStreaming(self, request: CommonRequest, context):
        """異步處理流式回應"""
        async for response in self.brick.run_output_streaming(request):
            yield response

    async def InputStreaming(self, request_iterator: AsyncIterator[CommonRequest], context):
        """異步處理流式輸入"""
        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield request
        
        return await self.brick.run_input_streaming(async_request_iterator())

    async def BidiStreaming(self, request_iterator: AsyncIterator[CommonRequest], context):
        """異步處理雙向流式請求"""
        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield request
        
        async for response in self.brick.run_bidi_streaming(async_request_iterator()):
            yield response

    def register(self, server):
        common_pb2_grpc.add_CommonServiceServicer_to_server(self, server)