# CommonBrick

本指南詳細說明 [`llmbrick/bricks/common/common.py`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/common/common.py) 中的 CommonBrick 實作，這是 LLMBrick 框架中最基礎且重要的組件。

---

## 專案概述與目標

### 🎯 設計目標與解決問題

CommonBrick 是 LLMBrick 框架的核心基礎組件，設計用來解決以下關鍵問題：

- **統一介面協定**：為所有 Brick 類型提供標準化的請求/回應處理機制
- **多協定支援**：內建完整的 gRPC 服務支援，支援四種通訊模式
- **擴展基礎**：作為其他專用 Brick（LLMBrick、GuardBrick 等）的繼承基礎
- **服務化能力**：可輕鬆轉換為獨立的微服務或客戶端
- **錯誤處理標準化**：提供統一的錯誤處理和狀態管理機制

### 🔧 核心功能特色

- **四種通訊模式**：Unary（單次）、Input Streaming（輸入串流）、Output Streaming（輸出串流）、Bidirectional Streaming（雙向串流）
- **裝飾器模式**：支援動態註冊處理器，靈活組合業務邏輯
- **類別繼承模式**：支援傳統的類別繼承方式定義處理器
- **自動 gRPC 轉換**：一鍵轉換為 gRPC 客戶端或服務端
- **完整錯誤處理**：內建豐富的錯誤碼和錯誤處理機制

---

## 專案結構圖與模組詳解

### 整體架構圖

```plaintext
LLMBrick Framework
├── llmbrick/
│   ├── core/                           # 核心基礎模組
│   │   ├── brick.py                    # BaseBrick 基礎類別與裝飾器
│   │   ├── error_codes.py              # 統一錯誤碼定義
│   │   └── exceptions.py               # 自訂例外類別
│   │
│   ├── bricks/                         # Brick 實作模組
│   │   └── common/
│   │       ├── __init__.py
│   │       └── common.py               # CommonBrick 主體實作
│   │
│   ├── protocols/                      # 協定定義模組
│   │   ├── grpc/                       # gRPC 協定
│   │   │   └── common/
│   │   │       ├── common.proto        # Protocol Buffer 定義
│   │   │       ├── common_pb2.py       # 自動生成的訊息類別
│   │   │       └── common_pb2_grpc.py  # 自動生成的服務存根
│   │   └── models/                     # 資料模型
│   │       └── bricks/
│   │           └── common_types.py     # CommonBrick 資料類型
│   │
│   └── servers/                        # 服務器實作
│       └── grpc/
│           ├── server.py               # gRPC 服務器
│           └── wrappers/
│               └── common_grpc_wrapper.py  # CommonBrick gRPC 包裝器
```

### 核心模組詳細說明

#### 1. [`BaseBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L71) - 基礎抽象類別

**職責**：所有 Brick 的基礎類別，定義標準介面和行為

**核心特性**：
- **泛型支援**：`BaseBrick[InputT, OutputT]` 提供型別安全
- **處理器管理**：自動註冊和管理五種處理器類型
- **裝飾器支援**：提供 `@brick.unary()` 等裝飾器方法
- **執行入口**：提供 `run_*` 系列方法作為統一執行入口
- **錯誤處理**：內建異常捕獲和日誌記錄

**關鍵屬性**：
```python
class BaseBrick(Generic[InputT, OutputT]):
    brick_type: Optional[BrickType] = None              # Brick 類型標識
    allowed_handler_types: Optional[set] = None         # 允許的處理器類型限制
    _unary_handler: Optional[UnaryHandler] = None       # 單次請求處理器
    _output_streaming_handler: Optional[...] = None     # 輸出串流處理器
    _input_streaming_handler: Optional[...] = None      # 輸入串流處理器
    _bidi_streaming_handler: Optional[...] = None       # 雙向串流處理器
    _get_service_info_handler: Optional[...] = None     # 服務資訊處理器
```

#### 2. [`CommonBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/common/common.py#L15) - 通用 Brick 實作

**職責**：提供通用的請求/回應處理能力，支援所有通訊模式

**核心特性**：
- **繼承 BaseBrick**：獲得完整的基礎功能
- **gRPC 整合**：內建 `toGrpcClient()` 方法
- **無限制處理器**：支援所有五種處理器類型
- **標準資料模型**：使用 `CommonRequest/CommonResponse`

#### 3. [`ErrorCodes`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/error_codes.py#L12) - 錯誤碼管理

**職責**：統一的錯誤碼定義和 ErrorDetail 創建工廠

**錯誤碼分類**：
- **HTTP 標準碼**：200-599（成功、客戶端錯誤、服務器錯誤）
- **框架業務碼**：1000-9999（通用、驗證、認證、模型、外部服務、資源、網路、存儲、業務錯誤）

**工廠方法範例**：
```python
# 快速創建常用錯誤
ErrorCodes.success()                    # 成功狀態
ErrorCodes.parameter_invalid("name")    # 參數無效
ErrorCodes.model_not_found("gpt-4")     # 模型未找到
ErrorCodes.internal_error("詳細錯誤")    # 內部錯誤
```

#### 4. 資料模型系統

