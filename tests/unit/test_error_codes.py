"""
ErrorCodes 類別使用示例和測試

展示如何使用新的ErrorCodes工具類別來處理各種錯誤情況。
"""

import pytest
from llmbrick.core.error_codes import ErrorCodes, ErrorCodeUtils
from llmbrick.protocols.models.bricks.common_types import ErrorDetail, CommonResponse


class TestErrorCodes:
    """ErrorCodes 基本功能測試"""
    
    def test_create_basic_errors(self):
        """測試基本錯誤創建"""
        # 使用工廠方法創建常見錯誤
        bad_request = ErrorCodes.bad_request("無效的請求參數", "缺少必需字段 'name'")
        assert bad_request.code == 400
        assert bad_request.message == "無效的請求參數"
        assert bad_request.detail == "缺少必需字段 'name'"
        
        not_found = ErrorCodes.not_found()
        assert not_found.code == 404
        assert not_found.message == "未找到"
        
        internal_error = ErrorCodes.internal_error("伺服器內部錯誤")
        assert internal_error.code == 500
        assert internal_error.message == "伺服器內部錯誤"
    
    def test_create_custom_errors(self):
        """測試自定義錯誤創建"""
        # 使用通用創建方法
        custom_error = ErrorCodes.create_error(
            ErrorCodes.MODEL_NOT_FOUND,
            "指定的模型不存在",
            "模型 'gpt-4' 在當前環境中不可用"
        )
        assert custom_error.code == 4001
        assert custom_error.message == "指定的模型不存在"
        assert custom_error.detail == "模型 'gpt-4' 在當前環境中不可用"
    
    def test_default_messages(self):
        """測試默認錯誤訊息"""
        # 不提供訊息時使用默認訊息
        validation_error = ErrorCodes.create_error(ErrorCodes.VALIDATION_ERROR)
        assert validation_error.code == 2000
        assert validation_error.message == "驗證錯誤"
        
        # 測試未知錯誤代碼
        unknown_error = ErrorCodes.create_error(99999)
        assert unknown_error.message == "未知錯誤 (99999)"
    
    def test_specialized_factory_methods(self):
        """測試特化的工廠方法"""
        # 參數相關錯誤
        missing_param = ErrorCodes.parameter_missing("user_id", "請求中必須包含用戶ID")
        assert missing_param.code == 2002
        assert "user_id" in missing_param.message
        
        invalid_param = ErrorCodes.parameter_invalid("age", "年齡必須是正整數")
        assert invalid_param.code == 2003
        assert "age" in invalid_param.message
        
        # 模型相關錯誤
        model_not_found = ErrorCodes.model_not_found("gpt-4", "模型服務暫時不可用")
        assert model_not_found.code == 4001
        assert "gpt-4" in model_not_found.message
        
        # 資源相關錯誤
        resource_not_found = ErrorCodes.resource_not_found("用戶", "12345")
        assert resource_not_found.code == 6001
        assert "用戶" in resource_not_found.message
        assert "12345" in resource_not_found.message
        
        # 外部服務錯誤
        external_error = ErrorCodes.external_service_error("OpenAI API", "API金鑰無效")
        assert external_error.code == 5000
        assert "OpenAI API" in external_error.message


class TestErrorCodeUtils:
    """ErrorCodeUtils 工具類測試"""
    
    def test_error_category_detection(self):
        """測試錯誤分類判斷"""
        # 成功狀態
        assert ErrorCodeUtils.is_success(200) == True
        assert ErrorCodeUtils.is_success(201) == True
        assert ErrorCodeUtils.is_success(404) == False
        
        # 客戶端錯誤
        assert ErrorCodeUtils.is_client_error(400) == True
        assert ErrorCodeUtils.is_client_error(404) == True
        assert ErrorCodeUtils.is_client_error(500) == False
        
        # 伺服器錯誤
        assert ErrorCodeUtils.is_server_error(500) == True
        assert ErrorCodeUtils.is_server_error(503) == True
        assert ErrorCodeUtils.is_server_error(400) == False
        
        # 框架錯誤
        assert ErrorCodeUtils.is_framework_error(1000) == True
        assert ErrorCodeUtils.is_framework_error(2001) == True
        assert ErrorCodeUtils.is_framework_error(400) == False
    
    def test_error_categorization(self):
        """測試錯誤分類獲取"""
        assert ErrorCodeUtils.get_error_category(200) == "成功"
        assert ErrorCodeUtils.get_error_category(400) == "客戶端錯誤"
        assert ErrorCodeUtils.get_error_category(500) == "伺服器錯誤"
        assert ErrorCodeUtils.get_error_category(1000) == "通用錯誤"
        assert ErrorCodeUtils.get_error_category(2000) == "驗證錯誤"
        assert ErrorCodeUtils.get_error_category(3000) == "認證授權錯誤"
        assert ErrorCodeUtils.get_error_category(4000) == "模型錯誤"
        assert ErrorCodeUtils.get_error_category(5000) == "外部服務錯誤"
        assert ErrorCodeUtils.get_error_category(99999) == "未知錯誤"


