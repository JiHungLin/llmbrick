"""
主 gRPC Server，統一註冊各分類 Service Wrapper
"""
import grpc
from concurrent import futures

from llmbrick.servers.grpc.wrappers import register_to_grpc_server as register_grpc_service

class GrpcServer:
    def __init__(self, port=50051):
        self.server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))
        self.port = port

    def register_service(self, brick):
        register_grpc_service(self.server, brick)

    def start(self):
        self.server.add_insecure_port(f'[::]:{self.port}')
        self.server.start()
        print(f"gRPC server started on port {self.port}")
        self.server.wait_for_termination()