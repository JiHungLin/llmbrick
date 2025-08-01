"""
LLMBrick 框架錯誤代碼工具類別

提供方便的錯誤代碼定義和ErrorDetail創建工廠方法，
統一框架內的錯誤處理標準。
"""

from typing import Optional
from llmbrick.protocols.models.bricks.common_types import ErrorDetail


class ErrorCodes:
    """
    統一的錯誤代碼定義類別
    
    包含HTTP標準狀態碼和框架特定的業務錯誤代碼，
    提供工廠方法來創建ErrorDetail對象。
    """
    
    # === HTTP 標準狀態碼 ===
    SUCCESS = 200
    CREATED = 201
    ACCEPTED = 202
    NO_CONTENT = 204
    
    # 客戶端錯誤 4xx
    BAD_REQUEST = 400
    UNAUTHORIZED = 401
    FORBIDDEN = 403
    NOT_FOUND = 404
    METHOD_NOT_ALLOWED = 405
    NOT_ACCEPTABLE = 406
    REQUEST_TIMEOUT = 408
    CONFLICT = 409
    GONE = 410
    LENGTH_REQUIRED = 411
    PRECONDITION_FAILED = 412
    PAYLOAD_TOO_LARGE = 413
    URI_TOO_LONG = 414
    UNSUPPORTED_MEDIA_TYPE = 415
    RANGE_NOT_SATISFIABLE = 416
    EXPECTATION_FAILED = 417
    UNPROCESSABLE_ENTITY = 422
    LOCKED = 423
    FAILED_DEPENDENCY = 424
    TOO_MANY_REQUESTS = 429
    
    # 伺服器錯誤 5xx
    INTERNAL_ERROR = 500
    NOT_IMPLEMENTED = 501
    BAD_GATEWAY = 502
    SERVICE_UNAVAILABLE = 503
    GATEWAY_TIMEOUT = 504
    HTTP_VERSION_NOT_SUPPORTED = 505
    INSUFFICIENT_STORAGE = 507
    LOOP_DETECTED = 508
    NOT_EXTENDED = 510
    
    # === 框架特定業務錯誤代碼 1xxx-9xxx ===
    
    # 通用錯誤 1xxx
    UNKNOWN_ERROR = 1000
    INITIALIZATION_ERROR = 1001
    CONFIGURATION_ERROR = 1002
    DEPENDENCY_ERROR = 1003
    
    # 驗證錯誤 2xxx
    VALIDATION_ERROR = 2000
    SCHEMA_VALIDATION_ERROR = 2001
    PARAMETER_MISSING = 2002
    PARAMETER_INVALID = 2003
    DATA_FORMAT_ERROR = 2004
    
    # 認證授權錯誤 3xxx
    AUTHENTICATION_ERROR = 3000
    AUTHORIZATION_ERROR = 3001
    TOKEN_EXPIRED = 3002
    TOKEN_INVALID = 3003
    PERMISSION_DENIED = 3004
    
    # 模型相關錯誤 4xxx
    MODEL_ERROR = 4000
    MODEL_NOT_FOUND = 4001
    MODEL_LOADING_ERROR = 4002
    MODEL_INFERENCE_ERROR = 4003
    MODEL_TIMEOUT = 4004
    MODEL_OVERLOAD = 4005
    
    # 外部服務錯誤 5xxx
    EXTERNAL_SERVICE_ERROR = 5000
    EXTERNAL_API_ERROR = 5001
    EXTERNAL_SERVICE_TIMEOUT = 5002
    EXTERNAL_SERVICE_UNAVAILABLE = 5003
    RATE_LIMIT_EXCEEDED = 5004
    
    # 資源錯誤 6xxx
    RESOURCE_ERROR = 6000
    RESOURCE_NOT_FOUND = 6001
    RESOURCE_EXHAUSTED = 6002
    RESOURCE_LOCKED = 6003
    RESOURCE_CONFLICT = 6004
    
    # 網路錯誤 7xxx
    NETWORK_ERROR = 7000
    CONNECTION_ERROR = 7001
    TIMEOUT_ERROR = 7002
    DNS_ERROR = 7003
    SSL_ERROR = 7004
    
    # 儲存錯誤 8xxx
    STORAGE_ERROR = 8000
    DATABASE_ERROR = 8001
    FILE_NOT_FOUND = 8002
    PERMISSION_ERROR = 8003
    DISK_FULL = 8004
    
    # 業務邏輯錯誤 9xxx
    BUSINESS_ERROR = 9000
    WORKFLOW_ERROR = 9001
    STATE_ERROR = 9002
    CONSTRAINT_VIOLATION = 9003
    
    # === 錯誤代碼描述映射 ===
    _ERROR_MESSAGES = {
        # HTTP 狀態碼
        200: "成功",
        201: "已創建",
        202: "已接受",
        204: "無內容",
        400: "請求錯誤",
        401: "未授權",
        403: "禁止訪問",
        404: "未找到",
        405: "方法不允許",
        408: "請求超時",
        409: "衝突",
        422: "無法處理的實體",
        429: "請求過多",
        500: "內部伺服器錯誤",
        501: "未實現",
        502: "錯誤網關",
        503: "服務不可用",
        504: "網關超時",
        
        # 框架業務錯誤
        1000: "未知錯誤",
        1001: "初始化錯誤",
        1002: "配置錯誤",
        1003: "依賴錯誤",
        
        2000: "驗證錯誤",
        2001: "Schema驗證錯誤",
        2002: "參數缺失",
        2003: "參數無效",
        2004: "數據格式錯誤",
        
        3000: "認證錯誤",
        3001: "授權錯誤",
        3002: "Token已過期",
        3003: "Token無效",
        3004: "權限拒絕",
        
        4000: "模型錯誤",
        4001: "模型未找到",
        4002: "模型載入錯誤",
        4003: "模型推理錯誤",
        4004: "模型超時",
        4005: "模型過載",
        
        5000: "外部服務錯誤",
        5001: "外部API錯誤",
        5002: "外部服務超時",
        5003: "外部服務不可用",
        5004: "超出速率限制",
        
        6000: "資源錯誤",
        6001: "資源未找到",
        6002: "資源耗盡",
        6003: "資源鎖定",
        6004: "資源衝突",
        
        7000: "網路錯誤",
        7001: "連接錯誤",
        7002: "超時錯誤",
        7003: "DNS錯誤",
        7004: "SSL錯誤",
        
        8000: "存儲錯誤",
        8001: "資料庫錯誤",
        8002: "文件未找到",
        8003: "權限錯誤",
        8004: "磁碟空間不足",
        
        9000: "業務錯誤",
        9001: "工作流錯誤",
        9002: "狀態錯誤",
        9003: "約束違反",
    }
    
    @classmethod
    def get_message(cls, code: int) -> str:
        """獲取錯誤代碼對應的默認訊息"""
        return cls._ERROR_MESSAGES.get(code, f"未知錯誤 ({code})")
    
    @classmethod
    def create_error(cls, code: int, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """
        創建ErrorDetail對象的工廠方法
        
        Args:
            code: 錯誤代碼
            message: 錯誤訊息（可選，不提供時使用默認訊息）
            detail: 錯誤詳細信息（可選）
            
        Returns:
            ErrorDetail: 錯誤詳情對象
        """
        return ErrorDetail(
            code=code,
            message=message or cls.get_message(code),
            detail=detail
        )
    
    @classmethod
    def success(cls) -> ErrorDetail:
        """創建成功狀態的ErrorDetail"""
        return cls.create_error(cls.SUCCESS)
    
    @classmethod
    def bad_request(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建請求錯誤的ErrorDetail"""
        return cls.create_error(cls.BAD_REQUEST, message, detail)
    
    @classmethod
    def unauthorized(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建未授權錯誤的ErrorDetail"""
        return cls.create_error(cls.UNAUTHORIZED, message, detail)
    
    @classmethod
    def forbidden(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建禁止訪問錯誤的ErrorDetail"""
        return cls.create_error(cls.FORBIDDEN, message, detail)
    
    @classmethod
    def not_found(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建未找到錯誤的ErrorDetail"""
        return cls.create_error(cls.NOT_FOUND, message, detail)
    
    @classmethod
    def timeout(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建超時錯誤的ErrorDetail"""
        return cls.create_error(cls.REQUEST_TIMEOUT, message, detail)
    
    @classmethod
    def internal_error(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建內部錯誤的ErrorDetail"""
        return cls.create_error(cls.INTERNAL_ERROR, message, detail)
    
    @classmethod
    def not_implemented(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建未實現錯誤的ErrorDetail"""
        return cls.create_error(cls.NOT_IMPLEMENTED, message, detail)
    
    @classmethod
    def service_unavailable(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建服務不可用錯誤的ErrorDetail"""
        return cls.create_error(cls.SERVICE_UNAVAILABLE, message, detail)
    
    @classmethod
    def validation_error(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建驗證錯誤的ErrorDetail"""
        return cls.create_error(cls.VALIDATION_ERROR, message, detail)
    
    @classmethod
    def parameter_missing(cls, parameter_name: str, detail: Optional[str] = None) -> ErrorDetail:
        """創建參數缺失錯誤的ErrorDetail"""
        return cls.create_error(
            cls.PARAMETER_MISSING,
            f"必需參數 '{parameter_name}' 缺失",
            detail
        )
    
    @classmethod
    def parameter_invalid(cls, parameter_name: str, detail: Optional[str] = None) -> ErrorDetail:
        """創建參數無效錯誤的ErrorDetail"""
        return cls.create_error(
            cls.PARAMETER_INVALID,
            f"參數 '{parameter_name}' 值無效",
            detail
        )
    
    @classmethod
    def model_error(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建模型錯誤的ErrorDetail"""
        return cls.create_error(cls.MODEL_ERROR, message, detail)
    
    @classmethod
    def model_not_found(cls, model_name: str, detail: Optional[str] = None) -> ErrorDetail:
        """創建模型未找到錯誤的ErrorDetail"""
        return cls.create_error(
            cls.MODEL_NOT_FOUND,
            f"模型 '{model_name}' 未找到",
            detail
        )
    
    @classmethod
    def external_service_error(cls, service_name: str, detail: Optional[str] = None) -> ErrorDetail:
        """創建外部服務錯誤的ErrorDetail"""
        return cls.create_error(
            cls.EXTERNAL_SERVICE_ERROR,
            f"外部服務 '{service_name}' 錯誤",
            detail
        )
    
    @classmethod
    def rate_limit_exceeded(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建速率限制錯誤的ErrorDetail"""
        return cls.create_error(cls.RATE_LIMIT_EXCEEDED, message, detail)
    
    @classmethod
    def resource_not_found(cls, resource_type: str, resource_id: str, detail: Optional[str] = None) -> ErrorDetail:
        """創建資源未找到錯誤的ErrorDetail"""
        return cls.create_error(
            cls.RESOURCE_NOT_FOUND,
            f"{resource_type} ID '{resource_id}' 未找到",
            detail
        )
    
    @classmethod
    def business_error(cls, message: Optional[str] = None, detail: Optional[str] = None) -> ErrorDetail:
        """創建業務邏輯錯誤的ErrorDetail"""
        return cls.create_error(cls.BUSINESS_ERROR, message, detail)


class ErrorCodeUtils:
    """
    錯誤代碼工具類，提供額外的便利方法
    """
    
    @staticmethod
    def is_success(code: int) -> bool:
        """檢查錯誤代碼是否表示成功"""
        return 200 <= code < 300
    
    @staticmethod
    def is_client_error(code: int) -> bool:
        """檢查錯誤代碼是否為客戶端錯誤"""
        return 400 <= code < 500
    
    @staticmethod
    def is_server_error(code: int) -> bool:
        """檢查錯誤代碼是否為伺服器錯誤"""
        return 500 <= code < 600
    
    @staticmethod
    def is_framework_error(code: int) -> bool:
        """檢查錯誤代碼是否為框架特定錯誤"""
        return 1000 <= code < 10000
    
    @staticmethod
    def get_error_category(code: int) -> str:
        """獲取錯誤代碼的分類"""
        if ErrorCodeUtils.is_success(code):
            return "成功"
        elif ErrorCodeUtils.is_client_error(code):
            return "客戶端錯誤"
        elif ErrorCodeUtils.is_server_error(code):
            return "伺服器錯誤"
        elif 1000 <= code < 2000:
            return "通用錯誤"
        elif 2000 <= code < 3000:
            return "驗證錯誤"
        elif 3000 <= code < 4000:
            return "認證授權錯誤"
        elif 4000 <= code < 5000:
            return "模型錯誤"
        elif 5000 <= code < 6000:
            return "外部服務錯誤"
        elif 6000 <= code < 7000:
            return "資源錯誤"
        elif 7000 <= code < 8000:
            return "網路錯誤"
        elif 8000 <= code < 9000:
            return "存儲錯誤"
        elif 9000 <= code < 10000:
            return "業務錯誤"
        else:
            return "未知錯誤"