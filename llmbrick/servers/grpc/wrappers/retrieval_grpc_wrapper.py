from typing import AsyncIterator
import grpc
from llmbrick.bricks.retrieval.base_retrieval import RetrievalBrick
from llmbrick.protocols.grpc.retrieval import retrieval_pb2_grpc, retrieval_pb2
from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse
from google.protobuf import struct_pb2

# /protocols/grpc/retrieval/retrieval.proto
# retrieval_pb2
# message RetrievalRequest {
#   string query = 1;              // 用戶輸入的查詢文本
#   int32 max_results = 2;        // 最大返回結果數量
#   string client_id = 3;         // 識別呼叫系統
#   string session_id = 4;        // 識別連續對話會話
#   string request_id = 5;        // 唯一請求ID
#   string source_language = 6;   // 輸入文本的原始語言
# }

class RetrievalGrpcWrapper(retrieval_pb2_grpc.RetrievalServiceServicer):
    """
    RetrievalGrpcWrapper: 異步 gRPC 服務包裝器，用於處理檢索相關請求
    以 common_grpc_wrapper.py 為基礎，統一異步方法的錯誤處理與型別檢查。
    """

    def __init__(self, brick: RetrievalBrick):
        if not isinstance(brick, RetrievalBrick):
            raise TypeError("brick must be an instance of RetrievalBrick")
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
        if result.error and result.error.code != 0:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            error_data.detail = result.error.detail
            response = common_pb2.ServiceInfoResponse(error=error_data)
            return response
        response_dict = result.to_dict()
        response_dict["error"] = error_data
        response = common_pb2.ServiceInfoResponse(**response_dict)
        return response

    async def Unary(self, request: retrieval_pb2.RetrievalRequest, context):
        from llmbrick.protocols.models.bricks.retrieval_types import RetrievalRequest, RetrievalResponse
        req = RetrievalRequest.from_pb2_model(request)
        result = await self.brick.run_unary(req)
        error_data = retrieval_pb2.ErrorDetail(code=0, message="", detail="")
        if not isinstance(result, RetrievalResponse):
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details('Invalid unary response type!')
            error_data.code = grpc.StatusCode.INTERNAL.value[0]
            error_data.message = 'Invalid unary response type!'
            error_data.detail = 'The response from the brick is not of type RetrievalResponse.'
            return retrieval_pb2.RetrievalResponse(error=error_data)
        if result.error and result.error.code != 0:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(result.error.message)
            error_data.code = result.error.code
            error_data.message = result.error.message
            error_data.detail = result.error.detail
            response = retrieval_pb2.RetrievalResponse(error=error_data)
            return response
        # documents: List[Document]
        documents_pb = []
        for d in result.documents:
            doc_pb = retrieval_pb2.Document(
                doc_id=d.doc_id,
                title=d.title,
                snippet=d.snippet,
                score=d.score,
                metadata=d.metadata
            )
            documents_pb.append(doc_pb)
        response = retrieval_pb2.RetrievalResponse(documents=documents_pb, error=error_data)
        return response

    def register(self, server):
        retrieval_pb2_grpc.add_RetrievalServiceServicer_to_server(self, server)