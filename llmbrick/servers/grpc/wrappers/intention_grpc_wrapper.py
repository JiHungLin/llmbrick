from typing import AsyncIterator
import grpc
from llmbrick.bricks.intention.base_intention import IntentionBrick
from llmbrick.protocols.grpc.intention import intention_pb2_grpc, intention_pb2
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/intention/intention.proto
# intention_pb2
# message IntentionRequest {
#   string text = 1;              // 用戶輸入的文本
#   string client_id = 2;         // 識別呼叫系統
#   string session_id = 3;        // 識別連續對話會話
#   string request_id = 4;        // 唯一請求ID
#   string source_language = 5;   // 輸入文本的原始語言
# }

class IntentionGrpcWrapper(intention_pb2_grpc.IntentionServiceServicer):
    """
    IntentionGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Intention相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: IntentionBrick):
        if not isinstance(brick, IntentionBrick):
            raise TypeError("brick must be an instance of IntentionBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
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
        response_dict = result.to_dict()
        response_dict["error"] = error_data
        response = common_pb2.ServiceInfoResponse(**response_dict)
        return response

    async def Unary(self, request: intention_pb2.IntentionRequest, context):
        from llmbrick.protocols.models.bricks.intention_types import IntentionRequest, IntentionResponse
        req = IntentionRequest(
            text=request.text,
            client_id=request.client_id,
            session_id=request.session_id,
            request_id=request.request_id,
            source_language=request.source_language,
        )
        result = await self.brick.run_unary(req)
        error_data = intention_pb2.ErrorDetail(code=0, message="", detail="")
        if not isinstance(result, IntentionResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid unary response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = 'Invalid unary response type!'
            error_data.detail = 'The response from the brick is not of type IntentionResponse.'
            return intention_pb2.IntentionResponse(error=error_data)
        # results: List[IntentionResult]
        results_pb = []
        for r in result.results:
            res_pb = intention_pb2.IntentionResult(
                intent_category=r.intent_category,
                confidence=r.confidence
            )
            results_pb.append(res_pb)
        response = intention_pb2.IntentionResponse(results=results_pb, error=error_data)
        return response

    def register(self, server):
        intention_pb2_grpc.add_IntentionServiceServicer_to_server(self, server)