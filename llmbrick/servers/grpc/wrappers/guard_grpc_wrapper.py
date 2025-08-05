import grpc

from google.protobuf import struct_pb2
from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.protocols.grpc.common import common_pb2
from llmbrick.protocols.grpc.guard import guard_pb2, guard_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse
from llmbrick.core.error_codes import ErrorCodes

# /protocols/grpc/guard/guard.proto
# guard_pb2
# message GuardRequest {
#   string text = 1;              // 用戶輸入的文本
#   string client_id = 2;         // 識別呼叫系統
#   string session_id = 3;        // 識別連續對話會話
#   string request_id = 4;        // 唯一請求ID
#   string source_language = 5;   // 輸入文本的原始語言
# }


class GuardGrpcWrapper(guard_pb2_grpc.GuardServiceServicer):
    """
    GuardGrpcWrapper: 異步 gRPC 服務包裝器，用於處理Guard相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: GuardBrick):
        if not isinstance(brick, GuardBrick):
            raise TypeError("brick must be an instance of GuardBrick")
        self.brick = brick

    async def GetServiceInfo(self, request, context):
        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            result = await self.brick.run_get_service_info()
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
            if result.error and result.error.code != ErrorCodes.SUCCESS:
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
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = str(ev)
            error_data.detail = "The requested operation is not implemented."
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in GetServiceInfo: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing GetServiceInfo.",
            )
            return common_pb2.ServiceInfoResponse(error=error_data)

    async def Unary(self, request: guard_pb2.GuardRequest, context):
        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            request = GuardRequest.from_pb2_model(request)
            result: GuardResponse = await self.brick.run_unary(request)
            if not isinstance(result, GuardResponse):
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details('Invalid unary response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = "Invalid unary response type!"
                error_data.detail = (
                    "The response from the brick is not of type GuardResponse."
                )
                return guard_pb2.GuardResponse(error=error_data)
            if result.error and result.error.code != ErrorCodes.SUCCESS:
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details(result.error.message)
                error_data.code = result.error.code
                error_data.message = result.error.message
                error_data.detail = result.error.detail
                return guard_pb2.GuardResponse(error=error_data)

            results_pb = []
            for r in result.results:
                res_pb = guard_pb2.GuardResult(
                    is_attack=r.is_attack, confidence=r.confidence, detail=r.detail
                )
                results_pb.append(res_pb)
            response = guard_pb2.GuardResponse(results=results_pb, error=error_data)
            return response
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = str(ev)
            error_data.detail = "The requested operation is not implemented."
            return guard_pb2.GuardResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in Unary: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing Unary.",
            )
            return guard_pb2.GuardResponse(error=error_data)

    def register(self, server):
        guard_pb2_grpc.add_GuardServiceServicer_to_server(self, server)
