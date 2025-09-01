from my_brick import MyRetrievalBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyRetrievalBrick(
    index_name="grpc_index"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
