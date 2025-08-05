from my_brick import MyLLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

if __name__ == "__main__":
    import asyncio

    # 建立 gRPC client
    my_brick = MyLLMBrick.toGrpcClient(
        remote_address="127.0.0.1:50051",
        default_prompt="gRPC client prompt",
        model_id="grpc-client-llm"
    )

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            info = await my_brick.run_get_service_info()
            print(info)
        asyncio.run(example())

    run_get_service_info_example()

    print("\n=== Unary Method ===")
    def run_unary_example(is_test_error=False):
        async def example():
            if is_test_error:
                req = LLMRequest(prompt="", context=[Context(role="user", content="")])
            else:
                req = LLMRequest(prompt="Hello from gRPC client", context=[Context(role="user", content="Hi")])
            resp = await my_brick.run_unary(req)
            print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n=== Output Streaming Method ===")
    def run_output_streaming_example(is_test_error=False):
        async def example():
            if is_test_error:
                req = LLMRequest(prompt="", context=[])
            else:
                req = LLMRequest(prompt="Stream this via gRPC", context=[])
            async for resp in my_brick.run_output_streaming(req):
                await asyncio.sleep(0.2)
                print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)
    print("Error case:")
    run_output_streaming_example(is_test_error=True)
