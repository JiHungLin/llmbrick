from llmbrick.protocols.grpc.llm import llm_pb2_grpc
from llmbrick.protocols.grpc.llm import llm_pb2

class LLMGrpcWrapper(llm_pb2_grpc.LLMServiceServicer):
    def __init__(self, brick):
        self.brick = brick

    def GenerateResponse(self, request, context):
        # 假設 brick 有 run_generateresponse 方法
        return self.brick.run_generateresponse(request, context)

    def GenerateResponseStream(self, request, context):
        # 假設 brick 有 run_generateresponsestream 方法
        yield from self.brick.run_generateresponsestream(request, context)

    def register(self, server):
        llm_pb2_grpc.add_LLMServiceServicer_to_server(self, server)