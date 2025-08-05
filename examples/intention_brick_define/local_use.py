from llmbrick.core.error_codes import ErrorCodes
from my_brick import MyIntentionBrick
from llmbrick.protocols.models.bricks.intention_types import IntentionRequest
import asyncio

async def main():
    # 初始化 IntentionBrick
    my_brick = MyIntentionBrick(
        model_name="demo_model",
        res_prefix="local_test",
        verbose=False
    )

    print("=== Get Service Info ===")
    try:
        service_info = await my_brick.run_get_service_info()
        print(service_info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n\n=== Normal Cases ===")
    # 測試不同類型的意圖
    test_texts = [
        "你好，請問一下",  # 預期: greet
        "我想要查詢資料",  # 預期: query
        "謝謝，再見",      # 預期: goodbye
        "我需要幫助",      # 預期: help
        "隨機文本測試"     # 預期: unknown
    ]

    for text in test_texts:
        try:
            print(f"\nInput text: {text}")
            request = IntentionRequest(text=text, client_id="test_client")
            response = await my_brick.run_unary(request)
            if response.error and response.error.code != ErrorCodes.SUCCESS:
                print(f"Error: {response.error.message}")
            else:
                result = response.results[0]
                print(f"Intent: {result.intent_category}")
                print(f"Confidence: {result.confidence}")
        except Exception as e:
            print(f"Error processing request: {e}")

    print("\n\n=== Error Cases ===")
    # 測試錯誤情況 - 空文本
    try:
        print("\nTesting empty text:")
        request = IntentionRequest(text="", client_id="test_client")
        response = await my_brick.run_unary(request)
        if response.error:
            print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

    # 測試錯誤情況 - None 文本
    try:
        print("\nTesting None text:")
        request = IntentionRequest(text=None, client_id="test_client")
        response = await my_brick.run_unary(request)
        if response.error:
            print(f"Error (expected): {response.error.message}")
    except Exception as e:
        print(f"Error processing request: {e}")

if __name__ == "__main__":
    asyncio.run(main())