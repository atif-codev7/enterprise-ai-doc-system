import pytest
from app.workflows.tools import execute_payguard_ledger_tool, execute_financial_analytics_tool

def test_execute_payguard_ledger_tool_success():
    args = {"account_id": "ACC-1001", "limit": 5}
    result, trace = execute_payguard_ledger_tool(args)

    assert trace.status == "success"
    assert trace.tool_name == "query_payguard_ledger"
    assert result["found"] is True
    assert result["account"]["account_id"] == "ACC-1001"
    assert result["reconciliation_status"] == "BALANCED_ACID"
    assert len(result["journal_entries"]) > 0

def test_execute_payguard_ledger_tool_nonexistent():
    args = {"account_id": "ACC-999999", "limit": 5}
    result, trace = execute_payguard_ledger_tool(args)

    assert trace.status == "success"
    assert result["found"] is False
    assert "does not exist" in result["error"]

def test_execute_financial_analytics_tool():
    args = {"account_id": "ACC-2005", "time_window_days": 30}
    result, trace = execute_financial_analytics_tool(args)

    assert trace.status == "success"
    assert trace.tool_name == "run_financial_analytics"
    assert "metrics" in result
    m = result["metrics"]
    assert "transaction_velocity" in m
    assert "amount_variance" in m
    assert "anomaly_score" in m
    assert m["risk_rating"] in ["LOW", "MEDIUM", "HIGH"]
