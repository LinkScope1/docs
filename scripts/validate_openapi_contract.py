"""Validate the V1.3.2 OpenAPI contract and its review mirrors."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import yaml


ROOT = Path(__file__).resolve().parents[1]
OPENAPI = ROOT / "03-api" / "openapi.yaml"
MODULE_DIR = ROOT / "03-api" / "modules"
PERMISSION_MAPPING = ROOT / "03-api" / "permission-api-mapping.md"

HTTP_METHODS = {"get", "post", "put", "patch", "delete", "options", "head", "trace"}
REQUIRED_EXTENSIONS = (
    "x-owner",
    "x-permission",
    "x-data-scope",
    "x-idempotency",
    "x-audit",
    "x-status",
)
ALLOWED_SCOPES = {
    "GLOBAL",
    "ORG_SUBTREE",
    "ORG_SELF",
    "EMPLOYEE_SELF",
    "ASSET_SCOPE",
    "SOURCE_AND_TARGET_ORG",
    "SYSTEM",
}
ALLOWED_STATUSES = {"planned", "reviewed", "implemented", "deprecated"}
MODULE_FILES = {
    "m1-auth-audit.yaml",
    "m2-organizations.yaml",
    "m2-employees.yaml",
    "m3-assets.yaml",
    "m3-payloads.yaml",
    "m4-assignments.yaml",
    "m5-access-events.yaml",
}


class UniqueKeyLoader(yaml.SafeLoader):
    """SafeLoader variant that rejects duplicate YAML keys."""


def construct_unique_mapping(loader: UniqueKeyLoader, node: yaml.MappingNode, deep: bool = False) -> dict[str, Any]:
    mapping: dict[str, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        if key in mapping:
            raise ValueError(f"duplicate YAML key: {key}")
        mapping[key] = loader.construct_object(value_node, deep=deep)
    return mapping


UniqueKeyLoader.add_constructor(
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG,
    construct_unique_mapping,
)


def load_yaml(path: Path) -> dict[str, Any]:
    try:
        value = yaml.load(path.read_text(encoding="utf-8"), Loader=UniqueKeyLoader)
    except (OSError, yaml.YAMLError, ValueError) as exc:
        raise ValueError(f"{path.relative_to(ROOT)}: invalid YAML: {exc}") from exc
    if not isinstance(value, dict):
        raise ValueError(f"{path.relative_to(ROOT)}: root must be a mapping")
    return value


def operations(document: dict[str, Any]) -> list[tuple[str, str, dict[str, Any]]]:
    result: list[tuple[str, str, dict[str, Any]]] = []
    for path, path_item in document.get("paths", {}).items():
        if not isinstance(path_item, dict):
            continue
        for method, operation in path_item.items():
            if method in HTTP_METHODS and isinstance(operation, dict):
                result.append((path, method, operation))
    return result


def resolve_local_ref(document: dict[str, Any], reference: Any) -> Any:
    if not isinstance(reference, dict) or "$ref" not in reference:
        return reference
    ref = reference["$ref"]
    if not isinstance(ref, str) or not ref.startswith("#/"):
        return reference
    value: Any = document
    for part in ref[2:].split("/"):
        if not isinstance(value, dict) or part not in value:
            return None
        value = value[part]
    return value


def parse_mapping_rows() -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for line in PERMISSION_MAPPING.read_text(encoding="utf-8").splitlines():
        if not line.startswith("|") or line.startswith("|---") or line.startswith("| 权限编码"):
            continue
        cells = [cell.strip().strip("`") for cell in line.strip().strip("|").split("|")]
        if len(cells) != 5:
            continue
        methods = {token for token in re.findall(r"GET|POST|PATCH|PUT|DELETE", cells[1])}
        paths = [token.strip().strip("`") for token in re.split(r"、|，|,", cells[2])]
        scopes = set(re.findall(r"GLOBAL|ORG_SUBTREE|ORG_SELF|EMPLOYEE_SELF|ASSET_SCOPE|SOURCE_AND_TARGET_ORG|SYSTEM", cells[3]))
        rows.append(
            {
                "permission": cells[0],
                "methods": methods,
                "paths": paths,
                "scopes": scopes,
                "audit": cells[4] == "是",
            }
        )
    return rows


def mapping_match(pattern: str, path: str) -> bool:
    if pattern == path:
        return True
    if pattern.endswith("/**"):
        base = pattern[:-3]
        return path == base or path.startswith(base + "/")
    return False


def check_permission_mapping(document: dict[str, Any], errors: list[str]) -> None:
    rows = parse_mapping_rows()
    if not rows:
        errors.append("permission-api-mapping.md: no mapping rows found")
        return
    for path, method, operation in operations(document):
        permission = operation.get("x-permission")
        full_path = "/api/v1" + path
        candidates = [
            row
            for row in rows
            if method.upper() in row["methods"] and any(mapping_match(pattern, full_path) for pattern in row["paths"])
        ]
        if permission == "system_webhook":
            if operation.get("x-data-scope") != "SYSTEM" or operation.get("x-audit") is not True:
                errors.append(f"{method.upper()} {path}: system webhook scope/audit mismatch")
            continue
        if not candidates:
            errors.append(f"{method.upper()} {path}: missing permission-api-mapping row")
            continue
        candidates.sort(key=lambda row: max((len(pattern) for pattern in row["paths"]), default=0), reverse=True)
        row = candidates[0]
        if permission != row["permission"]:
            errors.append(f"{method.upper()} {path}: permission {permission!r} != {row['permission']!r}")
        if operation.get("x-data-scope") not in row["scopes"]:
            errors.append(f"{method.upper()} {path}: data scope is not allowed by permission mapping")
        if operation.get("x-audit") != row["audit"]:
            errors.append(f"{method.upper()} {path}: audit flag differs from permission mapping")


def check_modules(document: dict[str, Any], errors: list[str]) -> None:
    files = {path.name for path in MODULE_DIR.glob("*.yaml")}
    if files != MODULE_FILES:
        errors.append(f"modules: expected {sorted(MODULE_FILES)}, found {sorted(files)}")
    main_by_key = {(path, method): operation for path, method, operation in operations(document)}
    mirror_count = 0
    for filename in sorted(MODULE_FILES):
        path = MODULE_DIR / filename
        module = load_yaml(path)
        for key, path_item in module.items():
            if key.startswith("x-"):
                continue
            if not isinstance(path_item, dict) or not isinstance(path_item.get("x-canonical-path"), str):
                errors.append(f"{path.relative_to(ROOT)}:{key}: missing x-canonical-path")
                continue
            canonical_path = path_item["x-canonical-path"]
            methods = [method for method in path_item if method in HTTP_METHODS]
            if not methods:
                errors.append(f"{path.relative_to(ROOT)}:{key}: no HTTP operation")
                continue
            for method in methods:
                mirror_count += 1
                mirror = path_item[method]
                main = main_by_key.get((canonical_path, method))
                if main is None:
                    errors.append(f"{path.relative_to(ROOT)}:{key}:{method}: not found in main OpenAPI")
                    continue
                for field in ("operationId", *REQUIRED_EXTENSIONS):
                    if mirror.get(field) != main.get(field):
                        errors.append(
                            f"{path.relative_to(ROOT)}:{key}:{method}: {field} differs from main OpenAPI"
                        )
    if mirror_count != 38:
        errors.append(f"modules: expected 38 mirrored operations, found {mirror_count}")


def check_document(document: dict[str, Any], errors: list[str]) -> None:
    if document.get("openapi") != "3.1.0":
        errors.append("openapi.yaml: openapi must be 3.1.0")
    if document.get("info", {}).get("version") != "1.3.2":
        errors.append("openapi.yaml: info.version must be 1.3.2")
    if [server.get("url") for server in document.get("servers", [])] != ["/api/v1"]:
        errors.append("openapi.yaml: server must be exactly /api/v1")
    ops = operations(document)
    if len(ops) != 41:
        errors.append(f"openapi.yaml: expected 41 operations, found {len(ops)}")
    operation_ids: dict[str, tuple[str, str]] = {}
    for path, method, operation in ops:
        operation_id = operation.get("operationId")
        if not isinstance(operation_id, str) or not operation_id:
            errors.append(f"{method.upper()} {path}: operationId is required")
        elif operation_id in operation_ids:
            errors.append(f"duplicate operationId {operation_id}: {operation_ids[operation_id]} and {(method, path)}")
        else:
            operation_ids[operation_id] = (method, path)
        for field in REQUIRED_EXTENSIONS:
            if field not in operation:
                errors.append(f"{method.upper()} {path}: missing {field}")
        if operation.get("x-data-scope") not in ALLOWED_SCOPES:
            errors.append(f"{method.upper()} {path}: invalid x-data-scope")
        if operation.get("x-status") not in ALLOWED_STATUSES:
            errors.append(f"{method.upper()} {path}: invalid x-status")
        idempotency = operation.get("x-idempotency")
        if not isinstance(idempotency, str) or not (
            idempotency == "none"
            or idempotency == "event_id"
            or idempotency == "assignment_command"
            or idempotency.startswith("domain_key_")
        ):
            errors.append(f"{method.upper()} {path}: invalid x-idempotency")
        if operation.get("x-owner") in (None, ""):
            errors.append(f"{method.upper()} {path}: x-owner is required")
        if operation.get("security") == [{"bearerAuth": []}]:
            for code in ("401", "403"):
                if code not in operation.get("responses", {}):
                    errors.append(f"{method.upper()} {path}: missing {code} response")
        elif operation.get("x-permission") == "system_webhook" and "401" not in operation.get("responses", {}):
            errors.append(f"{method.upper()} {path}: webhook must define 401 response")
        if method in {"post", "put", "patch", "delete"}:
            if not any(code in operation.get("responses", {}) for code in ("400", "409", "503")):
                errors.append(f"{method.upper()} {path}: write operation needs validation/conflict/external error")
        for parameter in operation.get("parameters", []):
            parameter = resolve_local_ref(document, parameter)
            if parameter is None:
                errors.append(f"{method.upper()} {path}: unresolved parameter reference")
        for response_code, response in operation.get("responses", {}).items():
            if resolve_local_ref(document, response) is None:
                errors.append(f"{method.upper()} {path}: unresolved response {response_code}")
        for path_parameter in re.findall(r"\{([^}]+)\}", path):
            declared = False
            path_item = document["paths"][path]
            for parameter in [*path_item.get("parameters", []), *operation.get("parameters", [])]:
                resolved = resolve_local_ref(document, parameter)
                if isinstance(resolved, dict) and resolved.get("in") == "path" and resolved.get("name") == path_parameter:
                    declared = True
            if not declared:
                errors.append(f"{method.upper()} {path}: path parameter {path_parameter} is not declared")

    if "/imports/execute" in document.get("paths", {}):
        errors.append("openapi.yaml: /imports/execute is not allowed in V1.3.2")
    if "JsonObject" in document.get("components", {}).get("requestBodies", {}):
        errors.append("openapi.yaml: generic JsonObject request body is not allowed")
    critical_requests = [name for name in document.get("components", {}).get("schemas", {}) if name.endswith("Request")]
    for name in critical_requests:
        schema = document["components"]["schemas"][name]
        if schema.get("additionalProperties") is not False:
            errors.append(f"components.schemas.{name}: additionalProperties must be false")

    analytics = document["paths"].get("/analytics/summary", {}).get("get", {})
    analytics_200 = resolve_local_ref(document, analytics.get("responses", {}).get("200"))
    if analytics.get("x-permission") != "analytics.read":
        errors.append("analytics summary: permission must be analytics.read")
    if "503" not in analytics.get("responses", {}):
        errors.append("analytics summary: 503 DATA_SOURCE_UNAVAILABLE response is required")
    if not isinstance(analytics_200, dict) or analytics_200.get("content", {}).get("application/json", {}).get("schema", {}).get("properties", {}).get("data", {}).get("$ref") != "#/components/schemas/AnalyticsSummaryData":
        errors.append("analytics summary: 200 response must use AnalyticsSummaryData")
    query_names = {parameter.get("name") for parameter in analytics.get("parameters", [])}
    if query_names != {"from", "to", "orgCodePrefix"}:
        errors.append(f"analytics summary: query parameters must be from/to/orgCodePrefix, found {sorted(query_names)}")
    analytics_schema = document["components"]["schemas"].get("AnalyticsSummaryData", {})
    required = set(analytics_schema.get("required", []))
    expected = {"from", "to", "orgCodePrefix", "clickCount", "accessCount", "installCount", "inAppCount"}
    if required != expected:
        errors.append("AnalyticsSummaryData: required fields do not match frozen four-counter contract")


def main() -> int:
    errors: list[str] = []
    try:
        document = load_yaml(OPENAPI)
        check_document(document, errors)
        check_permission_mapping(document, errors)
        check_modules(document, errors)
    except ValueError as exc:
        errors.append(str(exc))
    if errors:
        print("OpenAPI contract validation failed:")
        print("\n".join(f"- {error}" for error in errors))
        return 1
    print("OpenAPI contract validation passed (41 operations, 38 module mirrors).")
    return 0


if __name__ == "__main__":
    sys.exit(main())
