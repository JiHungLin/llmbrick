"""
整合 OpenAI GPT Brick 與 SSE Server 的完整示例
"""

import asyncio
import os
from typing import AsyncGenerator, Dict, Any

from llmbrick.servers.sse.server import SSEServer
from llmbrick.servers.sse.config import SSEServerConfig
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.http.conversation import (
    ConversationSSERequest,
    ConversationSSEResponse,
    SSEResponseMetadata,
    SSEContext
)
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, Context
from llmbrick.core.exceptions import ValidationException
from llmbrick.utils.logging import logger
from llmbrick.protocols.models.bricks.common_types import ErrorDetail

class ChatHandler:
    """處理聊天請求的類別，整合 OpenAI GPT Brick 與 SSE 響應"""
    
    def __init__(self):
        # 初始化 OpenAI GPT Brick
        # self.llm = OpenAIGPTBrick(
        #     model_id="gpt-4o",  # 默認使用 GPT-4o 模型
        #     api_key=os.getenv("OPENAI_API_KEY")
        # )
        self.llm = OpenAIGPTBrick.toGrpcClient(remote_address="127.0.0.1:50051")
        # 追蹤對話 session
        self.sessions: Dict[str, list] = {}
    
    async def handle_chat(self, request: ConversationSSERequest) -> AsyncGenerator[ConversationSSEResponse, None]:
        """
        處理聊天請求並產生 SSE 回應
        
        Args:
            request: ConversationSSERequest 請求對象
        """
        try:
            # 解析請求
            logger.info(f"Received request: {request}")
            session_id = request.session_id or "default"

            # 檢查 session 和模型
            if session_id not in self.sessions:
                self.sessions[session_id] = []
            if request.model not in self.llm.supported_models:
                raise ValidationException(f"不支援的模型: {request.model}")
            
            # 準備 LLM 請求
            llm_request = LLMRequest(
                model_id=request.model,
                prompt=request.messages[-1].content,  # 最後一條消息作為當前提示
                context=[
                    Context(role=msg.role, content=msg.content)
                    for msg in request.messages[:-1]  # 之前的消息作為上下文
                ],
                temperature=request.temperature or 0.7,
                max_tokens=request.max_tokens or 1000
            )
            
            # 首先發送開始事件
            yield ConversationSSEResponse(
                id=f"{session_id}-start",
                type="start",
                model=request.model,
                progress="IN_PROGRESS",
                metadata=SSEResponseMetadata(
                    attachments=[{"type": "session", "id": session_id}]
                )
            )
            
            # 使用 OpenAI GPT Brick 生成回應
            response_id = f"{session_id}-{len(self.sessions[session_id])}"
            chunk_count = 0
            
            try:
                async for chunk in self.llm.run_output_streaming(llm_request):
                    if chunk.error and chunk.error.code != ErrorCodes.SUCCESS:
                        # 處理 LLM 錯誤
                        yield ConversationSSEResponse(
                            id=f"{response_id}-error",
                            type="error",
                            text=f"LLM 錯誤: {chunk.error.message}",
                            progress="DONE",
                            metadata=SSEResponseMetadata(
                                attachments=[{"type": "error", "code": chunk.error.code}]
                            )
                        )
                        return
                        
                    # 發送文本塊
                    if chunk.text:
                        yield ConversationSSEResponse(
                            id=f"{response_id}-{chunk_count}",
                            type="text",
                            text=chunk.text,
                            progress="IN_PROGRESS",
                            metadata=SSEResponseMetadata(
                                attachments=[{"type": "chunk", "number": chunk_count}]
                            ),
                            context=SSEContext(conversation_id=session_id)
                        )
                        chunk_count += 1
                
                # 保存對話記錄
                if chunk_count > 0:
                    self.sessions[session_id].append({
                        "role": "assistant",
                        "content": llm_request.prompt
                    })
                
                # 發送完成事件
                yield ConversationSSEResponse(
                    id=f"{response_id}-done",
                    type="done",
                    progress="DONE",
                    metadata=SSEResponseMetadata(
                        attachments=[
                            {"type": "session", "id": session_id},
                            {"type": "summary", "total_chunks": chunk_count}
                        ]
                    ),
                    context=SSEContext(conversation_id=session_id)
                )
                
            except Exception as e:
                logger.error(f"生成回應時發生錯誤: {str(e)}")
                yield ConversationSSEResponse(
                    id=f"{response_id}-error",
                    type="error",
                    text=f"生成回應時發生錯誤: {str(e)}",
                    progress="DONE",
                    metadata=SSEResponseMetadata(
                        attachments=[{"type": "error", "message": str(e)}]
                    ),
                    context=SSEContext(conversation_id=response_id)
                )
                
        except ValidationException as ve:
            # 處理驗證錯誤
            yield ConversationSSEResponse(
                id="validation-error",
                type="error",
                text=f"驗證錯誤: {str(ve)}",
                progress="DONE",
                metadata=SSEResponseMetadata(
                    attachments=[{"type": "error", "code": "validation_error", "message": str(ve)}]
                )
            )
            
        except Exception as e:
            # 處理其他錯誤
            logger.error(f"處理請求時發生錯誤: {str(e)}")
            yield ConversationSSEResponse(
                id="general-error",
                type="error",
                text=f"處理請求時發生錯誤: {str(e)}",
                progress="DONE",
                metadata=SSEResponseMetadata(
                    attachments=[{"type": "error", "code": "general_error", "message": str(e)}]
                )
            )


def main():
    """主函數：設置並啟動 SSE 服務器"""
    
    # 配置 SSE 服務器
    config = SSEServerConfig(
        host="127.0.0.1",
        port=8000,
        debug_mode=True,
        allowed_models=["gpt-4o", "gpt-3.5-turbo"],
        max_message_length=4000,
        enable_request_logging=True,
        enable_validation_details=True
    )
    
    # 創建服務器實例
    server = SSEServer(config=config, enable_test_page=True)
    handler = ChatHandler()
    
    # 註冊處理函數
    server.set_handler(handler.handle_chat)
    
    # 啟動服務器
    logger.info(f"啟動 SSE 服務器於 http://{config.host}:{config.port}/")
    logger.info("可以通過瀏覽器訪問測試頁面")
    server.run()


if __name__ == "__main__":
    main()