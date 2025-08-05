from llmbrick.protocols.models.bricks.translate_types import TranslateRequest
from my_brick import MyTranslateBrick
import asyncio

async def main():
    brick = MyTranslateBrick(model_name="demo_model", default_target_language="zh", verbose=True)

    print("=== Get Service Info ===")
    try:
        service_info = await brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Unary Method ===")
    try:
        print("Normal case:")
        request = TranslateRequest(
            text="Hello, world!",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r1",
            source_language="en",
        )
        response = await brick.run_unary(request)
        print(response)

        print("\nError case:")
        request = TranslateRequest(
            text="",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r2",
            source_language="en",
        )
        response = await brick.run_unary(request)
        print(response)
    except Exception as e:
        print(f"Error in unary call: {e}")

    print("\n\n=== Output Streaming Method ===")
    try:
        print("Normal case:")
        request = TranslateRequest(
            text="This is a streaming test",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r3",
            source_language="en",
        )
        async for resp in brick.run_output_streaming(request):
            await asyncio.sleep(0.3)
            print(resp)

        print("\nError case:")
        request = TranslateRequest(
            text="",
            model_id="demo_model",
            target_language="zh",
            client_id="test",
            session_id="s1",
            request_id="r4",
            source_language="en",
        )
        async for resp in brick.run_output_streaming(request):
            await asyncio.sleep(0.3)
            print(resp)
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())