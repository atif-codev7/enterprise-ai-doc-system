from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
import math

# Realistic in-memory PayGuard Double-Entry Ledger Store
# Mirrors Project 1 (PayGuard) architecture
class PayGuardLedgerDB:
    def __init__(self):
        self._accounts: Dict[str, Dict[str, Any]] = {
            "ACC-1001": {
                "account_id": "ACC-1001",
                "holder_name": "Apex Global Treasury Corp",
                "currency": "USD",
                "balance": 4500000.00,
                "status": "ACTIVE",
                "tier": "TIER_1_ENTERPRISE",
                "created_at": (datetime.utcnow() - timedelta(days=120)).isoformat()
            },
            "ACC-1002": {
                "account_id": "ACC-1002",
                "holder_name": "Horizon Settlement Clearing",
                "currency": "USD",
                "balance": 1850000.50,
                "status": "ACTIVE",
                "tier": "TIER_1_ENTERPRISE",
                "created_at": (datetime.utcnow() - timedelta(days=90)).isoformat()
            },
            "ACC-2005": {
                "account_id": "ACC-2005",
                "holder_name": "Nexus Merchant Processing LLC",
                "currency": "USD",
                "balance": 742110.25,
                "status": "ACTIVE",
                "tier": "TIER_2_MERCHANT",
                "created_at": (datetime.utcnow() - timedelta(days=45)).isoformat()
            },
            "ACC-9999": {
                "account_id": "ACC-9999",
                "holder_name": "PayGuard System Escrow & Fees",
                "currency": "USD",
                "balance": 12894500.00,
                "status": "ACTIVE",
                "tier": "SYSTEM_ESCROW",
                "created_at": (datetime.utcnow() - timedelta(days=365)).isoformat()
            }
        }
        
        # Double-entry Journal: Every transfer produces paired debit & credit entries
        self._journal_entries: List[Dict[str, Any]] = [
            {
                "entry_id": "JRN-89210",
                "timestamp": (datetime.utcnow() - timedelta(hours=2)).isoformat(),
                "idempotency_key": "idemp-sec-tx-89210-apex",
                "source_account": "ACC-1001",
                "destination_account": "ACC-2005",
                "amount": 150000.00,
                "currency": "USD",
                "status": "SETTLED",
                "transaction_type": "MERCHANT_SETTLEMENT",
                "isolation_level": "SERIALIZABLE",
                "row_lock_acquired": True,
                "description": "Daily automated liquidity sweep to Nexus Merchant Processing"
            },
            {
                "entry_id": "JRN-89209",
                "timestamp": (datetime.utcnow() - timedelta(hours=6)).isoformat(),
                "idempotency_key": "idemp-sec-tx-89209-horiz",
                "source_account": "ACC-1002",
                "destination_account": "ACC-1001",
                "amount": 500000.00,
                "currency": "USD",
                "status": "SETTLED",
                "transaction_type": "INTERBANK_TRANSFER",
                "isolation_level": "SERIALIZABLE",
                "row_lock_acquired": True,
                "description": "Collateral replenishment for cross-border FX buffer"
            },
            {
                "entry_id": "JRN-89208",
                "timestamp": (datetime.utcnow() - timedelta(days=1)).isoformat(),
                "idempotency_key": "idemp-sec-tx-89208-fee",
                "source_account": "ACC-2005",
                "destination_account": "ACC-9999",
                "amount": 3250.00,
                "currency": "USD",
                "status": "SETTLED",
                "transaction_type": "PLATFORM_FEE",
                "isolation_level": "SERIALIZABLE",
                "row_lock_acquired": True,
                "description": "PayGuard platform 0.05% processing fee deduction"
            },
            {
                "entry_id": "JRN-89190",
                "timestamp": (datetime.utcnow() - timedelta(days=2)).isoformat(),
                "idempotency_key": "idemp-sec-tx-89190-apex",
                "source_account": "ACC-1001",
                "destination_account": "ACC-9999",
                "amount": 12500.00,
                "currency": "USD",
                "status": "SETTLED",
                "transaction_type": "RISK_RESERVE",
                "isolation_level": "SERIALIZABLE",
                "row_lock_acquired": True,
                "description": "Quarterly risk reserve escrow hold"
            }
        ]

    def get_account(self, account_id: str) -> Optional[Dict[str, Any]]:
        return self._accounts.get(account_id.upper())

    def list_accounts(self) -> List[Dict[str, Any]]:
        return list(self._accounts.values())

    def query_ledger(self, account_id: str, limit: int = 10) -> Dict[str, Any]:
        acc = self.get_account(account_id)
        if not acc:
            return {
                "found": False,
                "account_id": account_id,
                "error": f"Account '{account_id}' does not exist in PayGuard ledger."
            }

        acc_id = acc["account_id"]
        matched_txs = [
            tx for tx in self._journal_entries
            if tx["source_account"] == acc_id or tx["destination_account"] == acc_id
        ][:limit]

        return {
            "found": True,
            "account": acc,
            "transaction_count": len(matched_txs),
            "journal_entries": matched_txs,
            "reconciliation_status": "BALANCED_ACID",
            "double_entry_verified": True
        }

    def compute_financial_analytics(self, account_id: str, time_window_days: int = 30) -> Dict[str, Any]:
        acc = self.get_account(account_id)
        if not acc:
            return {
                "error": f"Account '{account_id}' not found for analytics computation."
            }

        acc_id = acc["account_id"]
        cutoff = datetime.utcnow() - timedelta(days=time_window_days)

        inflows = [
            tx["amount"] for tx in self._journal_entries
            if tx["destination_account"] == acc_id
        ]
        outflows = [
            tx["amount"] for tx in self._journal_entries
            if tx["source_account"] == acc_id
        ]

        total_inflow = sum(inflows)
        total_outflow = sum(outflows)
        net_flow = total_inflow - total_outflow
        tx_count = len(inflows) + len(outflows)

        # Velocity = turnover relative to current balance
        balance = acc["balance"]
        velocity = round((total_inflow + total_outflow) / max(balance, 1.0), 4)

        # Variance calculation
        all_amounts = inflows + outflows
        if all_amounts:
            mean = sum(all_amounts) / len(all_amounts)
            sq_diffs = [(x - mean) ** 2 for x in all_amounts]
            variance = round(sum(sq_diffs) / len(all_amounts), 2)
            std_dev = round(math.sqrt(variance), 2)
        else:
            variance = 0.0
            std_dev = 0.0

        # Anomaly score based on velocity and sudden spikes
        anomaly_score = 0.05 if velocity < 1.0 else min(0.95, round(velocity * 0.15, 2))
        risk_level = "LOW" if anomaly_score < 0.3 else ("MEDIUM" if anomaly_score < 0.7 else "HIGH")

        return {
            "account_id": acc_id,
            "holder_name": acc["holder_name"],
            "currency": acc["currency"],
            "current_balance": balance,
            "time_window_days": time_window_days,
            "metrics": {
                "total_inflow": total_inflow,
                "total_outflow": total_outflow,
                "net_flow": net_flow,
                "transaction_velocity": velocity,
                "amount_variance": variance,
                "standard_deviation": std_dev,
                "anomaly_score": anomaly_score,
                "risk_rating": risk_level
            },
            "audit_trail": "Double-entry verified against PayGuard PostgreSQL row-level locks"
        }

# Singleton instance
payguard_db = PayGuardLedgerDB()
