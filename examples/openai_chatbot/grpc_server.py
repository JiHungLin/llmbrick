from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.servers.grpc.server import GrpcServer
import os

grpc_server = GrpcServer(port=50051)
openai_brick =  OpenAIGPTBrick(
        model_id="gpt-4o",  # 默認使用 GPT-4o 模型
        api_key=os.getenv("OPENAI_API_KEY")
    )
grpc_server.register_service(openai_brick)

if __name__ == "__main__":
    print("Starting OpenAI Chatbot gRPC server...")
    grpc_server.run()