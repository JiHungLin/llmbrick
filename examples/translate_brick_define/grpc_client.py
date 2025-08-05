from my_brick import MyTranslateBrick
from llmbrick.protocols.models.bricks.translate_types import TranslateRequest

if __name__ == "__main__":
    # 建立 gRPC client
    my_brick = MyTranslateBrick.toGrpcClient(remote_address="127.0.0.1:50071", verbose=False)
    import asyncio

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            service_info = await my_brick.run_get_service_info()
            print(service_info)
        asyncio.run(example())

    run_get_service_info_example()

    print("\n\n=== Unary Method ===")
    def run_unary_example(is_test_error=False):
        async def example():
            request = TranslateRequest(
                text="Hello, gRPC!" if not is_test_error else "",
                model_id="demo_model",
                target_language="zh",
                client_id="test",
                session_id="s1",
                request_id="r1" if not is_test_error else "r2",
                source_language="en",
            )
            response = await my_brick.run_unary(request)
            print(response)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n\n=== Output Streaming Method ===")
    def run_output_streaming_example(is_test_error=False):
        async def example():
            request = TranslateRequest(
                text="Streaming gRPC test" if not is_test_error else "",
                model_id="demo_model",
                target_language="zh",
                client_id="test",
                session_id="s1",
                request_id="r3" if not is_test_error else "r4",
                source_language="en",
            )
            async for resp in my_brick.run_output_streaming(request):
                await asyncio.sleep(0.3)
                print(resp)
        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)
    print("Error case:")
    run_output_streaming_example(is_test_error=True)