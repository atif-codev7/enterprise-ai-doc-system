import time
from typing import Dict, Any, Tuple
from app.guardrails.validator import tool_validator
from app.payguard_mock.ledger_db import payguard_db
from app.models.schemas import ToolExecutionTrace

def execute_payguard_ledger_tool(arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], ToolExecutionTrace]:
    """
    Executes PayGuard Ledger inquiry with Pydantic validation.
    """
    t_start = time.perf_counter()
    is_valid, validated_model, err_msg = tool_validator.validate_tool_call("query_payguard_ledger", arguments)
    
    if not is_valid:
        duration_ms = (time.perf_counter() - t_start) * 1000.0
        trace = ToolExecutionTrace(
            tool_name="query_payguard_ledger",
            input_parameters=arguments,
            output_result={"error": err_msg},
            execution_time_ms=round(duration_ms, 2),
            status="validation_error"
        )
        return {"error": err_msg}, trace

    result = payguard_db.query_ledger(
        account_id=validated_model.account_id,
        limit=validated_model.limit
    )
    duration_ms = (time.perf_counter() - t_start) * 1000.0

    trace = ToolExecutionTrace(
        tool_name="query_payguard_ledger",
        input_parameters=validated_model.model_dump(),
        output_result=result,
        execution_time_ms=round(duration_ms, 2),
        status="success"
    )
    return result, trace

def execute_financial_analytics_tool(arguments: Dict[str, Any]) -> Tuple[Dict[str, Any], ToolExecutionTrace]:
    """
    Executes PayGuard Financial Analytics calculation with Pydantic validation.
    """
    t_start = time.perf_counter()
    is_valid, validated_model, err_msg = tool_validator.validate_tool_call("run_financial_analytics", arguments)

    if not is_valid:
        duration_ms = (time.perf_counter() - t_start) * 1000.0
        trace = ToolExecutionTrace(
            tool_name="run_financial_analytics",
            input_parameters=arguments,
            output_result={"error": err_msg},
            execution_time_ms=round(duration_ms, 2),
            status="validation_error"
        )
        return {"error": err_msg}, trace

    result = payguard_db.compute_financial_analytics(
        account_id=validated_model.account_id,
        time_window_days=validated_model.time_window_days
    )
    duration_ms = (time.perf_counter() - t_start) * 1000.0

    trace = ToolExecutionTrace(
        tool_name="run_financial_analytics",
        input_parameters=validated_model.model_dump(),
        output_result=result,
        execution_time_ms=round(duration_ms, 2),
        status="success"
    )
    return result, trace
