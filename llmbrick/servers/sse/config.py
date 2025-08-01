from typing import List, Optional
from pydantic import BaseModel, Field


class SSEServerConfig(BaseModel):
    """SSE Server配置"""
    
    # 基本配置
    host: str = Field(default="0.0.0.0", description="Server host")
    port: int = Field(default=8000, description="Server port")
    prefix: str = Field(default="", description="API路徑前綴")
    chat_completions_path: str = Field(default="/chat/completions", description="聊天API路徑")
    
    # 驗證配置
    allowed_models: List[str] = Field(
        default=["gpt-4o", "gpt-3.5-turbo", "sonar"], 
        description="允許的模型清單"
    )
    max_message_length: int = Field(default=10000, description="單則訊息最大長度")
    max_messages_count: int = Field(default=100, description="對話最大訊息數量")
    
    # 開發者體驗配置
    debug_mode: bool = Field(default=False, description="除錯模式，提供更詳細的錯誤訊息")
    enable_request_logging: bool = Field(default=True, description="啟用請求日誌")
    enable_validation_details: bool = Field(default=True, description="啟用詳細驗證錯誤訊息")
    
    # 效能配置
    request_timeout: int = Field(default=30, description="請求超時時間(秒)")
    max_concurrent_connections: int = Field(default=100, description="最大並發連線數")
    
    class Config:
        extra = "forbid"