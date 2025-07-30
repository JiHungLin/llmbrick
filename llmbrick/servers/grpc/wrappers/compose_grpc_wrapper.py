from typing import AsyncIterator
import grpc
from llmbrick.bricks.compose.base_compose import ComposeBrick
from llmbrick.protocols.grpc.compose import compose_pb2_grpc, compose_pb2
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/compose/compose.proto
# compose_pb2
# message ComposeRequest {
#   repeated Document input_documents = 1;
#   string target_format = 2;    // 例: "json", "html", "markdown"
#   string client_id = 3;      // 識別呼叫系統/應用來源
#   string session_id = 4;     // 識別連續對話會話
#   string request_id = 5;     // 唯一請求ID，用於追蹤和除錯
#   string source_language = 6; // 輸入文件原始語言，如未提供可視為 target_language 相同
# }
class ComposeGrpcWrapper(compose_pb2_grpc.ComposeServiceServicer):
    """
    ComposeGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Compose相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: ComposeBrick):
        if not isinstance(brick, ComposeBrick):
            raise TypeError("brick must be an instance of ComposeBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        """異步獲取服務信息"""
        from llmbrick.protocols.grpc.common import common_pb2
        from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse
        result = await self.brick.run_get_service_info()
        error_data = common_pb2.ErrorDetail(code=0, message="", detail="")
        if result is None:
            context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            context.set_details('Service info not implemented!')
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = 'Service info not implemented!'
            error_data.detail = 'The brick did not implement service info.'
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        if not isinstance(result, ServiceInfoResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid service info response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = 'Invalid service info response type!'
            error_data.detail = 'The response from the brick is not of type ServiceInfoResponse.'
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        if result.error and result.error.code != 0:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            error_data.detail = result.error.detail
            return common_pb2.ServiceInfoResponse(error=error_data)
        response_dict = result.to_dict()
        response_dict["error"] = error_data
        response = common_pb2.ServiceInfoResponse(**response_dict)
        return response

    async def Unary(self, request: compose_pb2.ComposeRequest, context):
        """異步處理單次請求"""
        from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
        req = ComposeRequest.from_pb2_model(request)
        result = await self.brick.run_unary(req)
        error_data = compose_pb2.ErrorDetail(code=0, message="", detail="")
        if not isinstance(result, ComposeResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid unary response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = 'Invalid unary response type!'
            error_data.detail = 'The response from the brick is not of type ComposeResponse.'
            return compose_pb2.ComposeResponse(error=error_data)
        if result.error and result.error.code != 0:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            error_data.detail = result.error.detail
            return compose_pb2.ComposeResponse(error=error_data)
        output = struct_pb2.Struct()
        output.update(result.to_dict().get("output", {}))
        response = compose_pb2.ComposeResponse(output=output, error=error_data)
        return response

    async def OutputStreaming(self, request: compose_pb2.ComposeRequest, context):
        """異步處理流式回應"""
        from llmbrick.protocols.models.bricks.compose_types import ComposeRequest, ComposeResponse
        req = ComposeRequest.from_pb2_model(request)
        async for response in self.brick.run_output_streaming(req):
            error_data = compose_pb2.ErrorDetail(code=0, message="", detail="")
            if not isinstance(response, ComposeResponse):
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details('Invalid output streaming response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = 'Invalid output streaming response type!'
                error_data.detail = 'The response from the brick is not of type ComposeResponse.'
                yield compose_pb2.ComposeResponse(error=error_data)
                break
            if response.error and response.error.code != 0:
                context.set_code(grpc.StatusCode.INTERNAL)
                context.set_details(response.error.message)
                error_data.code = response.error.code
                error_data.message = response.error.message
                error_data.detail = response.error.detail
                yield compose_pb2.ComposeResponse(error=error_data)
                break
            output = struct_pb2.Struct()
            output.update(response.to_dict().get("output", {}))
            yield compose_pb2.ComposeResponse(output=output, error=error_data)

    def register(self, server):
        compose_pb2_grpc.add_ComposeServiceServicer_to_server(self, server)