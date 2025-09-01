from my_brick import MyComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest
import asyncio

async def main():
    client_brick = MyComposeBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        desc_prefix="GRPCClient",
        default_format="csv",
        verbose=False
    )
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")

    print("=== Get Service Info ===")
    try:
        info = await client_brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        response = await client_brick.run_unary(request)
        print(f"Unary result: {response.output.get('count')}, desc: {response.output.get('desc')}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        async for response in client_brick.run_output_streaming(request):
            print(f"Stream output: {response.output}, error: {response.error}")
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())
