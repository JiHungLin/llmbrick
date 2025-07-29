"""
主 gRPC Server，統一註冊各分類 Service Wrapper (異步版本)
"""
import grpc
import asyncio
from typing import Optional

from llmbrick.servers.grpc.wrappers import register_to_grpc_server as register_grpc_service

class GrpcServer:
    def __init__(self, port=50051):
        self.server: Optional[grpc.aio.Server] = None
        self.port = port

    def register_service(self, brick):
        if self.server is None:
            self.server = grpc.aio.server()
        register_grpc_service(self.server, brick)

    async def start(self):
        if self.server is None:
            self.server = grpc.aio.server()
            
        listen_addr = f'[::]:{self.port}'
        self.server.add_insecure_port(listen_addr)
        
        await self.server.start()
        print(f"異步 gRPC server 已啟動，監聽端口 {self.port}")
        
        try:
            await self.server.wait_for_termination()
        except KeyboardInterrupt:
            print("收到中斷信號，正在關閉伺服器...")
            await self.stop()

    async def stop(self):
        if self.server:
            await self.server.stop(grace=5.0)
            print("gRPC server 已停止")

    def run(self):
        """同步包裝器，用於向後相容"""
        asyncio.run(self.start())