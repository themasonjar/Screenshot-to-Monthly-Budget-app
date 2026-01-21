from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple

import os
from upstash_redis import Redis


def _utc_now_iso() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def _try_parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse expected transaction date formats.
    We primarily store/expect YYYY-MM-DD, but keep this tolerant.
    """
    date_str = (date_str or "").strip()
    for fmt in ("%Y-%m-%d", "%m/%d/%Y", "%m-%d-%Y", "%d/%m/%Y", "%d-%m-%Y"):
        try:
            return datetime.strptime(date_str, fmt).replace(tzinfo=timezone.utc)
        except ValueError:
            continue
    return None


def _month_key(dt: datetime) -> str:
    return dt.strftime("%m/%Y")


class Database:
    """
    Upstash Redis-backed persistence layer.

    NOTE: This replaces the previous SQLite implementation because Vercel’s filesystem is ephemeral.
    Required env vars (provided by the Upstash<>Vercel integration):
      - UPSTASH_REDIS_REST_URL
      - UPSTASH_REDIS_REST_TOKEN
    """

    def __init__(self, key_prefix: str = "budgetapp:"):
        url = os.getenv("UPSTASH_REDIS_REST_URL")
        token = os.getenv("UPSTASH_REDIS_REST_TOKEN")
        if not url or not token:
            raise RuntimeError(
                "Upstash Redis env vars are missing. Set UPSTASH_REDIS_REST_URL and "
                "UPSTASH_REDIS_REST_TOKEN (via Vercel Upstash integration or local .env)."
            )
        self.redis = Redis.from_env()
        self.key_prefix = key_prefix

    def _k(self, key: str) -> str:
        return f"{self.key_prefix}{key}"

    def _get_int(self, v) -> Optional[int]:
        if v is None:
            return None
        try:
            return int(v)
        except Exception:
            return None

    def _get_float(self, v) -> Optional[float]:
        if v is None:
            return None
        try:
            return float(v)
        except Exception:
            return None

    def _hgetall(self, key: str) -> Dict:
        data = self.redis.hgetall(key) or {}
        # upstash-redis may return dict[str, str] or dict[bytes, bytes] depending on config
        normalized: Dict[str, str] = {}
        for k, v in data.items():
            nk = k.decode() if isinstance(k, (bytes, bytearray)) else str(k)
            nv = v.decode() if isinstance(v, (bytes, bytearray)) else str(v)
            normalized[nk] = nv
        return normalized

    def _smembers(self, key: str) -> List[str]:
        members = self.redis.smembers(key) or []
        out: List[str] = []
        for m in members:
            out.append(m.decode() if isinstance(m, (bytes, bytearray)) else str(m))
        return out

    def _zrevrange(self, key: str, start: int, end: int) -> List[str]:
        members = self.redis.zrevrange(key, start, end) or []
        out: List[str] = []
        for m in members:
            out.append(m.decode() if isinstance(m, (bytes, bytearray)) else str(m))
        return out

    def _hset_mapping(self, key: str, mapping: Dict[str, str]) -> None:
        """
        Set multiple hash fields in a client-compatible way.

        Upstash's python SDK uses `values=` for multi-field HSET, not `mapping=`.
        Some environments/versions may only support the 3-arg form (key, field, value),
        so we fall back to per-field writes if needed.
        """
        try:
            # Upstash SDK signature: hset(key, values={...})
            self.redis.hset(key, values=mapping)
        except TypeError:
            # Fallback for older/alternate clients
            for field, value in mapping.items():
                self.redis.hset(key, field, value)

    # Project operations
    def create_project(self, name: str) -> int:
        """Create a new project"""
        project_id = int(self.redis.incr(self._k("project:next_id")))
        now = _utc_now_iso()
        self._hset_mapping(
            self._k(f"project:{project_id}"),
            {"id": str(project_id), "name": name, "created_at": now, "updated_at": now},
        )
        # Newest first: store created_at as sortable score (epoch seconds)
        score = int(datetime.now(timezone.utc).timestamp())
        self.redis.zadd(self._k("projects:by_created_at"), {str(project_id): score})
        return project_id

    def get_all_projects(self) -> List[Dict]:
        """Get all projects"""
        ids = self._zrevrange(self._k("projects:by_created_at"), 0, -1)
        projects: List[Dict] = []
        for pid in ids:
            p = self._hgetall(self._k(f"project:{pid}"))
            if p:
                p["id"] = self._get_int(p.get("id")) or self._get_int(pid) or pid
                projects.append(p)
        return projects

    def get_project(self, project_id: int) -> Optional[Dict]:
        """Get a specific project"""
        p = self._hgetall(self._k(f"project:{project_id}"))
        if not p:
            return None
        p["id"] = self._get_int(p.get("id")) or project_id
        return p

    def delete_project(self, project_id: int) -> bool:
        """Delete a project and all associated data"""
        project_key = self._k(f"project:{project_id}")
        if not self.redis.exists(project_key):
            return False

        # Delete categories
        cat_ids = self._smembers(self._k(f"project:{project_id}:categories"))
        for cid in cat_ids:
            self.delete_category(int(cid))

        # Delete transactions
        tx_ids = self._smembers(self._k(f"project:{project_id}:transactions:all"))
        for tid in tx_ids:
            self.delete_transaction(int(tid))

        # Delete project-level indexes
        self.redis.delete(self._k(f"project:{project_id}:categories"))
        self.redis.delete(self._k(f"project:{project_id}:categories:Income"))
        self.redis.delete(self._k(f"project:{project_id}:categories:Expenses"))
        self.redis.delete(self._k(f"project:{project_id}:categories:Savings"))
        self.redis.delete(self._k(f"project:{project_id}:transactions:all"))
        self.redis.delete(self._k(f"project:{project_id}:transactions:by_date"))
        # Month sets: best-effort cleanup (scan known months from tx hashes is expensive; rely on tx deletion cleanup)

        # Remove from global index and delete hash
        self.redis.zrem(self._k("projects:by_created_at"), str(project_id))
        self.redis.delete(project_key)
        return True

    # Category operations
    def add_category(self, project_id: int, name: str, category_type: str) -> int:
        """Add a category to a project"""
        category_id = int(self.redis.incr(self._k("category:next_id")))
        self._hset_mapping(
            self._k(f"category:{category_id}"),
            {
                "id": str(category_id),
                "project_id": str(project_id),
                "name": name,
                "type": category_type,
            },
        )
        self.redis.sadd(self._k(f"project:{project_id}:categories"), str(category_id))
        self.redis.sadd(self._k(f"project:{project_id}:categories:{category_type}"), str(category_id))
        return category_id

    def get_categories(self, project_id: int, category_type: Optional[str] = None) -> List[Dict]:
        """Get categories for a project"""
        if category_type:
            ids = self._smembers(self._k(f"project:{project_id}:categories:{category_type}"))
        else:
            ids = self._smembers(self._k(f"project:{project_id}:categories"))

        categories: List[Dict] = []
        for cid in ids:
            c = self._hgetall(self._k(f"category:{cid}"))
            if c:
                c["id"] = self._get_int(c.get("id")) or self._get_int(cid) or cid
                c["project_id"] = self._get_int(c.get("project_id")) or project_id
                categories.append(c)
        return categories

    def delete_category(self, category_id: int) -> bool:
        """Delete a category"""
        key = self._k(f"category:{category_id}")
        c = self._hgetall(key)
        if not c:
            return False
        project_id = self._get_int(c.get("project_id"))
        category_type = c.get("type")
        if project_id is not None:
            self.redis.srem(self._k(f"project:{project_id}:categories"), str(category_id))
            if category_type:
                self.redis.srem(self._k(f"project:{project_id}:categories:{category_type}"), str(category_id))
        self.redis.delete(key)
        return True

    # Transaction operations
    def add_transaction(self, project_id: int, date: str, trans_type: str,
                       category: str, amount: float, description: str = '') -> int:
        """Add a transaction"""
        transaction_id = int(self.redis.incr(self._k("transaction:next_id")))
        created_at = _utc_now_iso()

        dt = _try_parse_date(date) or datetime.now(timezone.utc)
        month = _month_key(dt)
        score = int(dt.timestamp())

        self._hset_mapping(
            self._k(f"transaction:{transaction_id}"),
            {
                "id": str(transaction_id),
                "project_id": str(project_id),
                "date": date,
                "type": trans_type,
                "category": category,
                "amount": str(float(amount)),
                "description": description or "",
                "created_at": created_at,
            },
        )

        self.redis.sadd(self._k(f"project:{project_id}:transactions:all"), str(transaction_id))
        self.redis.zadd(self._k(f"project:{project_id}:transactions:by_date"), {str(transaction_id): score})
        self.redis.sadd(self._k(f"project:{project_id}:transactions:month:{month}"), str(transaction_id))
        return transaction_id

    def add_transactions_batch(self, transactions: List[Dict]) -> List[int]:
        """Add multiple transactions at once"""
        transaction_ids: List[int] = []
        for trans in transactions:
            transaction_ids.append(
                self.add_transaction(
                    project_id=int(trans["project_id"]),
                    date=str(trans["date"]),
                    trans_type=str(trans["type"]),
                    category=str(trans["category"]),
                    amount=float(trans["amount"]),
                    description=str(trans.get("description", "") or ""),
                )
            )
        return transaction_ids

    def get_transactions(self, project_id: int, month: Optional[str] = None) -> List[Dict]:
        """Get transactions for a project, optionally filtered by month"""
        if month:
            ids = self._smembers(self._k(f"project:{project_id}:transactions:month:{month}"))
            txs: List[Tuple[int, Dict]] = []
            for tid in ids:
                t = self._hgetall(self._k(f"transaction:{tid}"))
                if not t:
                    continue
                dt = _try_parse_date(t.get("date", "")) or datetime.fromtimestamp(0, tz=timezone.utc)
                txs.append((int(dt.timestamp()), t))
            txs.sort(key=lambda x: x[0], reverse=True)
            transactions = [t for _, t in txs]
        else:
            ids = self._zrevrange(self._k(f"project:{project_id}:transactions:by_date"), 0, -1)
            transactions = []
            for tid in ids:
                t = self._hgetall(self._k(f"transaction:{tid}"))
                if t:
                    transactions.append(t)

        for t in transactions:
            t["id"] = self._get_int(t.get("id")) or t.get("id")
            t["project_id"] = self._get_int(t.get("project_id")) or project_id
            amt = self._get_float(t.get("amount"))
            if amt is not None:
                t["amount"] = amt
        return transactions

    def update_transaction(self, transaction_id: int, data: Dict) -> bool:
        """Update a transaction"""
        key = self._k(f"transaction:{transaction_id}")
        existing = self._hgetall(key)
        if not existing:
            return False

        project_id = self._get_int(existing.get("project_id"))
        if project_id is None:
            return False

        old_date = existing.get("date", "")
        old_dt = _try_parse_date(old_date) or datetime.fromtimestamp(0, tz=timezone.utc)
        old_month = _month_key(old_dt)

        updates: Dict[str, str] = {}
        for k in ("date", "type", "category", "amount", "description"):
            if k in data:
                if k == "amount":
                    updates[k] = str(float(data[k]))
                else:
                    updates[k] = str(data[k])

        if not updates:
            return False

        # If date changes, update indexes
        if "date" in updates:
            new_dt = _try_parse_date(updates["date"]) or datetime.now(timezone.utc)
            new_month = _month_key(new_dt)
            new_score = int(new_dt.timestamp())

            # zset score update
            self.redis.zadd(self._k(f"project:{project_id}:transactions:by_date"), {str(transaction_id): new_score})

            # month membership update
            self.redis.srem(self._k(f"project:{project_id}:transactions:month:{old_month}"), str(transaction_id))
            self.redis.sadd(self._k(f"project:{project_id}:transactions:month:{new_month}"), str(transaction_id))

        self._hset_mapping(key, updates)
        return True

    def delete_transaction(self, transaction_id: int) -> bool:
        """Delete a transaction"""
        key = self._k(f"transaction:{transaction_id}")
        t = self._hgetall(key)
        if not t:
            return False
        project_id = self._get_int(t.get("project_id"))
        if project_id is None:
            return False

        dt = _try_parse_date(t.get("date", "")) or datetime.fromtimestamp(0, tz=timezone.utc)
        month = _month_key(dt)

        self.redis.srem(self._k(f"project:{project_id}:transactions:all"), str(transaction_id))
        self.redis.zrem(self._k(f"project:{project_id}:transactions:by_date"), str(transaction_id))
        self.redis.srem(self._k(f"project:{project_id}:transactions:month:{month}"), str(transaction_id))
        self.redis.delete(key)
        return True

    def get_monthly_summary(self, project_id: int) -> Dict:
        """Get summary of all transactions grouped by month and type"""
        ids = self._smembers(self._k(f"project:{project_id}:transactions:all"))
        summary: Dict[str, Dict[str, float]] = {}
        for tid in ids:
            t = self._hgetall(self._k(f"transaction:{tid}"))
            if not t:
                continue
            dt = _try_parse_date(t.get("date", "")) or None
            if not dt:
                continue
            mkey = _month_key(dt)
            if mkey not in summary:
                summary[mkey] = {"Income": 0.0, "Expenses": 0.0, "Savings": 0.0}
            ttype = t.get("type", "")
            amt = self._get_float(t.get("amount")) or 0.0
            if ttype in summary[mkey]:
                summary[mkey][ttype] += amt
        return summary

    def get_category_breakdown(self, project_id: int, month: str, trans_type: str) -> Dict:
        """Get category breakdown for a specific month and type"""
        ids = self._smembers(self._k(f"project:{project_id}:transactions:month:{month}"))
        breakdown: Dict[str, float] = {}
        for tid in ids:
            t = self._hgetall(self._k(f"transaction:{tid}"))
            if not t:
                continue
            if t.get("type") != trans_type:
                continue
            cat = t.get("category") or "Uncategorized"
            amt = self._get_float(t.get("amount")) or 0.0
            breakdown[cat] = breakdown.get(cat, 0.0) + amt
        return breakdown
