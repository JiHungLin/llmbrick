# OpenAI LLM Brick

本指南詳細說明 [`llmbrick/bricks/llm/openai_llm.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L1) 中的 OpenAIGPTBrick 實作，這是 LLMBrick 框架中專為 OpenAI GPT API 串接設計的 LLM Brick。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

OpenAIGPTBrick 旨在讓開發者能夠：

- **快速整合 OpenAI GPT-3.5/4/4o**：以統一介面串接 OpenAI 官方 API，支援同步與串流回應。
- **標準化 LLM 請求/回應流程**：與 LLMBrick 其他 Brick 完全相容，便於組合與擴展。
- **自動錯誤處理與日誌**：內建錯誤回報、日誌與服務資訊查詢。
- **支援多種模型與參數**：可彈性切換 OpenAI 支援的多種模型。

---

## 專案結構圖與模組詳解

### 架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── bricks/
│   │   └── llm/
│   │       ├── base_llm.py                # LLMBrick 抽象基底
│   │       └── openai_llm.py              # OpenAIGPTBrick 主體實作
│   ├── core/
│   │   ├── brick.py                       # Brick 裝飾器與執行邏輯
│   │   └── error_codes.py                 # 統一錯誤碼
│   └── protocols/
│       └── models/
│           └── bricks/
│               ├── llm_types.py           # LLMRequest/LLMResponse 資料模型
│               └── common_types.py        # ErrorDetail/ServiceInfoResponse
```

### 核心模組說明

- [`openai_llm.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L1)：OpenAIGPTBrick 主體，負責與 OpenAI API 溝通。
- [`base_llm.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L1)：LLMBrick 抽象基底，定義標準介面。
- [`llm_types.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L1)：LLMRequest/LLMResponse 資料結構。
- [`common_types.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/common_types.py#L1)：錯誤與服務資訊資料結構。

---

## 安裝與環境設定指南

### 必要套件

- `llmbrick`：主框架
- `openai`：官方 OpenAI Python SDK

### 安裝步驟

1. **安裝套件**

   ```bash
   pip install llmbrick openai
   ```

2. **設定 OpenAI API 金鑰**

   - 建議以環境變數方式設定：
     ```bash
     export OPENAI_API_KEY=sk-xxxxxxx
     ```
   - 或於程式中傳入 `api_key` 參數。

3. **驗證安裝**

   ```python
   from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
   print("✅ OpenAIGPTBrick 安裝成功！")
   ```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 OpenAIGPTBrick 使用

```python
import asyncio
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest

async def basic_example():
    # 建立 OpenAIGPTBrick 實例（API 金鑰自動從環境變數讀取）
    brick = OpenAIGPTBrick(model_id="gpt-3.5-turbo")
    
    # 建立請求
    request = LLMRequest(prompt="你好，請用一句話介紹 LLMBrick。")
    
    # 執行單次請求
    response = await brick.run_unary(request)
    print("回應：", response.text)

asyncio.run(basic_example())
```

### 2. 串流回應（Streaming）

```python
import asyncio
from llmbrick.bricks.llm.openai_llm import OpenAIGPTBrick
from llmbrick.protocols.models.bricks.llm_types import LLMRequest

async def streaming_example():
    brick = OpenAIGPTBrick(model_id="gpt-4o")
    request = LLMRequest(prompt="請用繁體中文分段說明 LLMBrick 的優勢。")
    
    print("串流回應：")
    async for chunk in brick.run_output_streaming(request):
        print(chunk.text, end="", flush=True)
    print("\n--- 完成 ---")

asyncio.run(streaming_example())
```

### 3. 進階：自訂 prompt、模型與 API 金鑰

```python
brick = OpenAIGPTBrick(
    default_prompt="請用一句話總結輸入內容。",
    model_id="gpt-4",
    api_key="sk-xxxxxxx"  # 可選，預設讀取環境變數
)
```

### 4. 查詢服務資訊

```python
info = await brick.run_get_service_info()
print(f"服務名稱: {info.service_name}, 支援模型: {info.models}")
```

---

## 核心 API / 類別 / 函式深度解析

### [`OpenAIGPTBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L17) 類別

#### 類別簽名與繼承關係

```python
class OpenAIGPTBrick(LLMBrick):
    """OpenAI GPT implementation of LLMBrick.
    
    Attributes:
        default_prompt (str): Default prompt to use if none provided.
        model_id (str): OpenAI model ID to use (e.g. "gpt-3.5-turbo", "gpt-4", "gpt-4o").
        client (AsyncOpenAI): Async OpenAI client instance.
        supported_models (List[str]): List of supported OpenAI model IDs.
    """
```

- **繼承自** [`LLMBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L1)
- 支援所有 LLM 標準通訊模式

#### 核心屬性詳解

- [`model_id`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L42)：預設使用的 OpenAI 模型 ID
- [`supported_models`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L43)：支援的模型清單 `["gpt-3.5-turbo", "gpt-4", "gpt-4o"]`
- [`client`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L56)：AsyncOpenAI 客戶端實例

### 重要方法詳細解析

#### [`__init__`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L27) - 初始化方法

```python
def __init__(self, 
             default_prompt: str = "",
             model_id: str = "gpt-3.5-turbo",
             api_key: Optional[str] = None,
             **kwargs):
```

**功能**：初始化 OpenAIGPTBrick 實例，設定模型參數並建立 OpenAI 客戶端

**參數詳解**：
- `default_prompt: str = ""`：預設提示詞，當請求未提供 prompt 時使用
- `model_id: str = "gpt-3.5-turbo"`：預設 OpenAI 模型 ID
- `api_key: Optional[str] = None`：OpenAI API 金鑰，若未提供則從環境變數 `OPENAI_API_KEY` 讀取

**內部實作邏輯**：

1. **呼叫父類別初始化** ([L40](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L40))：
   ```python
   super().__init__(default_prompt=default_prompt, **kwargs)
   ```

2. **設定模型參數** ([L42-43](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L42)):
   ```python
   self.model_id = model_id
   self.supported_models = ["gpt-3.5-turbo", "gpt-4", "gpt-4o"]
   ```

3. **API 金鑰處理** ([L47-53](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L47))：
   ```python
   api_key = api_key or os.getenv("OPENAI_API_KEY")
   if not api_key:
       logger.error("OpenAI API key not found in environment or constructor")
       raise ValueError(
           "OpenAI API key must be provided either through constructor "
           "or OPENAI_API_KEY environment variable"
       )
   ```

4. **建立 OpenAI 客戶端** ([L56-57](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L56))：
   ```python
   self.client = AsyncOpenAI(api_key=api_key)
   logger.info(f"OpenAIGPTBrick initialized with model {model_id}")
   ```

#### [`_create_chat_completion`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L60) - 核心 API 呼叫方法

```python
@log_function(service_name="OpenAIGPTBrick", level="debug")
async def _create_chat_completion(
    self,
    request: LLMRequest,
    stream: bool = False
) -> Union[ChatCompletion, AsyncGenerator[ChatCompletionChunk, None]]:
```

**功能**：統一的 OpenAI API 呼叫介面，支援同步與串流模式

**參數詳解**：
- `request: LLMRequest`：LLM 請求物件，包含 prompt、context、參數等
- `stream: bool = False`：是否使用串流模式

**回傳值**：
- 非串流：`ChatCompletion` 完整回應物件
- 串流：`AsyncGenerator[ChatCompletionChunk, None]` 串流回應生成器

**內部實作邏輯**：

1. **Context 轉換為 OpenAI Messages 格式** ([L75-81](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L75))：
   ```python
   messages = []
   for ctx in request.context:
       messages.append({
           "role": ctx.role or "user",
           "content": ctx.content
       })
   ```

2. **添加主要 Prompt** ([L83-87](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L83))：
   ```python
   messages.append({
       "role": "user",
       "content": request.prompt or self.default_prompt
   })
   ```

3. **呼叫 OpenAI API** ([L90-96](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L90))：
   ```python
   return await self.client.chat.completions.create(
       model=request.model_id or self.model_id,
       messages=messages,
       temperature=request.temperature,
       max_tokens=request.max_tokens if request.max_tokens > 0 else None,
       stream=stream
   )
   ```

#### [`unary_method`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L100) - 單次請求處理

```python
@unary_handler
@log_function(service_name="OpenAIGPTBrick", level="info")
async def unary_method(self, request: LLMRequest) -> LLMResponse:
```

**功能**：處理單次請求/回應互動，使用 `@unary_handler` 裝飾器註冊

**內部實作邏輯**：

1. **呼叫 API 並處理成功回應** ([L109-116](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L109))：
   ```python
   try:
       completion = await self._create_chat_completion(request, stream=False)
       return LLMResponse(
           text=completion.choices[0].message.content,
           tokens=[],  # OpenAI doesn't provide token-by-token breakdown
           is_final=True,
           error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
       )
   ```

2. **異常處理** ([L117-123](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L117))：
   ```python
   except Exception as e:
       return LLMResponse(
           text="",
           tokens=[],
           is_final=True,
           error=ErrorDetail(code=1, message=str(e))
       )
   ```

#### [`output_streaming_method`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L127) - 串流回應處理

```python
@output_streaming_handler
@log_function(service_name="OpenAIGPTBrick", level="info")
async def output_streaming_method(self, request: LLMRequest) -> AsyncGenerator[LLMResponse, None]:
```

**功能**：處理串流回應互動，使用 `@output_streaming_handler` 裝飾器註冊

**內部實作邏輯**：

1. **串流處理主循環** ([L136-146](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L136))：
   ```python
   try:
       async for chunk in await self._create_chat_completion(request, stream=True):
           if not chunk.choices[0].delta.content:
               continue
               
           yield LLMResponse(
               text=chunk.choices[0].delta.content,
               tokens=[],  # OpenAI doesn't provide token-by-token breakdown
               is_final=False,
               error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
           )
   ```

2. **發送最終結束標記** ([L148-154](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L148))：
   ```python
   # Send final chunk
   yield LLMResponse(
       text="",
       tokens=[],
       is_final=True,
       error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
   )
   ```

3. **異常處理** ([L156-162](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L156))：
   ```python
   except Exception as e:
       yield LLMResponse(
           text="",
           tokens=[],
           is_final=True,
           error=ErrorDetail(code=1, message=str(e))
       )
   ```

#### [`get_service_info_method`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L166) - 服務資訊查詢

```python
@get_service_info_handler
@log_function(service_name="OpenAIGPTBrick", level="info")
async def get_service_info_method(self) -> ServiceInfoResponse:
```

**功能**：提供服務基本資訊，使用 `@get_service_info_handler` 裝飾器註冊

**回傳內容** ([L172-177](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L172))：
```python
return ServiceInfoResponse(
    service_name="OpenAI GPT Brick",
    version="1.0.0",
    models=self.supported_models,
    error=ErrorDetail(code=ErrorCodes.SUCCESS, message="Success")
)
```

### 關鍵設計特色

#### 1. 日誌記錄系統

所有方法都使用 [`@log_function`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L59) 裝飾器：
- 自動記錄方法呼叫
- 不同層級的日誌（debug、info）
- 統一的服務名稱標識

#### 2. 錯誤處理機制

- **初始化階段**：檢查 API 金鑰有效性
- **API 呼叫階段**：捕獲所有異常並轉換為 LLMResponse
- **統一錯誤格式**：使用 ErrorDetail 標準化錯誤資訊

#### 3. 資料轉換邏輯

- **LLMRequest → OpenAI Messages**：自動轉換 context 和 prompt
- **OpenAI Response → LLMResponse**：統一回應格式
- **參數映射**：temperature、max_tokens 等參數直接傳遞

#### 4. 串流處理優化

- **空內容過濾**：跳過空的 delta.content
- **結束標記**：明確的 is_final=True 標記
- **異常恢復**：串流中斷時提供錯誤回應

### 資料模型詳解

#### LLMRequest 主要欄位
- `prompt: str`：主要提示詞
- `context: List[Context]`：對話上下文
- `model_id: Optional[str]`：指定模型（覆蓋預設）
- `temperature: float`：生成溫度參數
- `max_tokens: int`：最大 token 數量

#### LLMResponse 主要欄位
- `text: str`：生成的文本內容
- `tokens: List[str]`：token 分解（OpenAI 不提供，固定為空）
- `is_final: bool`：是否為最終回應
- `error: ErrorDetail`：錯誤資訊

---

## 常見錯誤與排除指引

### 初始化階段錯誤

- **未設定 API 金鑰**  
  - 錯誤訊息：`OpenAI API key not found in environment or constructor`
  - 發生位置：[`__init__` 方法 L49](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L49)
  - 解法：設定 `OPENAI_API_KEY` 環境變數或傳入 `api_key` 參數

### API 呼叫階段錯誤

- **模型名稱錯誤**  
  - 錯誤訊息：OpenAI API 回傳 "model not found"
  - 發生位置：[`_create_chat_completion` 方法 L91](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L91)
  - 解法：確認 `model_id` 為支援的模型（"gpt-3.5-turbo", "gpt-4", "gpt-4o"）

- **API 請求失敗**  
  - 可能原因：金鑰無效、流量超過、網路問題
  - 處理位置：[異常處理區塊 L117](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L117)
  - 解法：檢查金鑰、API 狀態與網路連線

### 串流處理錯誤

- **串流回應未出現內容**  
  - 可能原因：prompt 為空、OpenAI API 回傳空內容
  - 處理位置：[內容過濾 L138](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L138)
  - 解法：確認 prompt 有內容，檢查 OpenAI API 狀態

---

## 效能優化與最佳實踐

### 安全性最佳實踐

- **API 金鑰管理**：使用環境變數，避免硬編碼於程式中
- **錯誤資訊**：避免在日誌中洩露敏感資訊
- **參數驗證**：在 API 呼叫前驗證參數有效性

### 效能優化建議

- **串流模式**：長文本生成建議使用串流模式，提升使用者體驗
- **模型選擇**：根據需求選擇適當模型（gpt-3.5-turbo 速度快、gpt-4o 效果佳）
- **參數調整**：適當調整 temperature、max_tokens 控制生成品質與速度

### 日誌與監控

- **日誌層級**：生產環境建議設定為 INFO 以上
- **效能監控**：監控 API 回應時間和錯誤率
- **使用量追蹤**：記錄 token 使用量以控制成本

---

## FAQ / 進階問答

### Q1: 如何切換不同 OpenAI 模型？

**A**：於建構 OpenAIGPTBrick 時指定 `model_id`，如：
```python
brick = OpenAIGPTBrick(model_id="gpt-4o")
```
或在請求中動態指定：
```python
request = LLMRequest(prompt="...", model_id="gpt-4")
```

### Q2: 可以同時支援多個 API 金鑰嗎？

**A**：目前一個 Brick 實例僅支援一組金鑰。可建立多個 Brick 實例分別指定不同金鑰：
```python
brick1 = OpenAIGPTBrick(api_key="sk-key1...")
brick2 = OpenAIGPTBrick(api_key="sk-key2...")
```

### Q3: 如何處理 OpenAI API 限流？

**A**：OpenAI SDK 內建重試機制，但建議在應用層實作：
- 監控 API 回應狀態
- 實作指數退避重試
- 使用多個 API 金鑰輪替

### Q4: 串流模式下如何處理中斷？

**A**：串流處理已內建異常處理 ([L156](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L156))，會自動發送錯誤回應。應用端可檢查 `response.error.code` 判斷是否成功。

### Q5: 如何取得 token 使用量資訊？

**A**：OpenAI API 回應包含 usage 資訊，但目前 LLMResponse 未包含此欄位。可考慮：
- 擴展 LLMResponse 資料結構
- 在日誌中記錄 usage 資訊
- 使用 OpenAI 官方儀表板監控

---

## 參考資源與延伸閱讀

### 原始碼參考
- [OpenAIGPTBrick 完整實作](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/openai_llm.py#L1)
- [LLMRequest/LLMResponse 資料結構](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/llm_types.py#L1)
- [LLMBrick 基礎類別](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/llm/base_llm.py#L1)

### 官方文件
- [LLMBrick 基礎說明](../llm_brick_guide.md)
- [OpenAI 官方文件](https://platform.openai.com/docs/)
- [OpenAI Python SDK](https://github.com/openai/openai-python)

### 社群資源
- [LLMBrick 問題回報](https://github.com/JiHungLin/llmbrick/issues)
- [範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples)

---

OpenAIGPTBrick 提供了完整的 OpenAI GPT 整合方案，從基礎的 API 呼叫到進階的串流處理，都有完善的錯誤處理和日誌記錄。透過標準化的 LLMBrick 介面，可以輕鬆與其他 Brick 組合，打造強大的 AI 應用生態系統。

*本指南持續更新中，如有問題或建議，歡迎參與社群討論！*
