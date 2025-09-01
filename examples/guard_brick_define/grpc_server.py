from my_brick import MyGuardBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyGuardBrick(sensitivity=0.7, verbose=True)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
