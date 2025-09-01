import asyncio
from my_brick import MyLLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context

async def main():
    brick = MyLLMBrick(default_prompt="Hello LLM", model_id="local-llm", supported_languages=["en", "zh"])

    print("=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(info)
    except Exception as e:
        print(f"Error in get_service_info: {e}")

    print("\n=== Unary Method ===")
    try:
        print("Normal case:")
        req = LLMRequest(prompt="Test prompt", context=[Context(role="user", content="Hi")])
        resp = await brick.run_unary(req)
        print(resp)

        print("Error case (empty prompt):")
        req = LLMRequest(prompt="", context=[Context(role="user", content="Hi")])
        resp = await brick.run_unary(req)
        print(resp)

        print("Error case (context type error):")
        req = LLMRequest(prompt="Test", context=None)  # type: ignore
        resp = await brick.run_unary(req)
        print(resp)
    except Exception as e:
        print(f"Error in unary call: {e}")

    print("\n=== Output Streaming Method ===")
    try:
        print("Normal case:")
        req = LLMRequest(prompt="Stream this text", context=[])
        async for resp in brick.run_output_streaming(req):
            await asyncio.sleep(0.2)
            print(resp)

        print("Error case (empty prompt):")
        req = LLMRequest(prompt="", context=[])
        async for resp in brick.run_output_streaming(req):
            await asyncio.sleep(0.2)
            print(resp)
    except Exception as e:
        print(f"Error in output streaming: {e}")

if __name__ == "__main__":
    asyncio.run(main())