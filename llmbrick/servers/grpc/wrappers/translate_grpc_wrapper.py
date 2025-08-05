import grpc

from google.protobuf import struct_pb2
from llmbrick.bricks.translate.base_translate import TranslateBrick
from llmbrick.protocols.grpc.common import common_pb2
from llmbrick.protocols.grpc.translate import translate_pb2, translate_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import ServiceInfoResponse
from llmbrick.protocols.models.bricks.translate_types import (
    TranslateRequest,
    TranslateResponse,
)
from llmbrick.core.error_codes import ErrorCodes

# /protocols/grpc/translate/translate.proto
# translate_pb2
# message TranslateRequest {
#   string text = 1;              // 用戶輸入的文本
#   string model_id = 2;         // 使用的翻譯模型ID
#   string target_language = 3; // 目標語言代碼，如 "en", "zh", "ja"
#   string client_id = 4;        // 識別呼叫系統
#   string session_id = 5;       // 識別連續對話會話
#   string request_id = 6;       // 唯一請求ID
#   string source_language = 7;  // 輸入文本的原始語言
# }


class TranslateGrpcWrapper(translate_pb2_grpc.TranslateServiceServicer):
    """
    TranslateGrpcWrapper: 異步 gRPC 服務包裝器，用於處理 Translate相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: TranslateBrick):
        if not isinstance(brick, TranslateBrick):
            raise TypeError("brick must be an instance of TranslateBrick")
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

    async def Unary(self, request: translate_pb2.TranslateRequest, context):
        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            request = TranslateRequest.from_pb2_model(request)
            result: TranslateResponse = await self.brick.run_unary(request)
            if not isinstance(result, TranslateResponse):
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details('Invalid unary response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = "Invalid unary response type!"
                error_data.detail = (
                    "The response from the brick is not of type TranslateResponse."
                )
                return translate_pb2.TranslateResponse(error=error_data)
            if result.error and result.error.code != ErrorCodes.SUCCESS:
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details(result.error.message)
                error_data.code = result.error.code
                error_data.message = result.error.message
                error_data.detail = result.error.detail
                return translate_pb2.TranslateResponse(error=error_data)

            response = translate_pb2.TranslateResponse(
                text=result.text,
                tokens=result.tokens,
                language_code=result.language_code,
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
            return translate_pb2.TranslateResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in Unary: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing Unary.",
            )
            return translate_pb2.TranslateResponse(error=error_data)

    async def OutputStreaming(self, request: translate_pb2.TranslateRequest, context):
        request = TranslateRequest.from_pb2_model(request)
        try:
            async for response in self.brick.run_output_streaming(request):
                error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
                if not isinstance(response, TranslateResponse):
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details('Invalid output streaming response type!')
                    error_data.code = grpc.StatusCode.INTERNAL.value[0]
                    error_data.message = "Invalid output streaming response type!"
                    error_data.detail = (
                        "The response from the brick is not of type TranslateResponse."
                    )
                    yield translate_pb2.TranslateResponse(error=error_data)
                    break
                if response.error and response.error.code != ErrorCodes.SUCCESS:
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details(response.error.message)
                    error_data.code = response.error.code
                    error_data.message = response.error.message
                    error_data.detail = response.error.detail
                    yield translate_pb2.TranslateResponse(error=error_data)
                    break
                yield translate_pb2.TranslateResponse(
                    text=response.text,
                    tokens=response.tokens,
                    language_code=response.language_code,
                    is_final=response.is_final,
                    error=error_data,
                )
        except NotImplementedError as ev:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.UNIMPLEMENTED.value[0],
                message=str(ev),
                detail="The requested operation is not implemented."
            )
            yield translate_pb2.TranslateResponse(error=error_data)
        except Exception as e:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing OutputStreaming."
            )
            yield translate_pb2.TranslateResponse(error=error_data)

    def register(self, server):
        translate_pb2_grpc.add_TranslateServiceServicer_to_server(self, server)
