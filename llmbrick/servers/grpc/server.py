"""
主 gRPC Server，統一註冊各分類 Service Wrapper (異步版本)
"""

import asyncio
from typing import Optional

import grpc

from llmbrick.core.brick import BaseBrick
from llmbrick.servers.grpc.wrappers import (
    register_to_grpc_server as register_grpc_service,
)
from llmbrick.utils.logging import logger


class GrpcServer:
    def __init__(self, port: int = 50051):
        self.server: Optional[grpc.aio.Server] = None
        self.port: int = port

    def register_service(self, brick: BaseBrick) -> None:
        if self.server is None:
            self.server = grpc.aio.server()
        register_grpc_service(self.server, brick)

    async def start(self) -> None:
        if self.server is None:
            self.server = grpc.aio.server()

        listen_addr = f"[::]:{self.port}"
        self.server.add_insecure_port(listen_addr)

        await self.server.start()
        logger.info(f"異步 gRPC server 已啟動，監聽端口 {self.port}")

        try:
            await self.server.wait_for_termination()
        except KeyboardInterrupt:
            print("收到中斷信號，正在關閉伺服器...")
            await self.stop()

    async def stop(self) -> None:
        if self.server:
            await self.server.stop(grace=5.0)
            logger.info("gRPC server 已停止")

    def run(self) -> None:
        """同步包裝器，用於向後相容"""
        asyncio.run(self.start())
