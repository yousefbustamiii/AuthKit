"""
Bundles all middleware-related source files into a single reviewable TXT file.
Output: server/middleware_bundle.txt

Run from anywhere:
    python server/src/scripts/bundle_middleware.py
"""

import os

REPO_ROOT = "/Users/yousefbustami/Desktop/saas-authentication-paid"
SERVER_ROOT = os.path.join(REPO_ROOT, "server")
OUTPUT_PATH = os.path.join(SERVER_ROOT, "middleware_bundle.txt")

# ---------------------------------------------------------------------------
# Files are listed explicitly and in execution order so reviewers can follow
# the request path from entry to resolution.
# ---------------------------------------------------------------------------

SECTIONS = [
    (
        "ENTRY POINT — Middleware Chain",
        [
            "src/app/middleware/middleware_chain.py",
        ],
    ),
    (
        "PHASE 1 — Identity & Endpoint Configuration",
        [
            "src/app/middleware/phases/phase1/endpoint_matrix.py",
            "src/app/middleware/phases/phase1/plan_limits.py",
            "src/app/middleware/phases/phase1/request_context.py",
            "src/app/middleware/phases/phase1/execute.py",
            "src/app/middleware/phases/phase1/extract_identity.py",
            "src/app/middleware/phases/phase1/helpers/classify_ip_type.py",
            "src/app/middleware/phases/phase1/helpers/extract_country.py",
            "src/app/middleware/phases/phase1/helpers/extract_device.py",
        ],
    ),
    (
        "PHASE 2 — Authentication: Session Token",
        [
            "src/app/middleware/phases/phase2/execute.py",
        ],
    ),
    (
        "PHASE 2 — Authentication: API Key",
        [
            "src/app/middleware/phases/phase2/execute_api_key.py",
        ],
    ),
    (
        "PHASE 3 — Idempotency",
        [
            "src/app/middleware/phases/phase3/execute.py",
        ],
    ),
    (
        "SECURITY — Rate Limiting & Web Headers",
        [
            "src/app/middleware/security/execute.py",
            "src/app/middleware/security/rate_limiting/check_rate_limit.py",
            "src/app/middleware/security/web/cors_handler.py",
            "src/app/middleware/security/web/csp_handler.py",
            "src/app/middleware/security/web/response_headers.py",
        ],
    ),
    (
        "STORE — Session Resolution (L1 Memory → L2 Redis → L3 Postgres)",
        [
            "src/store/sql/authentication/sessions/shared/resolve_session_by_token_hash.py",
        ],
    ),
    (
        "STORE — API Key Resolution (L1 Memory → L2 Redis → L3 Postgres)",
        [
            "src/store/sql/core/api_keys/shared/resolve_api_key_by_hash.py",
        ],
    ),
    (
        "STORE — Rate Limit Memory Cache (L1)",
        [
            "src/store/cache/authentication/memory/rate_limit_memory_cache.py",
        ],
    ),
    (
        "LUA SCRIPTS — Atomic Redis Operations",
        [
            "src/store/cache/lua/shared/token_bucket.lua",
            "src/store/cache/lua/idempotency.lua",
        ],
    ),
    (
        "CONFIG — Lua Script Manager",
        [
            "src/app/config/lua_manager.py",
        ],
    ),
]


def write_section_header(f, title):
    border = "#" * 80
    f.write(f"\n{border}\n")
    f.write(f"# {title}\n")
    f.write(f"{border}\n\n")


def write_file_block(f, abs_path, rel_label):
    f.write("=" * 80 + "\n")
    f.write(f"FILE: {rel_label}\n")
    f.write("=" * 80 + "\n\n")
    try:
        with open(abs_path, "r", encoding="utf-8", errors="replace") as src:
            f.write(src.read())
    except Exception as e:
        f.write(f"[ERROR READING FILE: {e}]")
    f.write("\n\n")


def main():
    total_files = sum(len(files) for _, files in SECTIONS)
    print(f"Bundling {total_files} middleware files...")

    with open(OUTPUT_PATH, "w", encoding="utf-8") as f:
        f.write("=" * 80 + "\n")
        f.write("MIDDLEWARE BUNDLE\n")
        f.write("saas-authentication-paid — server/src\n")
        f.write("=" * 80 + "\n")
        f.write(
            "\nThis file contains every file that participates in the middleware pipeline,\n"
            "ordered by execution phase. Use it for code review or AI analysis.\n\n"
            "REQUEST FLOW:\n"
            "  middleware_chain.py\n"
            "    → Phase 1  (identity, endpoint config, token extraction)\n"
            "    → Phase 2  (session auth OR api key auth)\n"
            "    → Rate Limiting  (IP / user / api key)\n"
            "    → Phase 3  (idempotency)\n\n"
        )

        for section_title, relative_paths in SECTIONS:
            write_section_header(f, section_title)
            for rel_path in relative_paths:
                abs_path = os.path.join(SERVER_ROOT, rel_path)
                if not os.path.exists(abs_path):
                    f.write(f"[FILE NOT FOUND: {rel_path}]\n\n")
                    print(f"  WARNING: not found — {rel_path}")
                    continue
                write_file_block(f, abs_path, rel_path)
                print(f"  + {rel_path}")

    print(f"\nDone. Output: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
