from my_brick import MyRectifyBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyRectifyBrick(
    mode="upper",
    supported_languages=["en", "zh"],
    description="RectifyBrick gRPC server"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
