import asyncio
from my_brick import MyComposeBrick
from llmbrick.protocols.models.bricks.compose_types import ComposeRequest

async def main():
    brick = MyComposeBrick(desc_prefix="DemoPrefix", default_format="yaml", verbose=False)
    docs = [
        type("Doc", (), {"doc_id": "1", "title": "A", "snippet": "", "score": 1.0, "metadata": {}})(),
        type("Doc", (), {"doc_id": "2", "title": "B", "snippet": "", "score": 2.0, "metadata": {}})(),
    ]
    request = ComposeRequest(input_documents=docs, target_format="json")

    print("=== Unary Method ===")
    try:
        response = await brick.run_unary(request)
        print(f"Unary result: {response.output.get('count')}, desc: {response.output.get('desc')}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        async for response in brick.run_output_streaming(request):
            print(f"Stream output: {response.output}, error: {response.error}")
    except Exception as e:
        print(f"Error in output streaming: {e}")

    print("\n=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

if __name__ == "__main__":
    asyncio.run(main())