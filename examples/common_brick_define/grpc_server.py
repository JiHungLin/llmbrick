from my_brick import MyBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyBrick(
    my_init_data="Initialization data for gRPC server",
    res_prefix="From gRPC server"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
