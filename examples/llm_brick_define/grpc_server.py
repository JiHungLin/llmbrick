from my_brick import MyLLMBrick
from llmbrick.servers.grpc.server import GrpcServer

grpc_server = GrpcServer(port=50051)
my_brick = MyLLMBrick(
    default_prompt="gRPC default prompt",
    model_id="grpc-llm",
    supported_languages=["en", "zh"],
    version="1.0.0",
    description="gRPC LLMBrick example"
)
grpc_server.register_service(my_brick)

if __name__ == "__main__":
    grpc_server.run()
