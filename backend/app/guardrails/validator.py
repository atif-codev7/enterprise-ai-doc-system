from typing import Any, Dict, Tuple
from pydantic import ValidationError
from app.models.schemas import PayGuardLedgerQuery, FinancialAnalyticsQuery

class ToolCallValidator:
    """
    Enforces strict Pydantic parameter schemas on all agent tool invocations,
    preventing hallucinated tool arguments, parameter smuggling, and type corruption.
    """

    SUPPORTED_TOOLS = {
        "query_payguard_ledger": PayGuardLedgerQuery,
        "run_financial_analytics": FinancialAnalyticsQuery
    }

    @classmethod
    def validate_tool_call(cls, tool_name: str, arguments: Dict[str, Any]) -> Tuple[bool, Any, str]:
        """
        Validates arguments against the target tool schema.
        Returns (is_valid, validated_model_or_none, error_message).
        """
        if tool_name not in cls.SUPPORTED_TOOLS:
            return (
                False,
                None,
                f"Unauthorized tool invocation: '{tool_name}' is not in allowed tool catalog."
            )

        model_cls = cls.SUPPORTED_TOOLS[tool_name]
        try:
            validated = model_cls(**arguments)
            return True, validated, ""
        except ValidationError as e:
            return False, None, f"Schema validation error for '{tool_name}': {e.errors()}"
        except Exception as ex:
            return False, None, f"Malformed arguments for '{tool_name}': {str(ex)}"

tool_validator = ToolCallValidator()
