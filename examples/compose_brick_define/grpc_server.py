from my_brick import MyComposeBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyComposeBrick(desc_prefix="GRPCServer", default_format="xml", verbose=True)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
