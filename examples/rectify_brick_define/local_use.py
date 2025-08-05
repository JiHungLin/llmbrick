from llmbrick.protocols.models.bricks.rectify_types import RectifyRequest
from my_brick import MyRectifyBrick
import asyncio

async def main():
    # 建立 MyRectifyBrick 實例，可自訂 mode
    brick = MyRectifyBrick(mode="upper", supported_languages=["en", "zh"], description="Demo rectify brick")

    print("=== Get Service Info ===")
    try:
        service_info = await brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Unary Method ===")
    # 正常案例
    try:
        print("Normal case:")
        request = RectifyRequest(
            text="Hello, World!",
            client_id="cli",
            session_id="s1",
            request_id="r1",
            source_language="en"
        )
        response = await brick.run_unary(request)
        print(response)

        print("\nError case:")
        error_request = RectifyRequest(
            text="",
            client_id="cli",
            session_id="s1",
            request_id="r2",
            source_language="en"
        )
        error_response = await brick.run_unary(error_request)
        print(error_response)
    except Exception as e:
        print(f"Error in unary call: {e}")

if __name__ == "__main__":
    asyncio.run(main())