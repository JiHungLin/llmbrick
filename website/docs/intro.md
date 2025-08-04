---
sidebar_position: 1
---

# LLMBrick 框架介紹

## 框架概述

LLMBrick 是一個專注於 LLM（大型語言模型）應用開發的框架，其核心理念為：所有功能皆以 Brick（積木）組件為單元，協定明確、組裝彈性，方便擴充與客製化。這種設計讓開發者能夠像堆疊積木一般，輕鬆構建複雜的 LLM 應用。

## 文件目的與使用對象

本文件主要服務於以下對象：
- 🎯 **應用開發者**：希望快速開發 LLM 應用的工程師
- 🔧 **Brick 開發者**：想要開發新組件或擴展現有功能的開發者
- 🏗️ **系統架構師**：需要設計大規模 LLM 系統的架構師

無論您是剛接觸 LLM 開發，還是經驗豐富的開發者，本文件都能助您快速上手並深入理解 LLMBrick 框架。

## 文件結構

本文件分為兩大部分：

### 1. 快速上手（Quickstart）
為新手提供最短路徑的入門指南：
- 基礎安裝與配置
- 第一個 LLMBrick 應用
- 常見使用場景範例

### 2. 詳細文件（Documents）
深入的技術文件與進階指南：
- 架構設計原理
- API 文件
- 最佳實踐指南
- 擴展開發教程

## 核心特色

### 🧱 模組化設計
- 所有功能以 Brick 為基本單位
- 組件可插拔、可重組
- 支援多層次組裝
- 單一 Brick 可輕鬆轉換為獨立服務

<a href="/img/BricksUML.svg" target="_blank" rel="noopener noreferrer">
    <img
        src="/img/BricksUML.svg"
        alt="Brick Types Architecture"
        style={{ maxWidth: "100%", height: "auto", display: "block", margin: "auto" }}
    />
</a>

```python
# 模組化設計範例 pseudocode
from llmbricl.bricks.guard.base_guard import GuardBrick
from llmbricl.bricks.rectify.base_rectify import RectifyBrick
from llmbricl.bricks.intention.base_intention import IntentionBrick
from llmbricl.bricks.llm.base_llm import LLMBrick

...
guard_brick = GuardBrick()
rectify_brick = RectifyBrick()
intention_brick = IntentionBrick()
llm_brick = LLMBrick()

async def main():
    result1 = guard_brick.run_unary(guard_request)
    rectify_text = rectify_brick.run_unary(rectify_request)
    intention_result = intention_brick.run_unary(rectify_text)
    async for answer in llm_brick.run_output_streaming(question_context)
        yield answer

```

### 📑 明確協定定義
- 所有 Brick 之間的資料流有明確協定
- 型別與錯誤處理標準化
- 透過gRPC跨語言、跨協議整合便利
- 支援本地呼叫與遠端gRPC調用

<a href="/img/BrickDataType.svg" target="_blank" rel="noopener noreferrer">
    <img
    src="/img/BrickDataType.svg"
    alt="Brick Types Architecture"
    style={{ maxWidth: "100%", height: "auto", display: "block", margin: "auto" }}
    />
</a>

```python
# 協定定義範例 pseudocode
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest, CommonResponse, ErrorDetail
)

async def process(request: CommonRequest) -> CommonResponse:
    return CommonResponse(
        data={"result": "處理完成"},
        error=ErrorDetail(code=0, message="Success")
    )
```

#### LLMBrick 框架中的每個 Brick 組件都需實作以下標準函式，確保資料流與協定一致：

- `run_unary(request)`：單次請求/回應，適用於一般處理流程。
- `run_input_streaming(request_stream)`：輸入串流，處理多筆輸入資料。
- `run_output_streaming(request)`：輸出串流，回傳多筆結果（如 LLM 逐步產生答案）。
- `run_bidi_streaming(request_stream)`：雙向串流，支援持續資料交換。
- `run_get_service_info()`：查詢 Brick 服務資訊（如型別、版本、能力）。
- `@func_decorator`：使用裝飾模式靈活定義

```python
class ExampleBrick(CommonBrick):
    async def run_unary(self, request: CommonRequest) -> CommonResponse: ...
    async def run_input_streaming(self, request_stream: AsyncIterable[CommonRequest]) -> CommonResponse: ...
    async def run_output_streaming(self, request: CommonRequest) -> AsyncIterable[CommonResponse]: ...
    async def run_bidi_streaming(self, request_stream: AsyncIterable[CommonRequest]) -> AsyncIterable[CommonResponse]: ...
    async def run_get_service_info(self) -> ServiceInfo: ...

    # class 內部定義
    @unary_handler
    async def my_unary_func(self, request)...
    @input_streaming_handler
    async def my_input_streaming_func(self, request)...
    @output_streaming_handler
    async def my_output_streaming_func(self, request)...
    @bidi_streaming_handler
    async def my_bidi_streaming_func(self, request)...
    @get_service_info_handler
    async def my_get_service_info_func(self, request)...

# 物件直接替換
common_brick = CommonBrick()
@common_brick.unary()
async def my_unary_func(self, request)...
@common_brick.input_streaming()
async def my_input_streaming_func(self, request)...
@common_brick.output_streaming()
async def my_output_streaming_func(self, request)...
@common_brick.bidi_streaming()
async def my_bidi_streaming_func(self, request)...
@common_brick.get_service_info()
async def my_get_service_info_func(self, request)...
```

### 🔄 分散式架構支援
- 內建 gRPC 服務轉換
  - 任何 Brick 都可一鍵轉換為 gRPC 服務
  - 支援跨網路、跨語言的服務調用
  - 適合分散式系統架構
- 多種協議整合
  - SSE（Server-Sent Events）適合串流應用
  - gRPC 支援高效能分散式部署
  - WebSocket/WebRTC 規劃中

```python
# 本地 Brick 轉換為 gRPC 服務 pseudocode
from llmbrick.servers.grpc import GrpcServer
from your_customer_brick import HelloBrick

# 建立並啟動 gRPC 服務
brick = HelloBrick()
server = GrpcServer(port=50051)
server.register_service(brick)
await server.start()

# 客戶端調用
client_brick = HelloBrick.toGrpcClient("localhost:50051")
response = await client_brick.run_unary(request)
```

### 🔧 易於擴展
- 插件系統
- 自定義組件
- 彈性客製化
- 支援橫向擴展部署

```python
# 自定義 Brick 範例 pseudocode
from llmbrick.bricks.common.common import CommonBrick

class CustomBrick(CommonBrick):
    @unary_handler
    async def process(self, request: CommonRequest) -> CommonResponse:
        # 自定義處理邏輯
        return CommonResponse(...)
```

## 快速導覽

根據您的需求，我們建議按以下路徑探索文件：

### 新手入門
1. [快速入門範例](./quickstart)：15 分鐘內完成第一個應用
2. [常見範例](./quickstart/local_brick_define)：參考實用範例

### 進階開發
1. [API 參考](./documents/api)：完整 API 文件
2. [最佳實踐](./documents/best-practices)：開發建議與規範

## 下一步

- 🚀 [立即開始](./quickstart)：快速建立您的第一個 LLMBrick 應用
- 📖 [詳細文件](./documents)：深入了解框架細節
- 💡 [查看範例](https://github.com/JiHungLin/llmbrick/tree/main/examples)：參考實際應用範例
