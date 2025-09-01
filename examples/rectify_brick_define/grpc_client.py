from my_brick import MyRectifyBrick
from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest

if __name__ == "__main__":
    my_brick = MyRectifyBrick.toGrpcClient(remote_address="127.0.0.1:50051")

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
            if not is_test_error:
                request = RectifyRequest(
                    text="Hello, gRPC!",
                    client_id="cli",
                    session_id="s1",
                    request_id="r1",
                    source_language="en"
                )
            else:
                request = RectifyRequest(
                    text="",
                    client_id="cli",
                    session_id="s1",
                    request_id="r2",
                    source_language="en"
                )
            response = await my_brick.run_unary(request)
            print(response)
        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)
    print("Error case:")
    run_unary_example(is_test_error=True)
