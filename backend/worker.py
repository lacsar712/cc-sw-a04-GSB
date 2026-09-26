import os
import time
from datetime import datetime, timezone

import psycopg
from psycopg.rows import dict_row

from domain import judge

DSN = os.environ.get("DATABASE_URL", "postgresql://app:app@localhost:54395/spectrum")


def connect():
    return psycopg.connect(DSN, row_factory=dict_row)


def claim_one(conn):
    # 领取侧：先清空急测待处理，再碰普通；同档编号升序
    row = conn.execute(
        """
        SELECT id, nominal_nm, measured_nm, urgent FROM jobs
        WHERE status='pending'
        ORDER BY CASE WHEN urgent THEN 0 ELSE 1 END, id
        FOR UPDATE SKIP LOCKED
        LIMIT 1
        """
    ).fetchone()
    if not row:
        return None
    verdict, reason = judge(row["nominal_nm"], row["measured_nm"])
    conn.execute(
        "UPDATE jobs SET status='done', verdict=%s, reason=%s WHERE id=%s",
        (verdict, reason, row["id"]),
    )
    conn.commit()
    lane = "急测" if row["urgent"] else "普通"
    print(f"claimed job {row['id']} via {lane} lane -> {verdict}", flush=True)
    return row["id"]


def main():
    while True:
        try:
            with connect() as conn:
                claim_one(conn)
        except Exception as exc:
            print("worker err", exc, flush=True)
        time.sleep(0.4)


if __name__ == "__main__":
    main()
