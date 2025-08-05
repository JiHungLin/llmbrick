"""
簡化版 gRPC Server，專注於解決優雅關閉問題
"""

import asyncio
import signal
import sys
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
        self._pending_bricks: list[BaseBrick] = []
        self._is_stopping = False

    def register_service(self, brick: BaseBrick) -> None:
        """註冊服務到待處理列表"""
        self._pending_bricks.append(brick)

    async def start(self) -> None:
        """啟動 gRPC 服務器"""
        # 創建服務器
        self.server = grpc.aio.server()
        
        # 註冊所有服務
        for brick in self._pending_bricks:
            register_grpc_service(self.server, brick)
        self._pending_bricks.clear()

        # 綁定端口並啟動
        listen_addr = f"[::]:{self.port}"
        self.server.add_insecure_port(listen_addr)
        await self.server.start()
        
        logger.info(f"異步 gRPC server 已啟動，監聽端口 {self.port}")
        # 等待終止
        try:
            await self.server.wait_for_termination()
        except Exception as e:
            if not self._is_stopping:
                logger.error(f"服務器運行時發生錯誤: {e}")
                raise

    async def stop(self) -> None:
        """停止服務器"""
        if self.server and not self._is_stopping:
            self._is_stopping = True
            logger.info("正在停止 gRPC 服務器...")
            
            try:
                await self.server.stop(grace=3.0)
                logger.info("gRPC server 已停止")
            except Exception as e:
                logger.error(f"停止服務器時發生錯誤: {e}")
            finally:
                self.server = None
                self._is_stopping = False

    def run(self) -> None:
        """運行服務器的主要入口"""
        async def _run_with_signals():
            # 設置信號處理（僅適用於 Unix）
            if sys.platform != 'win32':
                loop = asyncio.get_running_loop()
                
                def handle_signal():
                    if not self._is_stopping:
                        logger.info("收到中斷信號，開始停止服務器...")
                        loop.create_task(self.stop())
                
                for sig in (signal.SIGTERM, signal.SIGINT):
                    loop.add_signal_handler(sig, handle_signal)
            
            # 啟動服務器
            await self.start()
        
        try:
            asyncio.run(_run_with_signals())
        except KeyboardInterrupt:
            # 在 Windows 上或信號處理器未能捕獲的情況下
            logger.info("\n收到中斷信號，正在停止...")
        except Exception as e:
            logger.error(f"服務器發生未預期錯誤: {e}")
            raise
        finally:
            # 確保清理資源
            if self.server and not self._is_stopping:
                try:
                    asyncio.run(self.stop())
                except Exception as e:
                    logger.error(f"最終清理時發生錯誤: {e}")