**[`CommonRequest`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/common_types.py#L58)**：
```python
@dataclass
class CommonRequest:
    data: Dict[str, Any] = field(default_factory=dict)  # 靈活的資料載體
```

**[`CommonResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/common_types.py#L71)**：
```python
@dataclass
class CommonResponse:
    data: Dict[str, Any] = field(default_factory=dict)  # 回應資料
    error: Optional[ErrorDetail] = None                  # 錯誤詳情
```

**[`ServiceInfoResponse`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/models/bricks/common_types.py#L106)**：
```python
@dataclass
class ServiceInfoResponse:
    service_name: str = ""                               # 服務名稱
    version: str = ""                                    # 版本資訊
    models: List[ModelInfo] = field(default_factory=list)  # 支援的模型
    error: Optional[ErrorDetail] = None                  # 錯誤狀態
```

#### 5. gRPC 協定層

**[Protocol Buffer 定義](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/protocols/grpc/common/common.proto)**：
```protobuf
service CommonService {
  rpc GetServiceInfo(ServiceInfoRequest) returns (ServiceInfoResponse);
  rpc Unary (CommonRequest) returns (CommonResponse);
  rpc OutputStreaming (CommonRequest) returns (stream CommonResponse);
  rpc InputStreaming (stream CommonRequest) returns (CommonResponse);
  rpc BidiStreaming (stream CommonRequest) returns (stream CommonResponse);
}
```

**[gRPC 包裝器](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/servers/grpc/wrappers/common_grpc_wrapper.py)**：
- 自動處理 Protocol Buffer 與 Python 物件轉換
- 統一的錯誤處理和狀態碼映射
- 異步串流處理支援

---

## 安裝與環境設定指南

### 依賴需求

CommonBrick 需要以下核心依賴：

```bash
# 核心依賴
grpcio>=1.50.0              # gRPC 核心庫
grpcio-tools>=1.50.0        # gRPC 工具（Protocol Buffer 編譯）
protobuf>=4.21.0            # Protocol Buffer 支援
google-protobuf>=4.21.0     # Google Protocol Buffer 擴展
```

### 自動化安裝步驟

#### 1. 安裝 LLMBrick 套件

```bash
# 從 PyPI 安裝（推薦）
pip install llmbrick

# 或從源碼安裝
git clone https://github.com/JiHungLin/llmbrick.git
cd llmbrick
pip install -e .
```

#### 2. 驗證安裝

```python
# 驗證安裝是否成功
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse

print("✅ CommonBrick 安裝成功！")
```

#### 3. 開發環境設定

```bash
# 安裝開發依賴
pip install -r requirements-dev.txt

# 設定環境變數（可選）
export LLMBRICK_LOG_LEVEL=INFO
export LLMBRICK_GRPC_PORT=50051
```

---

## 逐步範例：從基礎到進階

### 1. 最簡單的 CommonBrick 使用

```python
import asyncio
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse
from llmbrick.core.error_codes import ErrorCodes

async def basic_example():
    """最基本的 CommonBrick 使用範例"""
    
    # 建立 CommonBrick 實例
    brick = CommonBrick()
    
    # 使用裝飾器定義處理邏輯
    @brick.unary()
    async def echo_handler(request: CommonRequest) -> CommonResponse:
        """簡單的回音處理器"""
        message = request.data.get("message", "Hello, World!")
        return CommonResponse(
            data={"echo": f"收到訊息: {message}"},
            error=ErrorCodes.success()
        )
    
    # 執行請求
    request = CommonRequest(data={"message": "測試訊息"})
    response = await brick.run_unary(request)
    
    print(f"回應: {response.data}")
    print(f"狀態: {response.error.message}")

# 執行範例
asyncio.run(basic_example())
```

### 2. 類別繼承方式定義 CommonBrick

```python
from typing import AsyncIterator
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import (
    CommonRequest, CommonResponse, ErrorDetail, ServiceInfoResponse, ModelInfo
)
from llmbrick.core.error_codes import ErrorCodes
from llmbrick.core.brick import (
    unary_handler, input_streaming_handler, output_streaming_handler, 
    bidi_streaming_handler, get_service_info_handler
)

class TextProcessorBrick(CommonBrick):
    """文本處理 Brick 範例"""
    
    def __init__(self, processor_name: str = "TextProcessor", **kwargs):
        super().__init__(**kwargs)
        self.processor_name = processor_name
        self.processed_count = 0
    
    @unary_handler
    async def process_text(self, request: CommonRequest) -> CommonResponse:
        """單次文本處理"""
        try:
            text = request.data.get("text", "")
            if not text:
                return CommonResponse(
                    data={},
                    error=ErrorCodes.parameter_invalid("text", "文本內容不能為空")
                )
            
            # 模擬文本處理邏輯
            processed_text = text.upper().strip()
            self.processed_count += 1
            
            return CommonResponse(
                data={
                    "original": text,
                    "processed": processed_text,
                    "length": len(processed_text),
                    "processor": self.processor_name
                },
                error=ErrorCodes.success()
            )
            
        except Exception as e:
            return CommonResponse(
                data={},
                error=ErrorCodes.internal_error(f"處理失敗: {str(e)}")
            )
    
    @output_streaming_handler
    async def stream_process(self, request: CommonRequest) -> AsyncIterator[CommonResponse]:
        """串流文本處理 - 逐字輸出"""
        text = request.data.get("text", "")
        if not text:
            yield CommonResponse(
                data={},
                error=ErrorCodes.parameter_invalid("text")
            )
            return
        
        # 逐字處理並串流輸出
        for i, char in enumerate(text):
            await asyncio.sleep(0.1)  # 模擬處理延遲
            yield CommonResponse(
                data={
                    "position": i,
                    "character": char,
                    "is_alpha": char.isalpha(),
                    "progress": f"{i+1}/{len(text)}"
                },
                error=ErrorCodes.success()
            )
    
    @input_streaming_handler
    async def batch_process(self, request_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
        """批次處理輸入串流"""
        texts = []
        total_length = 0
        
        try:
            async for request in request_stream:
                text = request.data.get("text", "")
                if text:  # 忽略空文本
                    texts.append(text)
                    total_length += len(text)
            
            if not texts:
                return CommonResponse(
                    data={},
                    error=ErrorCodes.parameter_invalid("texts", "至少需要一個有效文本")
                )
            
            # 批次處理結果
            processed_texts = [text.upper().strip() for text in texts]
            
            return CommonResponse(
                data={
                    "batch_size": len(texts),
                    "total_length": total_length,
                    "processed_texts": processed_texts,
                    "average_length": total_length / len(texts)
                },
                error=ErrorCodes.success()
            )
            
        except Exception as e:
            return CommonResponse(
                data={},
                error=ErrorCodes.internal_error(f"批次處理失敗: {str(e)}")
            )
    
    @bidi_streaming_handler
    async def interactive_process(self, request_stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]:
        """雙向串流互動處理"""
        session_id = f"session_{asyncio.get_event_loop().time()}"
        message_count = 0
        
        try:
            async for request in request_stream:
                message_count += 1
                text = request.data.get("text", "")
                
                if not text:
                    yield CommonResponse(
                        data={"session_id": session_id, "message_count": message_count},
                        error=ErrorCodes.parameter_invalid("text", "文本不能為空")
                    )
                    continue
                
                # 互動式處理邏輯
                if text.lower() == "exit":
                    yield CommonResponse(
                        data={
                            "session_id": session_id,
                            "message": "會話結束",
                            "total_messages": message_count
                        },
                        error=ErrorCodes.success()
                    )
                    break
                
                # 處理並回應
                processed = text.upper()
                yield CommonResponse(
                    data={
                        "session_id": session_id,
                        "message_count": message_count,
                        "original": text,
                        "processed": processed,
                        "timestamp": asyncio.get_event_loop().time()
                    },
                    error=ErrorCodes.success()
                )
                
        except Exception as e:
            yield CommonResponse(
                data={"session_id": session_id},
                error=ErrorCodes.internal_error(f"互動處理失敗: {str(e)}")
            )
    
    @get_service_info_handler
    async def get_service_info(self) -> ServiceInfoResponse:
        """服務資訊查詢"""
        return ServiceInfoResponse(
            service_name=f"{self.processor_name}Service",
            version="1.0.0",
            models=[
                ModelInfo(
                    model_id="text_processor_v1",
                    version="1.0.0",
                    supported_languages=["zh", "en"],
                    support_streaming=True,
                    description="通用文本處理模型，支援大小寫轉換、長度統計等功能"
                )
            ],
            error=ErrorCodes.success()
        )

# 使用範例
async def advanced_example():
    """進階使用範例"""
    brick = TextProcessorBrick("AdvancedProcessor")
    
    # 測試單次處理
    print("=== 單次處理測試 ===")
    request = CommonRequest(data={"text": "hello world"})
    response = await brick.run_unary(request)
    print(f"處理結果: {response.data}")
    
    # 測試串流輸出
    print("\n=== 串流輸出測試 ===")
    request = CommonRequest(data={"text": "ABC"})
    async for response in brick.run_output_streaming(request):
        print(f"字符: {response.data}")
    
    # 測試服務資訊
    print("\n=== 服務資訊 ===")
    info = await brick.run_get_service_info()
    print(f"服務: {info.service_name}, 版本: {info.version}")
    print(f"模型: {info.models[0].model_id}")

asyncio.run(advanced_example())
```

### 3. gRPC 服務端建立與部署

```python
# grpc_server.py
import asyncio
from llmbrick.servers.grpc.server import GrpcServer
from text_processor_brick import TextProcessorBrick

async def start_grpc_server():
    """啟動 gRPC 服務端"""
    
    # 建立 gRPC 服務器
    server = GrpcServer(
        port=50051,
        max_workers=10,
        options=[
            ('grpc.keepalive_time_ms', 30000),
            ('grpc.keepalive_timeout_ms', 5000),
            ('grpc.keepalive_permit_without_calls', True),
            ('grpc.http2.max_pings_without_data', 0),
            ('grpc.http2.min_time_between_pings_ms', 10000),
            ('grpc.http2.min_ping_interval_without_data_ms', 300000)
        ]
    )
    
    # 建立並註冊 Brick 服務
    text_processor = TextProcessorBrick(
        processor_name="ProductionTextProcessor",
        verbose=True  # 啟用詳細日誌
    )
    
    server.register_service(text_processor)
    
    print("🚀 gRPC 服務器啟動中...")
    print(f"📡 監聽地址: localhost:50051")
    print(f"🔧 服務名稱: {text_processor.processor_name}")
    
    try:
        await server.start()
    except KeyboardInterrupt:
        print("\n⏹️  服務器關閉中...")
        await server.stop()

if __name__ == "__main__":
    asyncio.run(start_grpc_server())
```

### 4. gRPC 客戶端連接與使用

```python
# grpc_client.py
import asyncio
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest

async def grpc_client_example():
    """gRPC 客戶端使用範例"""
    
    # 建立 gRPC 客戶端
    client = CommonBrick.toGrpcClient("localhost:50051")
    
    print("🔗 連接到 gRPC 服務器...")
    
    try:
        # 1. 查詢服務資訊
        print("\n=== 服務資訊查詢 ===")
        service_info = await client.run_get_service_info()
        print(f"服務名稱: {service_info.service_name}")
        print(f"版本: {service_info.version}")
        if service_info.models:
            model = service_info.models[0]
            print(f"模型: {model.model_id} (v{model.version})")
            print(f"支援語言: {', '.join(model.supported_languages)}")
            print(f"支援串流: {'是' if model.support_streaming else '否'}")
        
        # 2. 單次請求測試
        print("\n=== 單次請求測試 ===")
        request = CommonRequest(data={"text": "hello grpc world"})
        response = await client.run_unary(request)
        
        if response.error.code == 200:
            print(f"✅ 處理成功")
            print(f"原文: {response.data['original']}")
            print(f"處理後: {response.data['processed']}")
            print(f"長度: {response.data['length']}")
        else:
            print(f"❌ 處理失敗: {response.error.message}")
        
        # 3. 串流輸出測試
        print("\n=== 串流輸出測試 ===")
        request = CommonRequest(data={"text": "Stream"})
        print("串流處理中...")
        
        async for response in client.run_output_streaming(request):
            if response.error.code == 200:
                data = response.data
                print(f"位置 {data['position']}: '{data['character']}' "
                      f"({'字母' if data['is_alpha'] else '非字母'}) "
                      f"進度: {data['progress']}")
            else:
                print(f"❌ 串流錯誤: {response.error.message}")
                break
        
        # 4. 輸入串流測試
        print("\n=== 輸入串流測試 ===")
        
        async def input_generator():
            """生成輸入串流"""
            texts = ["Hello", "gRPC", "Streaming", "World"]
            for text in texts:
                print(f"📤 發送: {text}")
                yield CommonRequest(data={"text": text})
                await asyncio.sleep(0.5)
        
        response = await client.run_input_streaming(input_generator())
        if response.error.code == 200:
            print(f"✅ 批次處理完成")
            print(f"處理數量: {response.data['batch_size']}")
            print(f"總長度: {response.data['total_length']}")
            print(f"平均長度: {response.data['average_length']:.2f}")
        else:
            print(f"❌ 批次處理失敗: {response.error.message}")
        
        # 5. 雙向串流測試
        print("\n=== 雙向串流測試 ===")
        
        async def bidi_input_generator():
            """生成雙向串流輸入"""
            messages = ["hello", "how are you", "grpc is great", "exit"]
            for msg in messages:
                print(f"📤 發送: {msg}")
                yield CommonRequest(data={"text": msg})
                await asyncio.sleep(1)
        
        print("雙向串流通訊中...")
        async for response in client.run_bidi_streaming(bidi_input_generator()):
            if response.error.code == 200:
                data = response.data
                if "message" in data:  # 結束訊息
                    print(f"🏁 {data['message']}, 總訊息數: {data['total_messages']}")
                else:  # 正常處理訊息
                    print(f"📥 收到回應 #{data['message_count']}: "
                          f"'{data['original']}' -> '{data['processed']}'")
            else:
                print(f"❌ 雙向串流錯誤: {response.error.message}")
                break
    
    except Exception as e:
        print(f"❌ 客戶端錯誤: {str(e)}")
    
    print("\n🔚 客戶端測試完成")

if __name__ == "__main__":
    asyncio.run(grpc_client_example())
```

---

## 核心 API / 類別 / 函式深度解析

### [`CommonBrick`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/common/common.py#L15) 類別

#### 類別簽名與繼承關係

```python
class CommonBrick(BaseBrick[CommonRequest, CommonResponse]):
    """
    CommonBrick: 基於 BaseBrick 的通用服務
    
    泛型參數:
        InputT: CommonRequest - 輸入請求類型
        OutputT: CommonResponse - 輸出回應類型
    """
    brick_type = BrickType.COMMON  # 標識為 COMMON 類型 Brick
```

#### 核心方法詳解

##### [`toGrpcClient()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/bricks/common/common.py#L37) - gRPC 客戶端轉換

```python
@classmethod
def toGrpcClient(cls, remote_address: str, **kwargs) -> CommonBrick
```

**功能**：將 CommonBrick 轉換為異步 gRPC 客戶端

**參數詳解**：
- `remote_address: str` - gRPC 伺服器地址
  - 格式：`"host:port"`（如 `"localhost:50051"`）
  - 支援 IPv4/IPv6 地址
  - 支援域名解析
- `**kwargs` - 傳遞給 CommonBrick 建構子的額外參數
  - `verbose: bool = True` - 是否啟用詳細日誌
  - 其他自訂初始化參數

**回傳值**：配置為 gRPC 客戶端的 CommonBrick 實例

**內部實作原理**：
1. 建立 CommonBrick 實例
2. 為每種通訊模式動態註冊 gRPC 處理器
3. 每個處理器內部建立 gRPC 通道和客戶端存根
4. 自動處理 Protocol Buffer 與 Python 物件轉換

**使用範例**：
```python
# 基本用法
client = CommonBrick.toGrpcClient("localhost:50051")

# 帶參數用法
client = CommonBrick.toGrpcClient(
    "production-server:443",
    verbose=False
)

# 使用客戶端
request = CommonRequest(data={"message": "Hello"})
response = await client.run_unary(request)
```

**注意事項**：
- 每次調用會建立新的 gRPC 通道，適合短期使用
- 長期使用建議實作連線池管理
- 自動處理連線錯誤和重試機制

#### 標準執行方法

##### [`run_unary()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L233) - 單次請求執行

```python
async def run_unary(self, input_data: CommonRequest) -> CommonResponse
```

**功能**：執行單次請求/回應處理

**參數**：
- `input_data: CommonRequest` - 輸入請求物件

**回傳**：`CommonResponse` - 處理結果

**使用場景**：
- 簡單的資料轉換
- 狀態查詢
- 驗證操作
- 計算任務

**範例**：
```python
brick = CommonBrick()

@brick.unary()
async def calculator(request: CommonRequest) -> CommonResponse:
    a = request.data.get("a", 0)
    b = request.data.get("b", 0)
    operation = request.data.get("operation", "add")
    
    if operation == "add":
        result = a + b
    elif operation == "multiply":
        result = a * b
    else:
        return CommonResponse(
            error=ErrorCodes.parameter_invalid("operation")
        )
    
    return CommonResponse(
        data={"result": result},
        error=ErrorCodes.success()
    )

# 使用
request = CommonRequest(data={"a": 10, "b": 5, "operation": "add"})
response = await brick.run_unary(request)
print(response.data["result"])  # 15
```

##### [`run_output_streaming()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L258) - 輸出串流執行

```python
async def run_output_streaming(self, input_data: CommonRequest) -> AsyncIterator[CommonResponse]
```

**功能**：執行輸出串流處理，從單一輸入產生多個輸出

**參數**：
- `input_data: CommonRequest` - 輸入請求物件

**回傳**：`AsyncIterator[CommonResponse]` - 異步回應迭代器

**使用場景**：
- 大型資料分頁輸出
- 即時資料串流
- 長時間處理的進度回報
- 聊天機器人回應生成

**範例**：
```python
@brick.output_streaming()
async def data_paginator(request: CommonRequest) -> AsyncIterator[CommonResponse]:
    """資料分頁串流輸出"""
    page_size = request.data.get("page_size", 10)
    total_items = request.data.get("total_items", 100)
    
    for page in range(0, total_items, page_size):
        # 模擬資料庫查詢
        await asyncio.sleep(0.1)
        
        items = [f"item_{i}" for i in range(page, min(page + page_size, total_items))]
        
        yield CommonResponse(
            data={
                "page": page // page_size + 1,
                "items": items,
                "has_more": page + page_size < total_items
            },
            error=ErrorCodes.success()
        )

# 使用
request = CommonRequest(data={"page_size": 5, "total_items": 23})
async for response in brick.run_output_streaming(request):
    print(f"第 {response.data['page']} 頁: {response.data['items']}")
```

##### [`run_input_streaming()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L274) - 輸入串流執行

```python
async def run_input_streaming(self, input_stream: AsyncIterator[CommonRequest]) -> CommonResponse
```

**功能**：執行輸入串流處理，從多個輸入產生單一輸出

**參數**：
- `input_stream: AsyncIterator[CommonRequest]` - 輸入請求串流

**回傳**：`CommonResponse` - 最終處理結果

**使用場景**：
- 批次資料處理
- 檔案上傳處理
- 資料聚合分析
- 串流資料收集

**範例**：
```python
@brick.input_streaming()
async def batch_analyzer(request_stream: AsyncIterator[CommonRequest]) -> CommonResponse:
    """批次資料分析"""
    total_count = 0
    sum_values = 0
    categories = {}
    
    async for request in request_stream:
        value = request.data.get("value", 0)
        category = request.data.get("category", "unknown")
        
        total_count += 1
        sum_values += value
        categories[category] = categories.get(category, 0) + 1
    
    if total_count == 0:
        return CommonResponse(
            error=ErrorCodes.parameter_invalid("input_stream", "沒有收到任何資料")
        )
    
    return CommonResponse(
        data={
            "total_count": total_count,
            "average_value": sum_values / total_count,
            "categories": categories,
            "summary": f"處理了 {total_count} 筆資料，平均值為 {sum_values/total_count:.2f}"
        },
        error=ErrorCodes.success()
    )

# 使用
async def data_generator():
    data_points = [
        {"value": 10, "category": "A"},
        {"value": 20, "category": "B"},
        {"value": 15, "category": "A"},
        {"value": 25, "category": "C"}
    ]
    for point in data_points:
        yield CommonRequest(data=point)

response = await brick.run_input_streaming(data_generator())
print(response.data["summary"])
```

##### [`run_bidi_streaming()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L288) - 雙向串流執行

```python
async def run_bidi_streaming(self, input_stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]
```

**功能**：執行雙向串流處理，即時處理輸入並產生輸出

**參數**：
- `input_stream: AsyncIterator[CommonRequest]` - 輸入請求串流

**回傳**：`AsyncIterator[CommonResponse]` - 輸出回應串流

**使用場景**：
- 即時聊天系統
- 互動式資料處理
- 即時翻譯服務
- 遊戲狀態同步

**範例**：
```python
@brick.bidi_streaming()
async def chat_processor(request_stream: AsyncIterator[CommonRequest]) -> AsyncIterator[CommonResponse]:
    """聊天處理器"""
    conversation_history = []
    
    async for request in request_stream:
        message = request.data.get("message", "")
        user_id = request.data.get("user_id", "anonymous")
        
        if not message:
            yield CommonResponse(
                error=ErrorCodes.parameter_invalid("message")
            )
            continue
        
        # 記錄對話歷史
        conversation_history.append(f"{user_id}: {message}")
        
        # 簡單的回應邏輯
        if message.lower() == "history":
            response_text = "\n".join(conversation_history[-5:])  # 最近5條
        elif message.lower() == "clear":
            conversation_history.clear()
            response_text = "對話歷史已清除"
        else:
            response_text = f"收到來自 {user_id} 的訊息: {message}"
        
        yield CommonResponse(
            data={
                "response": response_text,
                "timestamp": asyncio.get_event_loop().time(),
                "conversation_length": len(conversation_history)
            },
            error=ErrorCodes.success()
        )

# 使用
async def chat_input():
    messages = [
        {"message": "Hello", "user_id": "Alice"},
        {"message": "How are you?", "user_id": "Bob"},
        {"message": "history", "user_id": "Alice"}
    ]
    for msg in messages:
        yield CommonRequest(data=msg)
        await asyncio.sleep(1)

async for response in brick.run_bidi_streaming(chat_input()):
    print(response.data["response"])
```

##### [`run_get_service_info()`](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py#L245) - 服務資訊查詢

```python
async def run_get_service_info(self) -> ServiceInfoResponse
```

**功能**：查詢服務的基本資訊和能力

**回傳**：`ServiceInfoResponse` - 服務資訊物件

**使用場景**：
- 服務發現
- 健康檢查
- 能力查詢
- 版本檢查

**範例**：
```python
@brick.get_service_info()
async def service_info() -> ServiceInfoResponse:
    """服務資訊提供"""
    return ServiceInfoResponse(
        service_name="MyAdvancedService",
        version="2.1.0",
        models=[
            ModelInfo(
                model_id="text_processor",
                version="1.0.0",
                supported_languages=["zh-TW", "zh-CN", "en-US"],
                support_streaming=True,
                description="高效能文本處理模型"
            ),
            ModelInfo(
                model_id="data_analyzer",
                version="1.2.0",
                supported_languages=["universal"],
                support_streaming=False,
                description="通用資料分析模型"
            )
        ],
        error=ErrorCodes.success()
    )

# 使用
info = await brick.run_get_service_info()
print(f"服務: {info.service_name} v{info.version}")
for model in info.models:
    print(f"  模型: {model.model_id} - {model.description}")
```

### 裝飾器系統詳解

CommonBrick 提供兩套裝飾器系統：**實例裝飾器**（動態註冊）和**類別裝飾器**（靜態註冊）。

#### 實例裝飾器（推薦用於動態場景）

```python
# 建立 Brick 實例
brick = CommonBrick()

# 使用實例裝飾器動態註冊處理器
@brick.unary()
async def dynamic_handler(request: CommonRequest) -> CommonResponse:
    return CommonResponse(data={"type": "dynamic"})

@brick.output_streaming()
async def dynamic_streaming(request: CommonRequest) -> AsyncIterator[CommonResponse]:
    for i in range(3):
        yield CommonResponse(data={"count": i})
```

**優點**：
- 靈活性高，可在運行時動態註冊
- 適合插件系統和動態配置
- 可以有條件地註冊處理器

**缺點**：
- 需要先建立實例
- 不適合類別繼承場景

#### 類別裝飾器（推薦用於繼承場景）

```python
from llmbrick.core.brick import unary_handler, output_streaming_handler

class MyBrick(CommonBrick):
    @unary_handler
    async def static_handler(self, request: CommonRequest) -> CommonResponse:
        return CommonResponse(data={"type": "static"})
    
    @output_streaming_handler
    async def static_streaming(self, request: CommonRequest) -> AsyncIterator[CommonResponse]:
        for i in range(3):
            yield CommonResponse(data={"count": i})
```

**優點**：
- 清晰的類別結構
- 自動註冊，無需額外步驟
- 適合物件導向設計
- 支援繼承和多型

**缺點**：
- 靜態註冊，運行時無法修改
- 每個類別只能有一個同類型處理器

---

## 效能優化與最佳實踐

### 1. 異步處理優化

#### 並發控制

```python
import asyncio
from asyncio import Semaphore
from typing import List, AsyncIterator
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse

class HighPerformanceBrick(CommonBrick):
    """高效能 CommonBrick 實作"""
    
    def __init__(self, 
                 max_concurrent_requests: int = 100,
                 request_timeout: float = 30.0,
                 **kwargs):
        super().__init__(**kwargs)
        
        # 並發控制
        self.semaphore = Semaphore(max_concurrent_requests)
        self.request_timeout = request_timeout
        
        # 效能指標
        self.performance_stats = {
            "total_requests": 0,
            "concurrent_requests": 0,
            "max_concurrent": 0,
            "average_response_time": 0.0,
            "total_response_time": 0.0
        }
    
    async def _with_concurrency_control(self, coro):
        """並發控制包裝器"""
        async with self.semaphore:
            self.performance_stats["concurrent_requests"] += 1
            self.performance_stats["max_concurrent"] = max(
                self.performance_stats["max_

concurrent"],
                self.performance_stats["concurrent_requests"]
            )
            
            start_time = asyncio.get_event_loop().time()
            
            try:
                result = await asyncio.wait_for(coro, timeout=self.request_timeout)
                
                # 更新效能統計
                response_time = asyncio.get_event_loop().time() - start_time
                self.performance_stats["total_requests"] += 1
                self.performance_stats["total_response_time"] += response_time
                self.performance_stats["average_response_time"] = (
                    self.performance_stats["total_response_time"] / 
                    self.performance_stats["total_requests"]
                )
                
                return result
                
            finally:
                self.performance_stats["concurrent_requests"] -= 1
    
    @unary_handler
    async def high_performance_handler(self, request: CommonRequest) -> CommonResponse:
        """高效能處理器"""
        
        async def process_request():
            # 模擬處理邏輯
            data = request.data
            operation = data.get("operation", "default")
            
            if operation == "cpu_intensive":
                # CPU 密集型任務
                result = await self._cpu_intensive_task(data)
            elif operation == "io_intensive":
                # I/O 密集型任務
                result = await self._io_intensive_task(data)
            else:
                # 一般處理
                result = {"processed": True, "data": data}
            
            return CommonResponse(
                data=result,
                error=ErrorCodes.success()
            )
        
        return await self._with_concurrency_control(process_request())
    
    async def _cpu_intensive_task(self, data: dict) -> dict:
        """CPU 密集型任務（在執行器中運行）"""
        import concurrent.futures
        
        def cpu_work():
            # 模擬 CPU 密集型計算
            result = sum(i * i for i in range(10000))
            return {"computation_result": result, "input": data}
        
        # 在線程池中執行 CPU 密集型任務
        loop = asyncio.get_event_loop()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            result = await loop.run_in_executor(executor, cpu_work)
        
        return result
    
    async def _io_intensive_task(self, data: dict) -> dict:
        """I/O 密集型任務"""
        # 模擬異步 I/O 操作
        await asyncio.sleep(0.1)
        return {"io_result": "completed", "input": data}
    
    def get_performance_stats(self) -> dict:
        """獲取效能統計"""
        return self.performance_stats.copy()

# 效能測試範例
async def performance_test():
    """效能測試"""
    
    brick = HighPerformanceBrick(
        max_concurrent_requests=50,
        request_timeout=10.0
    )
    
    print("🚀 開始效能測試...")
    
    # 建立測試請求
    requests = [
        CommonRequest(data={"operation": "cpu_intensive", "id": i})
        for i in range(20)
    ] + [
        CommonRequest(data={"operation": "io_intensive", "id": i})
        for i in range(30)
    ]
    
    # 並發執行請求
    start_time = asyncio.get_event_loop().time()
    
    tasks = [brick.run_unary(req) for req in requests]
    responses = await asyncio.gather(*tasks, return_exceptions=True)
    
    end_time = asyncio.get_event_loop().time()
    
    # 分析結果
    successful = sum(1 for r in responses if isinstance(r, CommonResponse) and r.error.code == 200)
    failed = len(responses) - successful
    total_time = end_time - start_time
    
    print(f"📊 效能測試結果:")
    print(f"   總請求數: {len(requests)}")
    print(f"   成功: {successful}")
    print(f"   失敗: {failed}")
    print(f"   總時間: {total_time:.2f}s")
    print(f"   平均 QPS: {len(requests) / total_time:.2f}")
    
    # 顯示內部統計
    stats = brick.get_performance_stats()
    print(f"   平均回應時間: {stats['average_response_time']:.3f}s")
    print(f"   最大並發數: {stats['max_concurrent']}")

asyncio.run(performance_test())
```

### 2. 快取策略優化

```python
import asyncio
import hashlib
import json
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, Tuple
from dataclasses import dataclass
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse
from llmbrick.core.error_codes import ErrorCodes

@dataclass
class CacheConfig:
    """快取配置"""
    max_size: int = 1000
    ttl_seconds: int = 3600
    enable_lru: bool = True
    enable_compression: bool = False
    hit_rate_threshold: float = 0.7

class SmartCache:
    """智能快取系統"""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.cache: Dict[str, Tuple[Any, datetime, int]] = {}  # value, timestamp, access_count
        self.access_order: List[str] = []  # LRU 順序
        self.stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "size": 0
        }
    
    def _generate_key(self, data: Dict[str, Any]) -> str:
        """生成快取鍵值"""
        serialized = json.dumps(data, sort_keys=True)
        return hashlib.md5(serialized.encode()).hexdigest()
    
    def _is_expired(self, timestamp: datetime) -> bool:
        """檢查是否過期"""
        return datetime.now() - timestamp > timedelta(seconds=self.config.ttl_seconds)
    
    def _evict_lru(self):
        """LRU 淘汰"""
        if not self.access_order:
            return
        
        oldest_key = self.access_order.pop(0)
        if oldest_key in self.cache:
            del self.cache[oldest_key]
            self.stats["evictions"] += 1
    
    def _update_access_order(self, key: str):
        """更新訪問順序"""
        if self.config.enable_lru:
            if key in self.access_order:
                self.access_order.remove(key)
            self.access_order.append(key)
    
    def get(self, data: Dict[str, Any]) -> Optional[Any]:
        """獲取快取"""
        key = self._generate_key(data)
        
        if key not in self.cache:
            self.stats["misses"] += 1
            return None
        
        value, timestamp, access_count = self.cache[key]
        
        # 檢查過期
        if self._is_expired(timestamp):
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
            self.stats["misses"] += 1
            return None
        
        # 更新訪問記錄
        self.cache[key] = (value, timestamp, access_count + 1)
        self._update_access_order(key)
        self.stats["hits"] += 1
        
        return value
    
    def set(self, data: Dict[str, Any], value: Any):
        """設定快取"""
        key = self._generate_key(data)
        
        # 檢查容量限制
        if len(self.cache) >= self.config.max_size and key not in self.cache:
            self._evict_lru()
        
        # 設定快取
        self.cache[key] = (value, datetime.now(), 0)
        self._update_access_order(key)
        self.stats["size"] = len(self.cache)
    
    def get_hit_rate(self) -> float:
        """獲取命中率"""
        total = self.stats["hits"] + self.stats["misses"]
        return self.stats["hits"] / total if total > 0 else 0.0
    
    def clear_expired(self):
        """清理過期項目"""
        expired_keys = []
        for key, (_, timestamp, _) in self.cache.items():
            if self._is_expired(timestamp):
                expired_keys.append(key)
        
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_order:
                self.access_order.remove(key)
        
        self.stats["size"] = len(self.cache)
        return len(expired_keys)

class CacheOptimizedBrick(CommonBrick):
    """快取優化的 Brick"""
    
    def __init__(self, cache_config: CacheConfig = None, **kwargs):
        super().__init__(**kwargs)
        
        self.cache_config = cache_config or CacheConfig()
        self.cache = SmartCache(self.cache_config)
        
        # 啟動快取維護任務
        asyncio.create_task(self._cache_maintenance())
    
    async def _cache_maintenance(self):
        """快取維護任務"""
        while True:
            try:
                await asyncio.sleep(300)  # 每5分鐘執行一次
                
                # 清理過期項目
                expired_count = self.cache.clear_expired()
                
                # 檢查命中率
                hit_rate = self.cache.get_hit_rate()
                
                print(f"🧹 快取維護: 清理 {expired_count} 個過期項目, "
                      f"命中率: {hit_rate:.2%}, "
                      f"大小: {self.cache.stats['size']}")
                
                # 如果命中率過低，調整策略
                if hit_rate < self.cache_config.hit_rate_threshold:
                    print(f"⚠️  快取命中率過低 ({hit_rate:.2%}), 考慮調整快取策略")
                
            except Exception as e:
                print(f"快取維護錯誤: {e}")
    
    @unary_handler
    async def cached_handler(self, request: CommonRequest) -> CommonResponse:
        """帶快取的處理器"""
        
        # 嘗試從快取獲取
        cached_result = self.cache.get(request.data)
        if cached_result:
            return CommonResponse(
                data={**cached_result, "from_cache": True},
                error=ErrorCodes.success()
            )
        
        # 執行實際處理
        try:
            result = await self._process_data(request.data)
            
            # 存入快取
            self.cache.set(request.data, result)
            
            return CommonResponse(
                data={**result, "from_cache": False},
                error=ErrorCodes.success()
            )
            
        except Exception as e:
            return CommonResponse(
                error=ErrorCodes.internal_error("處理失敗", str(e))
            )
    
    async def _process_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """實際資料處理邏輯"""
        # 模擬複雜處理
        await asyncio.sleep(0.5)
        
        operation = data.get("operation", "default")
        
        if operation == "calculate":
            numbers = data.get("numbers", [])
            result = {
                "sum": sum(numbers),
                "average": sum(numbers) / len(numbers) if numbers else 0,
                "count": len(numbers)
            }
        elif operation == "transform":
            text = data.get("text", "")
            result = {
                "original": text,
                "uppercase": text.upper(),
                "length": len(text),
                "words": len(text.split())
            }
        else:
            result = {"processed": True, "operation": operation}
        
        return result
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """獲取快取統計"""
        stats = self.cache.stats.copy()
        stats["hit_rate"] = self.cache.get_hit_rate()
        stats["config"] = {
            "max_size": self.cache_config.max_size,
            "ttl_seconds": self.cache_config.ttl_seconds,
            "enable_lru": self.cache_config.enable_lru
        }
        return stats

# 快取效能測試
async def cache_performance_test():
    """快取效能測試"""
    
    config = CacheConfig(
        max_size=100,
        ttl_seconds=60,
        enable_lru=True
    )
    
    brick = CacheOptimizedBrick(cache_config=config)
    
    print("🧪 快取效能測試開始...")
    
    # 測試資料
    test_requests = [
        CommonRequest(data={"operation": "calculate", "numbers": [1, 2, 3, 4, 5]}),
        CommonRequest(data={"operation": "transform", "text": "Hello World"}),
        CommonRequest(data={"operation": "calculate", "numbers": [10, 20, 30]}),
        # 重複請求測試快取命中
        CommonRequest(data={"operation": "calculate", "numbers": [1, 2, 3, 4, 5]}),
        CommonRequest(data={"operation": "transform", "text": "Hello World"}),
    ]
    
    # 執行測試
    for i, request in enumerate(test_requests):
        start_time = asyncio.get_event_loop().time()
        response = await brick.run_unary(request)
        end_time = asyncio.get_event_loop().time()
        
        if response.error.code == 200:
            from_cache = response.data.get("from_cache", False)
            print(f"請求 {i+1}: {'快取命中' if from_cache else '實際處理'} "
                  f"({end_time - start_time:.3f}s)")
    
    # 顯示快取統計
    stats = brick.get_cache_stats()
    print(f"\n📊 快取統計:")
    print(f"   命中率: {stats['hit_rate']:.2%}")
    print(f"   命中次數: {stats['hits']}")
    print(f"   未命中次數: {stats['misses']}")
    print(f"   快取大小: {stats['size']}")

asyncio.run(cache_performance_test())
```

### 3. 批次處理優化

```python
import asyncio
from typing import List, AsyncIterator, Callable, Any
from dataclasses import dataclass
from llmbrick.bricks.common.common import CommonBrick
from llmbrick.protocols.models.bricks.common_types import CommonRequest, CommonResponse
from llmbrick.core.error_codes import ErrorCodes

@dataclass
class BatchConfig:
    """批次處理配置"""
    batch_size: int = 10
    max_wait_time: float = 1.0
    max_queue_size: int = 1000
    enable_adaptive_batching: bool = True

class BatchProcessor:
    """批次處理器"""
    
    def __init__(self, 
                 config: BatchConfig,
                 process_func: Callable[[List[Any]], List[Any]]):
        self.config = config
        self.process_func = process_func
        self.queue: List[Tuple[Any, asyncio.Future]] = []
        self.processing = False
        
        # 啟動批次處理任務
        asyncio.create_task(self._batch_processing_loop())
    
    async def add_to_batch(self, item: Any) -> Any:
        """添加項目到批次"""
        if len(self.queue) >= self.config.max_queue_size:
            raise Exception(f"批次佇列已滿: {self.config.max_queue_size}")
        
        future = asyncio.Future()
        self.queue.append((item, future))
        
        # 如果達到批次大小，立即處理
        if len(self.queue) >= self.config.batch_size:
            asyncio.create_task(self._process_batch())
        
        return await future
    
    async def _batch_processing_loop(self):
        """批次處理循環"""
        while True:
            try:
                await asyncio.sleep(self.config.max_wait_time)
                
                if self.queue and not self.processing:
                    await self._process_batch()
                    
            except Exception as e:
                print(f"批次處理循環錯誤: {e}")
    
    async def _process_batch(self):
        """處理批次"""
        if self.processing or not self.queue:
            return
        
        self.processing = True
        
        try:
            # 取出批次項目
            batch_size = min(len(self.queue), self.config.batch_size)
            batch_items = self.queue[:batch_size]
            self.queue = self.queue[batch_size:]
            
            # 分離資料和 Future
            items = [item for item, _ in batch_items]
            futures = [future for _, future in batch_items]
            
            # 執行批次處理
            results = await self.process_func(items)
            
            # 設定結果
            for future, result in zip(futures, results):
                if not future.done():
                    future.set_result(result)
                    
        except Exception as e:
            # 設定錯誤
            for _, future in batch_items:
                if not future.done():
                    future.set_exception(e)
        finally:
            self.processing = False

class BatchOptimizedBrick(CommonBrick):
    """批次優化的 Brick"""
    
    def __init__(self, batch_config: BatchConfig = None, **kwargs):
        super().__init__(**kwargs)
        
        self.batch_config = batch_config or BatchConfig()
        
        # 建立不同類型的批次處理器
        self.text_processor = BatchProcessor(
            self.batch_config,
            self._batch_process_text
        )
        
        self.number_processor = BatchProcessor(
            self.batch_config,
            self._batch_process_numbers
        )
    
    @unary_handler
    async def batch_optimized_handler(self, request: CommonRequest) -> CommonResponse:
        """批次優化的處理器"""
        
        try:
            data_type = request.data.get("type", "text")
            data = request.data.get("data")
            
            if data_type == "text":
                result = await self.text_processor.add_to_batch(data)
            elif data_type == "number":
                result = await self.number_processor.add_to_batch(data)
            else:
                return CommonResponse(
                    error=ErrorCodes.parameter_invalid("type", f"不支援的資料類型: {data_type}")
                )
            
            return CommonResponse(
                data={"result": result, "processed_in_batch": True},
                error=ErrorCodes.success()
            )
            
        except Exception as e:
            return CommonResponse(
                error=ErrorCodes.internal_error("批次處理失敗", str(e))
            )
    
    async def _batch_process_text(self, texts: List[str]) -> List[Dict[str, Any]]:
        """批次處理文本"""
        print(f"📦 批次處理 {len(texts)} 個文本")
        
        # 模擬批次處理（比單個處理更高效）
        await asyncio.sleep(0.1)  # 批次處理時間
        
        results = []
        for text in texts:
            results.append({
                "original": text,
                "length": len(text),
                "uppercase": text.upper(),
                "word_count": len(text.split())
            })
        
        return results
    
    async def _batch_process_numbers(self, numbers: List[float]) -> List[Dict[str, Any]]:
        """批次處理數字"""
        print(f"📦 批次處理 {len(numbers)} 個數字")
        
        # 模擬批次處理
        await asyncio.sleep(0.05)
        
        # 批次統計計算
        total = sum(numbers)
        average = total / len(numbers) if numbers else 0
        
        results = []
        for num in numbers:
            results.append({
                "original": num,
                "squared": num ** 2,
                "percentage_of_total": (num / total * 100) if total != 0 else 0,
                "deviation_from_avg": num - average
            })
        
        return results

# 批次處理測試
async def batch_processing_test():
    """批次處理測試"""
    
    config = BatchConfig(
        batch_size=5,
        max_wait_time=0.5,
        max_queue_size=100
    )
    
    brick = BatchOptimizedBrick(batch_config=config)
    
    print("🚀 批次處理測試開始...")
    
    # 建立測試請求
    text_requests = [
        CommonRequest(data={"type": "text", "data": f"測試文本 {i}"})
        for i in range(12)
    ]
    
    number_requests = [
        CommonRequest(data={"type": "number", "data": float(i * 10)})
        for i in range(8)
    ]
    
    # 混合請求測試
    all_requests = text_requests + number_requests
    
    # 並發發送請求
    start_time = asyncio.get_event_loop().time()
    
    tasks = [brick.run_unary(req) for req in all_requests]
    responses = await asyncio.gather(*tasks)
    
    end_time = asyncio.get_event_loop().time()
    
    # 分析結果
    successful = sum(1 for r in responses if r.error.code == 200)
    
    print(f"📊 批次處理結果:")
    print(f"   總請求數: {len(all_requests)}")
    print(f"   成功處理: {successful}")
    print(f"   總時間: {end_time - start_time:.2f}s")
    print(f"   平均每請求: {(end_time - start_time) / len(all_requests):.3f}s")

asyncio.run(batch_processing_test())
```

---

## FAQ / 進階問答

### Q1: CommonBrick 與其他 Brick 類型的關係是什麼？

**A**: CommonBrick 是整個 LLMBrick 框架的基礎類別，其他所有專用 Brick 都繼承自 CommonBrick：

```python
# 繼承關係示例
from llmbrick.bricks.common.common import CommonBrick

class LLMBrick(CommonBrick):
    """語言模型 Brick，繼承 CommonBrick 的所有功能"""
    pass

class GuardBrick(CommonBrick):
    """安全防護 Brick，繼承 CommonBrick 的所有功能"""
    pass

# 這意味著所有 Brick 都具備：
# 1. 相同的通訊協定（gRPC）
# 2. 統一的錯誤處理機制
# 3. 標準的資料模型（CommonRequest/CommonResponse）
# 4. 五種通訊模式支援
```

**優勢**：
- **統一介面**：所有 Brick 都可以互換使用
- **組合能力**：可以輕鬆組合不同類型的 Brick
- **擴展性**：新的 Brick 類型可以快速開發

---

## 參考資源與延伸閱讀

### 官方文件

- [LLMBrick 框架介紹](../../intro.md) - 框架整體概述
- [gRPC Server 使用指南](../servers/grpc_server_guide.md) - gRPC 服務器詳細配置
- [BaseBrick API 文件](https://github.com/JiHungLin/llmbrick/blob/main/llmbrick/core/brick.py) - 基礎類別參考

### 外部資源

- [Protocol Buffer 官方文件](https://developers.google.com/protocol-buffers) - Protocol Buffer 語法和最佳實踐
- [gRPC Python 官方文件](https://grpc.io/docs/languages/python/) - gRPC Python 實作指南
- [asyncio 官方文件](https://docs.python.org/3/library/asyncio.html) - Python 異步程式設計

### 社群資源

- [GitHub 範例程式碼](https://github.com/JiHungLin/llmbrick/tree/main/examples/common_brick_define) - 完整範例程式碼
- [問題回報](https://github.com/JiHungLin/llmbrick/issues) - 回報 Bug 或功能請求

---

CommonBrick 不僅是一個技術組件，更是構建可擴展、可維護 AI 應用的基石。掌握其使用方法對於開發高品質的 LLM 應用至關重要。

*本指南持續更新中，如有問題或建議，歡迎參與社群討論！*
