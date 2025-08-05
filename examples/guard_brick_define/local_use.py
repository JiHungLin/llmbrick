import asyncio
from my_brick import MyGuardBrick
from llmbrick.protocols.models.bricks.guard_types import GuardRequest

async def main():
    brick = MyGuardBrick(sensitivity=0.5, verbose=True)

    print("=== Unary Method ===")
    try:
        print("Normal case:")
        request = GuardRequest(text="This is a normal message.")
        response = await brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")

        print("\nAttack case:")
        request = GuardRequest(text="This is an attack!")
        response = await brick.run_unary(request)
        print(f"Is attack: {response.results[0].is_attack}, confidence: {response.results[0].confidence}, detail: {response.results[0].detail}, error: {response.error}")
    except Exception as e:
        print(f"Error in unary: {e}")

    print("\n=== Get Service Info ===")
    try:
        info = await brick.run_get_service_info()
        print(f"Service name: {info.service_name}, version: {info.version}, info: {info.error.message}")
    except Exception as e:
        print(f"Error in get_service_info: {e}")

if __name__ == "__main__":
    asyncio.run(main())