class TestErrorCodesIntegration:
    """ErrorCodes 與 CommonResponse 整合測試"""
    
    def test_success_response(self):
        """測試成功響應"""
        response = CommonResponse(
            data={"result": "操作成功"},
            error=None
        )
        assert response.error is None
        assert response.data["result"] == "操作成功"
    
    def test_error_response(self):
        """測試錯誤響應"""
        error = ErrorCodes.validation_error("數據驗證失敗", "缺少必需字段")
        response = CommonResponse(
            data={},
            error=error
        )
        assert response.error is not None
        assert response.error.code == 2000
        assert "驗證失敗" in response.error.message
    
    def test_error_response_serialization(self):
        """測試錯誤響應序列化"""
        error = ErrorCodes.model_not_found("gpt-4", "模型不可用")
        response = CommonResponse(data={}, error=error)
        
        # 轉換為字典
        response_dict = response.to_dict()
        assert "error" in response_dict
        assert response_dict["error"]["code"] == 4001
        assert "gpt-4" in response_dict["error"]["message"]
        
        # 從字典重構
        reconstructed = CommonResponse.from_dict(response_dict)
        assert reconstructed.error.code == 4001
        assert reconstructed.error.message == error.message


class TestRealWorldScenarios:
    """真實場景使用示例"""
    
    def test_api_validation_scenario(self):
        """API參數驗證場景"""
        def validate_user_request(request_data):
            """模擬用戶請求驗證"""
            if not request_data.get("name"):
                return ErrorCodes.parameter_missing("name", "用戶名稱不能為空")
            
            if not isinstance(request_data.get("age"), int) or request_data.get("age") < 0:
                return ErrorCodes.parameter_invalid("age", "年齡必須是非負整數")
            
            return None
        
        # 測試缺少參數
        error = validate_user_request({"age": 25})
        assert error is not None
        assert error.code == ErrorCodes.PARAMETER_MISSING
        assert "name" in error.message
        
        # 測試無效參數
        error = validate_user_request({"name": "張三", "age": -5})
        assert error is not None
        assert error.code == ErrorCodes.PARAMETER_INVALID
        assert "age" in error.message
        
        # 測試有效請求
        error = validate_user_request({"name": "張三", "age": 25})
        assert error is None
    
    def test_model_service_scenario(self):
        """模型服務場景"""
        def call_model_service(model_name, input_data):
            """模擬模型服務調用"""
            available_models = ["gpt-3.5-turbo", "gpt-4"]
            
            if model_name not in available_models:
                return None, ErrorCodes.model_not_found(
                    model_name, 
                    f"支援的模型: {', '.join(available_models)}"
                )
            
            if not input_data:
                return None, ErrorCodes.validation_error(
                    "輸入數據不能為空",
                    "請提供有效的輸入文本"
                )
            
            # 模擬成功處理
            return {"result": f"使用 {model_name} 處理: {input_data}"}, None
        
        # 測試模型不存在
        result, error = call_model_service("invalid-model", "測試輸入")
        assert result is None
        assert error.code == ErrorCodes.MODEL_NOT_FOUND
        assert "invalid-model" in error.message
        
        # 測試空輸入
        result, error = call_model_service("gpt-4", "")
        assert result is None
        assert error.code == ErrorCodes.VALIDATION_ERROR
        
        # 測試成功調用
        result, error = call_model_service("gpt-4", "測試輸入")
        assert result is not None
        assert error is None
        assert "gpt-4" in result["result"]
    
    def test_external_service_scenario(self):
        """外部服務調用場景"""
        def call_external_api(service_name, timeout=30):
            """模擬外部API調用"""
            import random
            
            # 模擬不同的錯誤情況
            scenario = random.choice(["success", "timeout", "rate_limit", "service_error"])
            
            if scenario == "timeout":
                return None, ErrorCodes.create_error(
                    ErrorCodes.EXTERNAL_SERVICE_TIMEOUT,
                    f"{service_name} 服務響應超時",
                    f"超時時間: {timeout}秒"
                )
            elif scenario == "rate_limit":
                return None, ErrorCodes.rate_limit_exceeded(
                    "API調用頻率超限",
                    "請稍後重試"
                )
            elif scenario == "service_error":
                return None, ErrorCodes.external_service_error(
                    service_name,
                    "服務暫時不可用"
                )
            else:
                return {"status": "success", "data": "API調用成功"}, None
        
        # 設定固定隨機種子以確保測試結果可預測
        import random
        random.seed(42)
        
        # 測試多次調用以覆蓋不同場景
        for _ in range(10):
            result, error = call_external_api("TestAPI")
            if error:
                # 驗證錯誤類型
                assert error.code in [
                    ErrorCodes.EXTERNAL_SERVICE_TIMEOUT,
                    ErrorCodes.RATE_LIMIT_EXCEEDED,
                    ErrorCodes.EXTERNAL_SERVICE_ERROR
                ]
                assert ErrorCodeUtils.get_error_category(error.code) in [
                    "外部服務錯誤", "網路錯誤"
                ]


if __name__ == "__main__":
    # 運行基本示例
    print("=== ErrorCodes 使用示例 ===")
    
    # 創建各種錯誤
    errors = [
        ErrorCodes.bad_request("請求參數錯誤"),
        ErrorCodes.not_found("資源未找到"),
        ErrorCodes.model_not_found("gpt-4"),
        ErrorCodes.parameter_missing("user_id"),
        ErrorCodes.validation_error("數據格式錯誤"),
    ]
    
    for error in errors:
        category = ErrorCodeUtils.get_error_category(error.code)
        print(f"[{error.code}] {error.message} - 分類: {category}")
    
    print("\n=== 整合 CommonResponse 示例 ===")
    
    # 成功響應
    success_response = CommonResponse(data={"message": "操作成功"})
    print(f"成功響應: {success_response.to_dict()}")
    
    # 錯誤響應
    error_response = CommonResponse(
        data={},
        error=ErrorCodes.internal_error("系統暫時不可用")
    )
    print(f"錯誤響應: {error_response.to_dict()}")