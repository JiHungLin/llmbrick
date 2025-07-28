from llmbrick.core.brick import BaseBrick
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest,
    CommonResponse,
)
from llmbrick.protocols.grpc.common import common_pb2_grpc, common_pb2
import grpc
from google.protobuf.json_format import ParseDict


class CommonBrick(BaseBrick[CommonRequest, CommonResponse]):
    """
    CommonBrick: 基於 BaseBrick 的通用服務，提供基本的請求和回應結構。
    gRPC服務類型為'Common'，用於處理通用請求。
    gRPC提中以下方法：
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
    grpc_service_type = "Common"

    @classmethod
    def toGRPCClient(cls, remote_address: str):
        """
        將 IntentionGuardBrick 轉換為 gRPC 客戶端。
        """
        channel = grpc.insecure_channel(remote_address)
        grpc_client: common_pb2_grpc.CommonServiceStub = common_pb2_grpc.CommonServiceStub(channel)
        from google.protobuf import struct_pb2

        brick = cls()
        @brick.unary
        def unary_handler(request: CommonRequest) -> CommonResponse:
            input = request.to_dict()
            s = struct_pb2.Struct()
            s.update(input)
            return grpc_client.Unary(s)

        @brick.output_streaming
        def output_streaming_handler(request: CommonRequest) -> grpc.ResponseStream[CommonResponse]:
            s = struct_pb2.Struct()
            s.update(request.to_dict())
            yield grpc_client.OutputStreaming(s)

        @brick.input_streaming
        def input_streaming_handler(request_stream: grpc.RequestStream[CommonRequest]) -> CommonResponse:
            # 將 request_stream 轉換為 gRPC 可用的 generator
            def grpc_request_generator():
                for req in request_stream:
                    # 假設 CommonRequest 有 to_dict 方法，轉換為 protobuf Struct
                    s = struct_pb2.Struct()
                    s.update(req.to_dict())
                    yield s

            return grpc_client.InputStreaming(grpc_request_generator())

        @brick.bidi_streaming
        def bidi_streaming_handler(request_stream: grpc.RequestStream[CommonRequest]) -> grpc.ResponseStream[CommonResponse]:
            yield grpc_client.BidiStreaming(request_stream)

        @brick.get_service_info
        def get_service_info_handler(request: common_pb2.GetServiceInfoRequest) -> common_pb2.GetServiceInfoResponse:
            return grpc_client.GetServiceInfo(request)

        return brick
