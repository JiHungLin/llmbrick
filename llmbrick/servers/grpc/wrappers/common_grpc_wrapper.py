from typing import AsyncIterator

import grpc
from google.protobuf import struct_pb2

from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.grpc.common import common_pb2, common_pb2_grpc
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest,
    CommonResponse,
    ServiceInfoResponse,
)
from llmbrick.core.error_codes import ErrorCodes

# common_pb2
# message CommonRequest {
#   google.protobuf.Struct data = 1;
# }


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

    async def Unary(self, request: common_pb2.CommonRequest, context):
        """異步處理單次請求"""
        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            request = CommonRequest.from_pb2_model(request)
            result: CommonResponse = await self.brick.run_unary(request)
            if not isinstance(result, CommonResponse):
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details('Invalid unary response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = "Invalid unary response type!"
                error_data.detail = (
                    "The response from the brick is not of type CommonResponse."
                )
                return common_pb2.CommonResponse(error=error_data)
            if result.error and result.error.code != ErrorCodes.SUCCESS:
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details(result.error.message)
                error_data.code = result.error.code
                error_data.message = result.error.message
                error_data.detail = result.error.detail
                return common_pb2.CommonResponse(error=error_data)

            data = struct_pb2.Struct()
            data.update(result.to_dict().get("data", {}))
            response = common_pb2.CommonResponse(data=data, error=error_data)

            return response
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = str(ev)
            error_data.detail = "The requested operation is not implemented."
            return common_pb2.CommonResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in Unary: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing Unary.",
            )
            return common_pb2.CommonResponse(error=error_data)
        
    # request is common_pb2.CommonRequest
    # request.data is struct_pb2.Struct
    async def OutputStreaming(self, request: common_pb2.CommonRequest, context):  # type: ignore
        """異步處理流式回應"""
        request = CommonRequest.from_pb2_model(request)
        try:
            async for response in self.brick.run_output_streaming(request):
                error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
                if not isinstance(response, CommonResponse):
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details('Invalid output streaming response type!')
                    error_data.code = grpc.StatusCode.INTERNAL.value[0]
                    error_data.message = "Invalid output streaming response type!"
                    error_data.detail = (
                        "The response from the brick is not of type CommonResponse."
                    )
                    yield common_pb2.CommonResponse(error=error_data)
                    break
                if response.error and response.error.code != ErrorCodes.SUCCESS:
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details(response.error.message)
                    error_data.code = response.error.code
                    error_data.message = response.error.message
                    error_data.detail = response.error.detail
                    yield common_pb2.CommonResponse(error=error_data)
                    break
                data = struct_pb2.Struct()
                data.update(response.to_dict().get("data", {}))
                yield common_pb2.CommonResponse(data=data, error=error_data)
        except NotImplementedError as ev:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.UNIMPLEMENTED.value[0],
                message=str(ev),
                detail="The requested operation is not implemented."
            )
            yield common_pb2.CommonResponse(error=error_data)
        except Exception as e:
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing OutputStreaming."
            )
            yield common_pb2.CommonResponse(error=error_data)

    async def InputStreaming(
        self, request_iterator: AsyncIterator[common_pb2.CommonRequest], context
    ):
        """異步處理流式輸入"""

        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield CommonRequest.from_pb2_model(request)

        error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
        try:
            result = await self.brick.run_input_streaming(async_request_iterator())
            if not isinstance(result, CommonResponse):
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details('Invalid input streaming response type!')
                error_data.code = grpc.StatusCode.INTERNAL.value[0]
                error_data.message = "Invalid input streaming response type!"
                error_data.detail = (
                    "The response from the brick is not of type CommonResponse."
                )
                return common_pb2.CommonResponse(error=error_data)
            if result.error and result.error.code != ErrorCodes.SUCCESS:
                # context.set_code(grpc.StatusCode.INTERNAL)
                # context.set_details(result.error.message)
                error_data.code = result.error.code
                error_data.message = result.error.message
                error_data.detail = result.error.detail
                return common_pb2.CommonResponse(error=error_data)
            data = struct_pb2.Struct()
            data.update(result.to_dict().get("data", {}))
            return common_pb2.CommonResponse(data=data, error=error_data)
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data.code = grpc.StatusCode.UNIMPLEMENTED.value[0]
            error_data.message = str(ev)
            error_data.detail = "The requested operation is not implemented."
            return common_pb2.CommonResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in InputStreaming: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing InputStreaming.",
            )
            return common_pb2.CommonResponse(error=error_data)

    async def BidiStreaming(
        self, request_iterator: AsyncIterator[common_pb2.CommonRequest], context
    ):
        """異步處理雙向流式請求"""

        # 將同步迭代器轉換為異步迭代器
        async def async_request_iterator():
            async for request in request_iterator:
                yield CommonRequest.from_pb2_model(request)

        try:
            async for response in self.brick.run_bidi_streaming(async_request_iterator()):
                error_data = common_pb2.ErrorDetail(code=ErrorCodes.SUCCESS, message="", detail="")
                if not isinstance(response, CommonResponse):
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details('Invalid bidi streaming response type!')
                    error_data.code = grpc.StatusCode.INTERNAL.value[0]
                    error_data.message = "Invalid bidi streaming response type!"
                    error_data.detail = (
                        "The response from the brick is not of type CommonResponse."
                    )
                    yield common_pb2.CommonResponse(error=error_data)
                    break
                if response.error and response.error.code != ErrorCodes.SUCCESS:
                    # context.set_code(grpc.StatusCode.INTERNAL)
                    # context.set_details(response.error.message)
                    error_data.code = response.error.code
                    error_data.message = response.error.message
                    error_data.detail = response.error.detail
                    yield common_pb2.CommonResponse(error=error_data)
                    break
                data = struct_pb2.Struct()
                data.update(response.to_dict().get("data", {}))
                yield common_pb2.CommonResponse(data=data, error=error_data)
        except NotImplementedError as ev:
            # context.set_code(grpc.StatusCode.UNIMPLEMENTED)
            # context.set_details(str(ev))
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.UNIMPLEMENTED.value[0],
                message=str(ev),
                detail="The requested operation is not implemented."
            )
            yield common_pb2.CommonResponse(error=error_data)
        except Exception as e:
            # context.set_code(grpc.StatusCode.INTERNAL)
            # context.set_details(f'Error in BidiStreaming: {str(e)}')
            error_data = common_pb2.ErrorDetail(
                code=grpc.StatusCode.INTERNAL.value[0],
                message=str(e),
                detail="An error occurred while processing BidiStreaming."
            )
            yield common_pb2.CommonResponse(error=error_data)

    def register(self, server):
        common_pb2_grpc.add_CommonServiceServicer_to_server(self, server)
