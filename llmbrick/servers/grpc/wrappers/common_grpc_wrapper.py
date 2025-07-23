from llmbrick.protocols.grpc.common import common_pb2_grpc
from llmbrick.protocols.grpc.common import common_pb2

class CommonGrpcWrapper(common_pb2_grpc.CommonServiceServicer):
    def __init__(self, brick):
        self.brick = brick

    def ServerStreaming(self, request, context):
        # 假設 brick 有 run_serverstreaming 方法
        yield from self.brick.run_serverstreaming(request, context)

    def UnaryCall(self, request, context):
        # 假設 brick 有 run_unarycall 方法
        return self.brick.run_unarycall(request, context)

    def register(self, server):
        common_pb2_grpc.add_CommonServiceServicer_to_server(self, server)