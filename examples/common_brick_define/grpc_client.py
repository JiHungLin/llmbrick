
from my_brick import MyBrick, CommonRequest
from llmbrick.bricks.common import CommonBrick


if __name__ == "__main__":
    my_brick = CommonBrick.toGrpcClient(remote_address="127.0.0.1:50051")
    import asyncio

    print("=== Get Service Info ===")
    def run_get_service_info_example():
        async def example():
            service_info = await my_brick.run_get_service_info()
            print(service_info)

        asyncio.run(example())

    run_get_service_info_example()

    print("\n\n=== Unary Method ===")
    # Example of running a unary method
    def run_unary_example(is_test_error=False):
        
        async def example():
            request = CommonRequest(data={"text": "Hello, World!"})
            if is_test_error:
                request.data["text"] = ""  # Trigger error
            response = await my_brick.run_unary(request)
            print(response)

        asyncio.run(example())

    print("Normal case:")
    run_unary_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_unary_example(is_test_error=True)

    print("\n\n=== Input Streaming Method ===")
    # Example of running an input streaming method
    def run_input_streaming_example(is_test_error=False):
        async def example():
            async def input_stream():
                for i in range(3):
                    await asyncio.sleep(0.5)  # Simulate async operation
                    print(f"Input {i + 1}")
                    yield CommonRequest(data={"text": f"Input {i + 1}"})
                yield CommonRequest(data={})  # Simulating an empty input

            response = await my_brick.run_input_streaming(input_stream())
            print(response)

        asyncio.run(example())

    print("Normal case:")
    run_input_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_input_streaming_example(is_test_error=True)

    print("\n\n=== Output Streaming Method ===")
    # Example of running an output streaming method
    def run_output_streaming_example(is_test_error=False):
        async def example():
            request = CommonRequest(data={"text": "Streaming output"})
            if is_test_error:
                request.data["text"] = ""
            async for response in my_brick.run_output_streaming(request):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(response)

        asyncio.run(example())

    print("Normal case:")
    run_output_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_output_streaming_example(is_test_error=True)


    print("\n\n=== Bidirectional Streaming Method ===")
    # Example of running a bidirectional streaming method
    def run_bidi_streaming_example(is_test_error=False):
        async def example():
            async def bidi_input_stream():
                for i in range(3):
                    await asyncio.sleep(0.5)  # Simulate async operation
                    print(f"Bidirectional input {i + 1}")
                    yield CommonRequest(data={"text": f"Bidirectional input {i + 1}"})
                yield CommonRequest(data={})

            async for response in my_brick.run_bidi_streaming(bidi_input_stream()):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(response)

        asyncio.run(example())

    print("Normal case:")
    run_bidi_streaming_example(is_test_error=False)  # Normal case
    print("Error case:")
    run_bidi_streaming_example(is_test_error=True)
