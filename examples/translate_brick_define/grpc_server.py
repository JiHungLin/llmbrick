from my_brick import MyTranslateBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50071)
my_brick = MyTranslateBrick(
    model_name="demo_model",
    default_target_language="zh",
    verbose=True,
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()