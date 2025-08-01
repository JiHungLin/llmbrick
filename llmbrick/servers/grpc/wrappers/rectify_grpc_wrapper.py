import grpc

from llmbrick.bricks.rectify.base_rectify import RectifyBrick
from llmbrick.protocols.grpc.common import common_pb2
from llmbrick.protocols.grpc.rectify import rectify_pb2, rectify_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse
from llmbrick.protocols.models.bricks.rectify_types import (
    RectifyRequest,
    RectifyResponse,
)

# /protocols/grpc/rectify/rectify.proto
# rectify_pb2
# message RectifyRequest {
#   string text = 1;              // 用戶輸入的文本
#   string client_id = 2;         // 識別呼叫系統
#   string session_id = 3;        // 識別連續對話會話
#   string request_id = 4;        // 唯一請求ID
#   string source_language = 5;   // 輸入文本的原始語言
# }


class RectifyGrpcWrapper(rectify_pb2_grpc.RectifyServiceServicer):
    """
    RectifyGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Rectify相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: RectifyBrick):
        if not isinstance(brick, RectifyBrick):
            raise TypeError("brick must be an instance of RectifyBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        result = await self.brick.run_get_service_info()
        error_data = common_pb2.ErrorDetail(code=0, message="", detail="")
        if result is None:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details('Service info not implemented!')
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = "Service info not implemented!"
            error_data.detail = "The brick did not implement service info."
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        if not isinstance(result, ServiceInfoResponse):
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details('Invalid service info response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = "Invalid service info response type!"
            error_data.detail = (
                "The response from the brick is not of type ServiceInfoResponse."
            )
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        if result.error and result.error.code != 0:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            error_data.detail = result.error.detail
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        response_dict = result.to_dict()
        response_dict["error"] = error_data
        response = common_pb2.ServiceInfoResponse(**response_dict)
        return response

    async def Unary(self, request: rectify_pb2.RectifyRequest, context):
        req = RectifyRequest(
            text=request.text,
            client_id=request.client_id,
            session_id=request.session_id,
            request_id=request.request_id,
            source_language=request.source_language,
        )
        result = await self.brick.run_unary(req)
        error_data = common_pb2.ErrorDetail(code=0, message="", detail="")
        if not isinstance(result, RectifyResponse):
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details('Invalid unary response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = "Invalid unary response type!"
            error_data.detail = (
                "The response from the brick is not of type RectifyResponse."
            )
            return rectify_pb2.RectifyResponse(error=error_data)
        if result.error and result.error.code != 0:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            print("***********************")
            print(error_data)
            print(result)
            error_data.detail = result.error.detail
            response = rectify_pb2.RectifyResponse(error=error_data)
            return response
        response = rectify_pb2.RectifyResponse(
            corrected_text=result.corrected_text, error=error_data
        )
        return response

    def register(self, server):
        rectify_pb2_grpc.add_RectifyServiceServicer_to_server(self, server)
