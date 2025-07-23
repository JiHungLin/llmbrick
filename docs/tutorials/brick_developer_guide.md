# Brick 開發者指引：自訂複雜 Brick class

## 設計原則

- **彈性**：允許開發者在 `__init__` 注入自訂參數、物件，並自由擴展屬性與方法。
- **直覺**：用 decorator 註冊 handler，明確對應 gRPC call type（unary、streaming）。
- **可讀性**：建議每個 handler 都加上型別註解與 docstring。
- **開發體驗**：提供明確範例與步驟，降低新手學習曲線。

---

## 最佳實踐範例（新版強型別 decorator）

```python
from llmbrick.core.brick import BaseBrick, unary_handler

class MyCustomBrick(BaseBrick[str, str]):
    """
    範例：自訂建構子與 handler
    """
    def __init__(self, prefix: str, **kwargs):
        super().__init__(**kwargs)
        self.prefix = prefix  # 你可以自訂任何屬性

    @unary_handler
    async def process(self, input_data: str) -> str:
        """
        處理輸入資料並回傳字串
        """
        return f"{self.prefix}: {input_data}"
```

---

## 開發步驟指引

1. **繼承 BaseBrick**  
   指定 input/output 型別（如 `BaseBrick[str, str]`）。

2. **自訂 `__init__`**  
   可以加入你需要的參數與物件，記得呼叫 `super().__init__(**kwargs)`。

3. **註冊 handler**  
   直接在 class method 上用 `@unary_handler`、`@output_streaming_handler` 等 decorator 標記。

4. **執行 handler**  
   用 `run_unary`、`run_output_streaming` 等方法呼叫。

---

## 常見錯誤與解法

- **沒有註冊 handler**：執行時會報 `NotImplementedError`，請確認有用 decorator 標記。
- **handler 型別不符**：請確認 async function 的 input/output 型別正確。
- **IDE 沒有提示**：請參考本指引範例，或查閱 `llmbrick.core.brick` 的 docstring。

---

## 進階建議

- 可在 class docstring 裡說明本 brick 的用途與 handler。
- 若有多個 handler，可分別用不同 decorator 標記。
- 建議每個 handler 都加上型別註解與 docstring，提升可讀性與 IDE 支援。

---

## Mermaid 結構圖（開發者視角）

```mermaid
classDiagram
    class BaseBrick
    class MyCustomBrick
    BaseBrick <|-- MyCustomBrick
    MyCustomBrick : +prefix: str
    MyCustomBrick : +process(input_data: str) str
```

---

## Brick-to-gRPC 分層包裝開發指引（推薦架構）

### 步驟 1：實作 Brick 子類

```python
from llmbrick.core.brick import BaseBrick

class LLMBrick(BaseBrick):
    def __init__(self, default_prompt: str, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.default_prompt = default_prompt

    def run_generateresponse(self, request, context):
        # 實作 gRPC handler 對應邏輯
        pass

    def run_generateresponsestream(self, request, context):
        # 實作 gRPC stream handler
        yield
```

### 步驟 2：使用 MainGrpcServer 註冊服務

```python
from llmbrick.servers.grpc.server import MainGrpcServer

brick = LLMBrick(default_prompt="hi")
server = GrpcServer(port=50051)
server.register_service(brick)
server.start()
```

- 每個分類有專屬 xxxGrpcWrapper，明確 mapping proto rpc function
- 通用型 Brick 可用 CommonGrpcWrapper 註冊
- 擴展新 Service 只需新增對應 wrapper 並在主 server 註冊