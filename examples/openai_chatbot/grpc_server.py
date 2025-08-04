from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.servers.grpc.server import GrpcServer
import os

async def run_openai_chatbot():
    grpc_server = GrpcServer(port=50051)
    openai_brick =  OpenAIGPTBrick(
            model_id="gpt-4o",  # 默認使用 GPT-4o 模型
            api_key=os.getenv("OPENAI_API_KEY")
        )
    grpc_server.register_service(openai_brick)

    print("Starting OpenAI Chatbot gRPC server...")
    await grpc_server.start()

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_openai_chatbot())
    print("OpenAI Chatbot gRPC server is running.")