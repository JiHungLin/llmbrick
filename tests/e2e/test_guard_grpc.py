"""
GuardBrick gRPC 功能測試
"""

import asyncio
from typing import Any, AsyncIterator

import pytest
import pytest_asyncio

from llmbrick.bricks.guard.base_guard import GuardBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.guard_types import GuardRequest, GuardResponse, GuardResult
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ModelInfo, ServiceInfoResponse
from llmbrick.servers.grpc.server import GrpcServer
from llmbrick.core.error_codes import ErrorCodes

class _TestGuardBrick(GuardBrick):
    """測試用的 Guard Brick"""

    @unary_handler
    async def unary_handler(self, request: GuardRequest) -> GuardResponse:
        await asyncio.sleep(0.05)
        is_attack = "attack" in (request.text or "").lower()
        result = GuardResult(
            is_attack=is_attack,
            confidence=0.95 if is_attack else 0.05,
            detail="Attack detected" if is_attack else "Safe"
        )
        return GuardResponse(
            results=[result],
            error=ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        )

    @get_service_info_handler
    async def get_service_info_handler(self) -> ServiceInfoResponse:
        await asyncio.sleep(0.01)
        error = ErrorDetail(code=ErrorCodes.SUCCESS, message="No error")
        return ServiceInfoResponse(
            service_name="TestGuardBrick",
            version="2.1.0",
            models=[
                ModelInfo(
                    model_id="guard-test",
                    version="2.1.0",
                    supported_languages=["zh", "en"],
                    support_streaming=False,
                    description="test"
                )
            ],
            error=error,
        )

@pytest.mark.asyncio
async def test_async_grpc_server_startup() -> None:
    """測試異步 gRPC 伺服器啟動"""
    print("測試 GuardBrick gRPC 伺服器啟動...")

    # 建立測試 Brick
    llm_brick = _TestGuardBrick()
    # 建立伺服器
    server = GrpcServer(port=50066)
    server.register_service(llm_brick)
    # 啟動伺服器
    assert len(server._pending_bricks) > 0
    assert server.port == 50066
    print("✓ GuardBrick 伺服器建立成功")

@pytest_asyncio.fixture
async def grpc_server() -> AsyncIterator[None]:
    guard_brick = _TestGuardBrick(verbose=False)
    server = GrpcServer(port=50068)
    server.register_service(guard_brick)
    server_task = asyncio.create_task(server.start())
    await asyncio.sleep(0.5)  # 等 server 啟動
    yield
    await server.stop()
    server_task.cancel()
    try:
        await server_task
    except asyncio.CancelledError:
        pass

@pytest_asyncio.fixture
async def grpc_client(grpc_server: Any) -> AsyncIterator[_TestGuardBrick]:
    client_brick = _TestGuardBrick.toGrpcClient(
        remote_address="127.0.0.1:50068", verbose=False
    )
    yield client_brick

@pytest.mark.asyncio
async def test_unary(grpc_client: _TestGuardBrick) -> None:
    print("== 測試 GuardBrick Unary 方法 ==")
    request = GuardRequest(text="This is a safe message")
    response = await grpc_client.run_unary(request)
    assert response is not None
    assert response.results[0].is_attack is False

    attack_request = GuardRequest(text="This is an attack!")
    attack_response = await grpc_client.run_unary(attack_request)
    assert attack_response.results[0].is_attack is True

@pytest.mark.asyncio
async def test_get_service_info(grpc_client: _TestGuardBrick) -> None:
    info = await grpc_client.run_get_service_info()
    assert info.service_name == "TestGuardBrick"
    assert info.version == "2.1.0"
    assert isinstance(info.models, list)
    assert info.models[0].model_id == "guard-test"

@pytest.mark.asyncio
async def test_error_handling(grpc_client: _TestGuardBrick) -> None:
    # 模擬異常情境
    class ErrorGuardBrick(GuardBrick):
        @unary_handler
        async def error_handler(self, request: GuardRequest) -> GuardResponse:
            if request.text == "raise":
                raise ValueError("Test exception")
            elif request.text == "error":
                return GuardResponse(
                    results=[],
                    error=ErrorDetail(code=ErrorCodes.INTERNAL_ERROR, message="Business logic error")
                )
            else:
                return GuardResponse(
                    results=[GuardResult(is_attack=False, confidence=1.0, detail="ok")],
                    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
                )
    # 直接用本地模式測試異常
    brick = ErrorGuardBrick(verbose=False)
    normal_request = GuardRequest(text="normal")
    response = await brick.run_unary(normal_request)
    assert response.error.code == ErrorCodes.SUCCESS
    error_request = GuardRequest(text="error")
    response = await brick.run_unary(error_request)
    assert response.error.code == ErrorCodes.INTERNAL_ERROR
    exception_request = GuardRequest(text="raise")
    with pytest.raises(ValueError):
        await brick.run_unary(exception_request)
