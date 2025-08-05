from llmbrick.protocols.models.bricks.common_types import CommonRequest
from my_brick import MyBrick
import asyncio

async def main():
    my_brick = MyBrick(my_init_data="Initialization data for local use")

    print("=== Get Service Info ===")
    try:
        service_info = await my_brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Unary Method ===")
    # Example of running a unary method
    try:
        print("Normal case:")
        request = CommonRequest(data={"text": "Hello, World!"})
        response = await my_brick.run_unary(request)
        print(response)

        print("\nError case:")
        request = CommonRequest(data={"text": ""})  # Trigger error
        response = await my_brick.run_unary(request)
        print(response)
    except Exception as e:
        print(f"Error in unary call: {e}")

    print("\n\n=== Input Streaming Method ===")
    # Example of running an input streaming method
    try:
        print("Normal case:")
        async def input_stream():
            for i in range(3):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(f"Input {i + 1}")
                yield CommonRequest(data={"text": f"Input {i + 1}"})

        response = await my_brick.run_input_streaming(input_stream())
        print(response)

        print("\nError case:")
        async def error_input_stream():
            for i in range(3):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(f"Input {i + 1}")
                yield CommonRequest(data={"text": f"Input {i + 1}"})
            yield CommonRequest(data={})  # Empty input to trigger error

        response = await my_brick.run_input_streaming(error_input_stream())
        print(response)
    except Exception as e:
        print(f"Error in input streaming: {e}")

    print("\n\n=== Output Streaming Method ===")
    # Example of running an output streaming method
    try:
        print("Normal case:")
        request = CommonRequest(data={"text": "Streaming output"})
        async for response in my_brick.run_output_streaming(request):
            await asyncio.sleep(0.5)  # Simulate async operation
            print(response)

        print("\nError case:")
        request = CommonRequest(data={"text": ""})
        async for response in my_brick.run_output_streaming(request):
            await asyncio.sleep(0.5)  # Simulate async operation
            print(response)
    except Exception as e:
        print(f"Error in output streaming: {e}")

    print("\n\n=== Bidirectional Streaming Method ===")
    # Example of running a bidirectional streaming method
    try:
        print("Normal case:")
        async def bidi_input_stream():
            for i in range(3):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(f"Bidirectional input {i + 1}")
                yield CommonRequest(data={"text": f"Bidirectional input {i + 1}"})

        async for response in my_brick.run_bidi_streaming(bidi_input_stream()):
            await asyncio.sleep(0.5)  # Simulate async operation
            print(response)

        print("\nError case:")
        async def error_bidi_input_stream():
            for i in range(3):
                await asyncio.sleep(0.5)  # Simulate async operation
                print(f"Bidirectional input {i + 1}")
                yield CommonRequest(data={"text": f"Bidirectional input {i + 1}"})
            yield CommonRequest(data={})  # Empty input to trigger error

        async for response in my_brick.run_bidi_streaming(error_bidi_input_stream()):
            await asyncio.sleep(0.5)  # Simulate async operation
            print(response)
    except Exception as e:
        print(f"Error in bidirectional streaming: {e}")


if __name__ == "__main__":
    asyncio.run(main())
