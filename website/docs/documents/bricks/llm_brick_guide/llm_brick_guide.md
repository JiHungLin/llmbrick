# LLMBrick 完整使用指南

本指南詳細說明 [`llmbrick/bricks/llm/base_llm.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L14) 中的 LLMBrick 實作，這是 LLMBrick 框架中專為大型語言模型（LLM）應用設計的核心組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

LLMBrick 旨在解決以下 LLM 應用開發的痛點：

- **標準化 LLM 請求/回應流程**：統一 prompt、context、流式回應等常見 LLM 互動模式
- **gRPC 服務化**：內建 gRPC 協定，支援單次與流式回應
- **易於擴展與客製化**：可自訂 prompt 處理、模型選擇、回應格式
- **與 CommonBrick 完全相容**：繼承所有通用錯誤處理、服務資訊查詢等能力

---

## 專案結構圖與模組詳解

### 架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── llm/
│   │       ├── __init__.py
│   │       └── base_llm.py         # LLMBrick 主體實作
│   ├── protocols/
│   │   ├── grpc/
│   │   │   └── llm/
│   │   │       ├── llm.proto       # Protocol Buffer 定義
│   │   │       ├── llm_pb2.py      # 自動生成的訊息類別
│   │   │       └── llm_pb2_grpc.py # gRPC 服務存根
│   │   └── models/
│   │       └── bricks/
│   │           └── llm_types.py    # LLMRequest/LLMResponse 資料模型
│   └── core/
│       └── brick.py                # BaseBrick 抽象基礎類別
```

### 核心模組說明

#### 1. [`LLMBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L14) - LLM 專用 Brick

- **職責**：專為 LLM 應用設計，標準化 prompt、context、流式回應等互動模式
- **繼承自**：[`BaseBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py)
- **gRPC 服務類型**：`llm`
- **僅允許三種 handler**：unary、output_streaming、get_service_info

#### 2. gRPC 協定層

- **[llm.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/llm/llm.proto#L33)** 定義
    ```protobuf
    service LLMService {
      rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
      rpc Unary(LLMRequest) returns (LLMResponse);
      rpc OutputStreaming(LLMRequest) returns (stream LLMResponse);
    }
    ```
- **訊息結構**：
    - `LLMRequest`：model_id, prompt, context, client_id, session_id, request_id, source_language, temperature, max_tokens
    - `LLMResponse`：text, tokens, is_final, error

#### 3. 資料模型

- **[`LLMRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L24)**：封裝 LLM 請求參數
- **[`LLMResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L72)**：封裝 LLM 回應內容
- **[`Context`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L11)**：對話上下文

---

## 安裝與環境設定指南

### 依賴需求

LLMBrick 需要以下核心依賴：

```bash
pip install llmbrick
# 會自動安裝 grpcio、protobuf 等必要套件
```

### 自動化安裝步驟

1. **安裝 LLMBrick 套件**
    ```bash
    pip install llmbrick
    ```
2. **驗證安裝**
    ```python
    from llmbrick.bricks.llm.base_llm import LLMBrick
    print("✅ LLMBrick 安裝成功！")
    ```
3. **開發環境建議**
    ```bash
    pip install -r requirements-dev.txt
    export LLMBRICK_LOG_LEVEL=INFO
    export LLMBRICK_GRPC_PORT=50051
    ```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 LLMBrick 使用

```python
import asyncio
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.core.brick import unary_handler, get_service_info_handler
from llmbrick.protocols.models.bricks.llm_types import LLMRequest, LLMResponse, Context
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, ServiceInfoResponse

class SimpleLLMBrick(LLMBrick):
    def __init__(self, default_prompt="Say hi", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @unary_handler
    async def echo(self, request: LLMRequest) -> LLMResponse:
        return LLMResponse(
            text=f"Echo: {request.prompt or self.default_prompt}",
            tokens=["echo"],
            is_final=True,
            error=ErrorDetail(code=200, message="Success"),
        )

    @get_service_info_handler
    async def info(self) -> ServiceInfoResponse:
        return ServiceInfoResponse(
            service_name="SimpleLLMBrick",
            version="1.0.0",
            models=[],
            error=ErrorDetail(code=200, message="Success"),
        )

async def main():
    brick = SimpleLLMBrick(default_prompt="Hello")
    req = LLMRequest(prompt="Test prompt", context=[])
    resp = await brick.run_unary(req)
    print(resp.text)

asyncio.run(main())
```

### 2. 流式回應與服務資訊

```python
from llmbrick.core.brick import output_streaming_handler

class StreamLLMBrick(LLMBrick):
    def __init__(self, default_prompt="Stream!", **kwargs):
        super().__init__(default_prompt=default_prompt, **kwargs)

    @output_streaming_handler
    async def stream(self, request: LLMRequest):
        for i, word in enumerate((request.prompt or self.default_prompt).split()):
            yield LLMResponse(
                text=word,
                tokens=[word],
                is_final=(i == len((request.prompt or self.default_prompt).split()) - 1),
                error=None,
            )
```

### 3. gRPC 客戶端連接與使用

```python
import asyncio
from llmbrick.bricks.llm.base_llm import LLMBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest

async def grpc_client_example():
    client = LLMBrick.toGrpcClient("localhost:50051", default_prompt="Hi!")
    req = LLMRequest(prompt="gRPC test", context=[])
    resp = await client.run_unary(req)
    print(resp.text)

asyncio.run(grpc_client_example())
```

更多範例請參考 [examples/llm_brick_define](https://github.com/JiHungLin/llmbrick/tree/main/examples/llm_brick_define)。

---

## 核心 API / 類別 / 函式深度解析

### [`LLMBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L14) 類別

#### 類別簽名與繼承關係

```python
class LLMBrick(BaseBrick[LLMRequest, LLMResponse]):
    brick_type = BrickType.LLM
    allowed_handler_types = {"unary", "output_streaming", "get_service_info"}
```

#### 重要屬性

- `default_prompt: str` - 預設提示詞
- `brick_type` - 標識為 LLM 類型
- `allowed_handler_types` - 僅允許三種 handler

#### 主要方法

##### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L61)

- **功能**：將 LLMBrick 轉換為異步 gRPC 客戶端
- **參數**：
    - `remote_address: str` - gRPC 伺服器位址
    - `default_prompt: str` - 預設提示詞
    - `**kwargs` - 額外初始化參數
- **回傳**：配置為 gRPC 客戶端的 LLMBrick 實例
- **範例**：
    ```python
    client = LLMBrick.toGrpcClient("localhost:50051", default_prompt="Hi!")
    ```

##### [`run_unary()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L233)

- **功能**：執行單次 LLM 請求
- **參數**：`input_data: LLMRequest`
- **回傳**：`LLMResponse`
- **範例**：
    ```python
    req = LLMRequest(prompt="Hello", context=[])
    resp = await brick.run_unary(req)
    ```

##### [`run_output_streaming()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L258)

- **功能**：執行流式 LLM 輸出
- **參數**：`input_data: LLMRequest`
- **回傳**：`AsyncIterator[LLMResponse]`
- **範例**：
    ```python
    async for resp in brick.run_output_streaming(req):
        print(resp.text)
    ```

##### [`run_get_service_info()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L245)

- **功能**：查詢服務資訊
- **回傳**：`ServiceInfoResponse`

#### 不支援的 handler

- LLMBrick **不支援** input_streaming 與 bidi_streaming，調用會拋出 NotImplementedError
    - [`bidi_streaming`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L39)
    - [`input_streaming`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L51)

---

## 資料模型說明

### [`LLMRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L24)

- `model_id: str` - 指定模型
- `prompt: str` - 輸入提示詞
- `context: List[Context]` - 對話上下文
- `client_id/session_id/request_id/source_language/temperature/max_tokens` - 進階參數

### [`LLMResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L72)

- `text: str` - 回應文字
- `tokens: List[str]` - 分詞結果（流式時可用）
- `is_final: bool` - 是否為最後一筆
- `error: Optional[ErrorDetail]` - 錯誤資訊

### [`Context`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L11)

- `role: str` - 角色（如 user/assistant）
- `content: str` - 內容

---

## 常見錯誤與排除

- **TypeError: context 必須為 List[Context]**
    - 請確保 LLMRequest 的 context 欄位為 Context 物件列表
- **NotImplementedError: LLMBrick does not support input_streaming/bidi_streaming handler**
    - LLMBrick 僅支援 unary、output_streaming、get_service_info
- **gRPC 連線失敗**
    - 檢查伺服器位址與防火牆設定
- **tokens 欄位型別錯誤**
    - tokens 必須為 List[str]

---

## 效能優化與最佳實踐

- **僅註冊允許的 handler**：LLMBrick 只允許 unary、output_streaming、get_service_info
- **善用流式回應**：長文本建議用 output_streaming 提升用戶體驗
- **服務資訊自動化**：建議實作 get_service_info_handler，方便前端自動發現模型能力
- **型別安全**：所有資料結構請用 LLMRequest/LLMResponse/Context

---

## FAQ / 進階問答

### Q1: LLMBrick 與 CommonBrick 差異？

**A**：LLMBrick 專為 LLM 應用設計，僅允許 prompt/context 相關的三種 handler，且資料模型更嚴謹。CommonBrick 則為通用型，允許所有通訊模式。

### Q2: 如何串接外部 LLM（如 OpenAI）？

**A**：可繼承 LLMBrick，於 unary/output_streaming handler 內呼叫外部 API，並將回應包裝為 LLMResponse。

### Q3: 可以自訂 context 處理嗎？

**A**：可以，context 欄位為 List[Context]，可依需求自訂對話歷史格式與處理邏輯。

---

## 參考資源與延伸閱讀

- [LLMBrick GitHub 原始碼](https://github.com/JiHungLin/llmbrick)
- [llmbrick/bricks/llm/base_llm.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py)
- [llmbrick/protocols/grpc/llm/llm.proto](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/llm/llm.proto)
- [llmbrick/protocols/models/bricks/llm_types.py](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py)
- [官方範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/llm_brick_define)
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/)
- [Protocol Buffer 官方文件](https://developers.google.com/protocol-buffers)

---

LLMBrick 是構建現代 LLM 應用的最佳起點，掌握其用法能大幅提升開發效率與維護性。如有問題，歡迎參與社群討論或回報 issue！
