import grpc

from google.protobuf import struct_pb2
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.grpc.common import common_pb2
from llmbrick.protocols.grpc.llm import llm_pb2, llm_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse
from llmbrick.core.error_codes import ErrorCodes

# /protocols/grpc/llm/llm.proto
# llm_pb2
# message Context {
#   string role = 1;              // 角色，如 "user", "system", "assistant"
#   string content = 2;           // 上下文內容
# }
# message LLMRequest {
#   string model_id = 1;          // 模型識別ID
#   string prompt = 2;            // 用戶輸入的提示文本
#   repeated Context context = 3; // 上下文信息列表
#   string client_id = 4;         // 識別呼叫系統/應用來源
#   string session_id = 5;        // 識別連續對話會話
#   string request_id = 6;        // 唯一請求ID
#   string source_language = 7;   // 輸入文本的原始語言
#   float temperature = 8;       // 溫度參數，用於控制生成文本的隨機性
#   int32 max_tokens = 9;        // 最大生成令牌數
# }
class LLMGrpcWrapper(llm_pb2_grpc.LLMServiceServicer):
    """
    LLMGrpcWrapper: 異步 gRPC 服務包裝器，用於處理LLM相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: LLMBrick):
        if not isinstance(brick, LLMBrick):
            raise TypeError("brick must be an instance of LLMBrick")
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

    async def Unary(self, request: llm_pb2.LLMRequest, context):
        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            request = LLMRequest.from_pb2_model(request)
            result: LLMResponse = await self.brick.run_unary(request)
            if not isinstance(result, LLMResponse):
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details('Invalid unary response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = "Invalid unary response type!"
                error_data.detail = (
                    "The response from the brick is not of type LLMResponse."
                )
                return llm_pb2.LLMResponse(error=error_data)
            if result.error and result.error.code != ErrorCodes.SUCCESS:
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details(result.error.message)
                error_data.code = result.error.code
                error_data.message = result.error.message
                error_data.detail = result.error.detail
                return llm_pb2.LLMResponse(error=error_data)

            response = llm_pb2.LLMResponse(
                text=result.text,
                tokens=result.tokens,
                is_final=result.is_final,
                error=error_data,
            )
            return response
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = str(ev)
            error_data.detail = "The requested operation is not implemented."
            return llm_pb2.LLMResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in Unary: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing Unary.",
            )
            return llm_pb2.LLMResponse(error=error_data)


    async def OutputStreaming(self, request: llm_pb2.LLMRequest, context):
        request = LLMRequest.from_pb2_model(request)
        try:
            async for response in self.brick.run_output_streaming(request):
                error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
                if not isinstance(response, LLMResponse):
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details('Invalid output streaming response type!')
                    error_data.code = grpc.StatusCode.INTERNAL.value[0]
                    error_data.message = "Invalid output streaming response type!"
                    error_data.detail = (
                        "The response from the brick is not of type LLMResponse."
                    )
                    yield llm_pb2.LLMResponse(error=error_data)
                    break
                if response.error and response.error.code != ErrorCodes.SUCCESS:
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details(response.error.message)
                    error_data.code = response.error.code
                    error_data.message = response.error.message
                    error_data.detail = response.error.detail
                    yield llm_pb2.LLMResponse(error=error_data)
                    break
                yield llm_pb2.LLMResponse(
                    text=response.text,
                    tokens=response.tokens,
                    is_final=response.is_final,
                    error=error_data,
                )
        except NotImplementedError as ev:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.UNIMPLEMENTED.value[0],
                message=str(ev),
                detail="The requested operation is not implemented."
            )
            yield llm_pb2.LLMResponse(error=error_data)
        except Exception as e:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing OutputStreaming."
            )
            yield llm_pb2.LLMResponse(error=error_data)

    def register(self, server):
        llm_pb2_grpc.add_LLMServiceServicer_to_server(self, server)
