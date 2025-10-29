from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict
from urllib import error, parse, request

CONFIG_PATH = Path(__file__).resolve().parent / "config" / "firebase.json"

def load_config(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as fh:
        config = json.load(fh)

    missing = {key for key in ("apiKey", "projectId") if key not in config}
    if missing:
        missing_list = ", ".join(sorted(missing))
        raise ValueError(f"Firebase config is missing required key(s): {missing_list}")

    return config

def encode_value(value: Any) -> Dict[str, Any]:
    if value is None:
        return {"nullValue": None}
    if isinstance(value, bool):
        return {"booleanValue": value}
    if isinstance(value, int):
        return {"integerValue": str(value)}
    if isinstance(value, float):
        return {"doubleValue": value}
    if isinstance(value, str):
        return {"stringValue": value}
    if isinstance(value, dict):
        return {
            "mapValue": {
                "fields": {key: encode_value(inner) for key, inner in value.items()}
            }
        }
    if isinstance(value, (list, tuple)):
        return {"arrayValue": {"values": [encode_value(item) for item in value]}}
    raise TypeError(f"Unsupported value type for Firestore encoding: {type(value)!r}")


def decode_value(value: Dict[str, Any]) -> Any:
    if "nullValue" in value:
        return None
    if "booleanValue" in value:
        return value["booleanValue"]
    if "integerValue" in value:
        return int(value["integerValue"])
    if "doubleValue" in value:
        return value["doubleValue"]
    if "stringValue" in value:
        return value["stringValue"]
    if "mapValue" in value:
        fields = value["mapValue"].get("fields", {})
        return {key: decode_value(inner) for key, inner in fields.items()}
    if "arrayValue" in value:
        values = value["arrayValue"].get("values", [])
        return [decode_value(item) for item in values]
    if "timestampValue" in value:
        return value["timestampValue"]
    return value


def decode_document(document: Dict[str, Any]) -> Dict[str, Any]:
    fields = document.get("fields", {})
    return {key: decode_value(value) for key, value in fields.items()}


def call_firestore(
    method: str,
    base_url: str,
    api_key: str,
    endpoint: str,
    params: Dict[str, Any] | None = None,
    body: Dict[str, Any] | None = None,
) -> Dict[str, Any]:
    params = dict(params or {})
    params.setdefault("key", api_key)

    query = parse.urlencode(params, doseq=True)
    cleaned_endpoint = endpoint.lstrip('/')
    url = f"{base_url}/{cleaned_endpoint}"
    if query:
        url = f"{url}?{query}"

    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Content-Type": "application/json"} if body is not None else {}

    req = request.Request(url, data=data, headers=headers, method=method.upper())

    try:
        with request.urlopen(req) as response:
            if response.status == 204:
                return {}
            return json.load(response)
    except error.HTTPError as exc:  # pragma: no cover - network dependent
        try:
            payload = json.loads(exc.read())
            message = payload.get("error", {}).get("message", str(payload))
        except json.JSONDecodeError:
            message = exc.reason
        raise RuntimeError(f"Firestore API {method} {endpoint} failed: {message}") from exc


def main() -> None:
    config = load_config(CONFIG_PATH)
    project_id: str = config["projectId"]
    api_key: str = config["apiKey"]
    base_url = f"https://firestore.googleapis.com/v1/projects/{project_id}/databases/(default)"

    print(f"Using Firebase project '{project_id}'.")

    sample_data = {"first": "Ada", "last": "Lovelace", "born": 1815}
    encoded = {"fields": {key: encode_value(value) for key, value in sample_data.items()}}
    document_endpoint = "documents/users"
    document_params = {"documentId": "alovelace"}

    print("Writing sample document to Firestore...")
    try:
        result = call_firestore(
            "POST",
            base_url,
            api_key,
            document_endpoint,
            params=document_params,
            body=encoded,
        )
    except RuntimeError as write_error:
        if "already exists" in str(write_error).lower():
            print("Document exists already; updating instead.")
            update_params = {"updateMask.fieldPaths": list(sample_data.keys())}
            result = call_firestore(
                "PATCH",
                base_url,
                api_key,
                f"{document_endpoint}/alovelace",
                params=update_params,
                body=encoded,
            )
        else:
            raise

    stored = {
        "name": result.get("name"),
        "fields": decode_document(result),
    }
    print("Document stored:")
    print(json.dumps(stored, indent=2))

    print("\nCurrent documents in 'users':")
    documents = call_firestore("GET", base_url, api_key, document_endpoint)
    for document in documents.get("documents", []):
        decoded = decode_document(document)
        print(f"- {document['name'].split('/')[-1]} => {decoded}")
    if not documents.get("documents"):
        print("(no documents found)")

    print("\nRetrieving the 'alovelace' document...")
    fetched = call_firestore("GET", base_url, api_key, f"{document_endpoint}/alovelace")
    print(json.dumps(decode_document(fetched), indent=2))


if __name__ == "__main__":
    main()
