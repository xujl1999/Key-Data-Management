from __future__ import annotations

import asyncio
import base64
import hashlib
import json
import os
import time
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

import httpx
from fastapi import FastAPI, File, Form, Header, Request, UploadFile
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.exceptions import HTTPException as StarletteHTTPException

APP_DIR = Path(__file__).resolve().parent
LOG_PATH = APP_DIR / "logs" / "food_log.jsonl"
MAX_IMAGE_BYTES = 8 * 1024 * 1024
DEFAULT_LOCALE = "zh-CN"
DEFAULT_WARNING = "如有多盘菜/遮挡/光线差，识别可能遗漏"
DEFAULT_UNCERTAINTY_NOTE = "仅根据图片估算，受分量、油盐、烹饪方式影响较大"
SERVICE_VERSION = "food_service_v1"

ALLOWED_MEAL_HINTS = {"breakfast", "lunch", "dinner", "snack"}


app = FastAPI()


@app.middleware("http")
async def add_request_id(request: Request, call_next):
    request.state.request_id = str(uuid.uuid4())
    return await call_next(request)


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return error_response(
        request_id=request_id,
        status_code=400,
        code="BAD_IMAGE",
        message="Invalid request payload.",
        detail=str(exc),
    )


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return error_response(
        request_id=request_id,
        status_code=exc.status_code,
        code="INTERNAL",
        message=exc.detail if isinstance(exc.detail, str) else "HTTP error.",
        detail=str(exc.detail),
    )


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    return error_response(
        request_id=request_id,
        status_code=500,
        code="INTERNAL",
        message="Internal server error.",
        detail=str(exc),
    )


@app.get("/health")
async def health():
    return {"ok": True, "version": SERVICE_VERSION, "ts": int(time.time())}


@app.post("/analyze")
async def analyze(
    request: Request,
    file: UploadFile = File(...),
    meal_hint: Optional[str] = Form(None),
    locale: Optional[str] = Form(None),
    x_token: Optional[str] = Header(default=None, alias="X-Token"),
):
    request_id = getattr(request.state, "request_id", str(uuid.uuid4()))
    expected_token = os.getenv("SHORTCUT_TOKEN", "")
    expected_present = bool(expected_token)
    expected_len, expected_prefix, expected_suffix = mask_token(expected_token)
    header_xtoken = request.headers.get("X-Token")
    header_xtoken_lower = request.headers.get("x-token")
    received_token = header_xtoken or header_xtoken_lower or x_token or ""
    received_token = received_token.strip()
    received_len, received_prefix, received_suffix = mask_token(received_token)
    filename = file.filename if file else None
    content_type = file.content_type if file else None
    image_md5: Optional[str] = None
    print(
        "auth_expected",
        expected_present,
        expected_len,
        expected_prefix,
        expected_suffix,
    )
    print(
        "auth_header_X_Token",
        bool(header_xtoken),
        *mask_token(header_xtoken),
    )
    print(
        "auth_header_x_token",
        bool(header_xtoken_lower),
        *mask_token(header_xtoken_lower),
    )
    print("auth_headers_keys", list(request.headers.keys()))
    print("auth_received", received_len, received_prefix, received_suffix)

    if not verify_token(received_token, expected_token):
        print("auth_compare", f"expected_len={expected_len}", f"got_len={received_len}")
        response = error_response(
            request_id=request_id,
            status_code=401,
            code="UNAUTHORIZED",
            message="Missing or invalid X-Token.",
            detail=None,
        )
        log_request(
            request_id=request_id,
            image_size=None,
            upstream_ms=None,
            summary={"error_code": "UNAUTHORIZED"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response

    if not file or not filename:
        response = error_response(
            request_id=request_id,
            status_code=400,
            code="BAD_IMAGE",
            message="Missing filename in upload.",
            detail=None,
        )
        log_request(
            request_id=request_id,
            image_size=None,
            upstream_ms=None,
            summary={"error_code": "BAD_IMAGE"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response

    if not file or not content_type or not content_type.startswith("image/"):
        response = error_response(
            request_id=request_id,
            status_code=400,
            code="BAD_IMAGE",
            message="Only image/* uploads are supported.",
            detail=f"content_type={content_type}",
        )
        log_request(
            request_id=request_id,
            image_size=None,
            upstream_ms=None,
            summary={"error_code": "BAD_IMAGE"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response

    payload = await file.read()
    image_size = len(payload)
    image_md5 = hashlib.md5(payload).hexdigest()
    if image_size == 0:
        response = error_response(
            request_id=request_id,
            status_code=400,
            code="BAD_IMAGE",
            message="Empty image payload.",
            detail=None,
        )
        log_request(
            request_id=request_id,
            image_size=image_size,
            upstream_ms=None,
            summary={"error_code": "BAD_IMAGE"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response
    if image_size > MAX_IMAGE_BYTES:
        response = error_response(
            request_id=request_id,
            status_code=413,
            code="BAD_IMAGE",
            message="Image exceeds 8MB limit.",
            detail=f"size={image_size}",
        )
        log_request(
            request_id=request_id,
            image_size=image_size,
            upstream_ms=None,
            summary={"error_code": "BAD_IMAGE"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response

    locale = locale or DEFAULT_LOCALE
    meal_hint = normalize_meal_hint(meal_hint)

    try:
        result, upstream_ms, provider_request_id = await analyze_image(
            image_bytes=payload,
            content_type=content_type,
            meal_hint=meal_hint,
            locale=locale,
            request_id=request_id,
        )
    except UpstreamTimeout as exc:
        response = error_response(
            request_id=request_id,
            status_code=502,
            code="UPSTREAM_TIMEOUT",
            message="Upstream timeout.",
            detail=str(exc),
        )
        log_request(
            request_id=request_id,
            image_size=image_size,
            upstream_ms=None,
            summary={"error_code": "UPSTREAM_TIMEOUT"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response
    except UpstreamError as exc:
        response = error_response(
            request_id=request_id,
            status_code=502,
            code="UPSTREAM_ERROR",
            message="Upstream error.",
            detail=str(exc),
        )
        log_request(
            request_id=request_id,
            image_size=image_size,
            upstream_ms=None,
            summary={"error_code": "UPSTREAM_ERROR"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response
    except ParseError as exc:
        response = error_response(
            request_id=request_id,
            status_code=502,
            code="PARSE_ERROR",
            message="Failed to parse upstream response.",
            detail=str(exc),
        )
        log_request(
            request_id=request_id,
            image_size=image_size,
            upstream_ms=None,
            summary={"error_code": "PARSE_ERROR"},
            provider_request_id=None,
            filename=filename,
            content_type=content_type,
            image_md5=image_md5,
        )
        return response

    log_request(
        request_id=request_id,
        image_size=image_size,
        upstream_ms=upstream_ms,
        summary=build_summary(result),
        provider_request_id=provider_request_id,
        filename=filename,
        content_type=content_type,
        image_md5=image_md5,
    )
    return JSONResponse(content=result)


class UpstreamError(RuntimeError):
    pass


class UpstreamTimeout(RuntimeError):
    pass


class ParseError(RuntimeError):
    pass


def verify_token(token: Optional[str], expected: Optional[str]) -> bool:
    if not expected:
        return False
    if not token:
        return False
    return token.strip() == expected.strip()


def mask_token(token: Optional[str]) -> Tuple[int, str, str]:
    if not token:
        return 0, "", ""
    token = str(token)
    length = len(token)
    prefix = token[:4] if length >= 4 else token
    suffix = token[-4:] if length >= 4 else token
    return length, prefix, suffix


def normalize_meal_hint(meal_hint: Optional[str]) -> Optional[str]:
    if not meal_hint:
        return None
    meal_hint = meal_hint.strip().lower()
    return meal_hint if meal_hint in ALLOWED_MEAL_HINTS else None


def error_response(
    request_id: str,
    status_code: int,
    code: str,
    message: str,
    detail: Optional[str],
):
    payload = {
        "request_id": request_id,
        "ts": int(time.time()),
        "error": {
            "code": code,
            "message": message,
            "detail": truncate_detail(detail),
        },
    }
    return JSONResponse(status_code=status_code, content=payload)


def truncate_detail(detail: Optional[str]) -> Optional[str]:
    if detail is None:
        return None
    detail = str(detail)
    return detail[:500]


def build_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    items = result.get("items") or []
    names = []
    for item in items:
        if isinstance(item, dict) and item.get("name_zh"):
            names.append(item.get("name_zh"))
    totals = result.get("totals") or {}
    return {
        "items_count": len(items),
        "items_names_zh": names,
        "calories_kcal": totals.get("calories_kcal"),
    }


def log_request(
    request_id: str,
    image_size: Optional[int],
    upstream_ms: Optional[int],
    summary: Dict[str, Any],
    provider_request_id: Optional[str],
    filename: Optional[str] = None,
    content_type: Optional[str] = None,
    image_md5: Optional[str] = None,
):
    LOG_PATH.parent.mkdir(parents=True, exist_ok=True)
    entry = {
        "ts": int(time.time()),
        "request_id": request_id,
        "image_size": image_size,
        "filename": filename,
        "content_type": content_type,
        "image_md5": image_md5,
        "upstream_ms": upstream_ms,
        "summary": summary,
        "provider_request_id": provider_request_id,
    }
    with LOG_PATH.open("a", encoding="utf-8") as handle:
        handle.write(json.dumps(entry, ensure_ascii=False) + "\n")


async def analyze_image(
    image_bytes: bytes,
    content_type: str,
    meal_hint: Optional[str],
    locale: str,
    request_id: str,
) -> Tuple[Dict[str, Any], Optional[int], Optional[str]]:
    raw_key = os.getenv("QWEN_API_KEY") or ""
    api_key = raw_key.strip().strip("\"").strip("'")
    if api_key.lower().startswith("bearer "):
        api_key = api_key[7:].strip()
    api_key = "".join(ch for ch in api_key if ch.isascii() and not ch.isspace())
    if not api_key:
        raise UpstreamError("QWEN_API_KEY is not set or invalid.")

    api_base = os.getenv("QWEN_API_BASE", "https://dashscope.aliyuncs.com/compatible-mode/v1")
    model = os.getenv("QWEN_MODEL", "qwen-vl-plus")
    model_alias = os.getenv("QWEN_MODEL_ALIAS", "qwen-vision")

    prompt = build_prompt(locale=locale, meal_hint=meal_hint)
    image_url = to_data_url(content_type, image_bytes)
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": "You are a nutrition analyst. Return only JSON."},
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            },
        ],
        "temperature": 0.2,
        "top_p": 0.9,
        "max_tokens": 1200,
    }

    url = f"{api_base.rstrip('/')}/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "X-DashScope-Api-Key": api_key,
    }

    upstream_ms: Optional[int] = None
    last_error: Optional[str] = None

    async with httpx.AsyncClient(timeout=httpx.Timeout(20.0)) as client:
        for attempt in range(2):
            try:
                start = time.perf_counter()
                response = await client.post(url, json=payload, headers=headers)
                upstream_ms = int((time.perf_counter() - start) * 1000)
            except httpx.TimeoutException as exc:
                last_error = str(exc)
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise UpstreamTimeout(last_error)
            except httpx.HTTPError as exc:
                last_error = str(exc)
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise UpstreamError(last_error)

            if response.status_code >= 400:
                last_error = response.text
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise UpstreamError(f"HTTP {response.status_code}: {truncate_detail(last_error)}")

            try:
                data = response.json()
            except json.JSONDecodeError:
                last_error = response.text
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise ParseError(truncate_detail(last_error))

            content = extract_content(data)
            provider_request_id = extract_provider_request_id(data, response)
            parsed = extract_json_object(content)
            if parsed is None:
                last_error = content
                if attempt == 0:
                    await asyncio.sleep(0.5)
                    continue
                raise ParseError(truncate_detail(last_error))

            normalized = normalize_response(
                parsed,
                request_id=request_id,
                ts=int(time.time()),
                locale=locale,
                meal_hint=meal_hint,
                model_alias=model_alias,
                provider_request_id=provider_request_id,
            )
            return normalized, upstream_ms, provider_request_id

    raise UpstreamError(last_error or "Unknown upstream error.")


def build_prompt(locale: str, meal_hint: Optional[str]) -> str:
    hint = meal_hint or "unknown"
    return (
        "Analyze the food in the image and respond with a single JSON object only. "
        "Use null for unknown numeric fields. Numbers must be numbers, not strings. "
        "Confidence must be between 0 and 1. "
        "If any food is visible, items MUST contain at least one object; "
        "if unsure, set name_zh/name_en to \"unknown\" and keep numbers as null. "
        "Do multi-dish enumeration: scan the image top-to-bottom, left-to-right, and list each "
        "container/plate/bowl/pot/package with edible items in items. "
        "Prefer recall over precision: include possible items with low confidence rather than "
        "returning only one item. If the image clearly shows 3 or more containers/dishes, items "
        "MUST include at least 3 entries unless they are clearly empty. "
        "Merge same dishes across multiple plates into one item and use quantity to represent servings. "
        "Totals must sum across all items for calories_kcal, macros_g, and micros. "
        "Each item evidence.visual_cues must list the key visual clues. "
        "If occlusion/glare/poor lighting may cause misses, add a warning and lower confidence. "
        "Output must follow this schema keys exactly:\n"
        "{\n"
        '  "source": {"model": "qwen-vision", "method": "image_only_estimation", "locale": "'
        + locale
        + '"},\n'
        '  "meal": {"hint": "' + hint + '", "detected": null, "confidence": null},\n'
        '  "items": [\n'
        "    {\n"
        '      "name_zh": null,\n'
        '      "name_en": null,\n'
        '      "category": null,\n'
        '      "quantity": null,\n'
        '      "unit": null,\n'
        '      "estimated_weight_g": null,\n'
        '      "calories_kcal": null,\n'
        '      "macros_g": {"protein_g": null, "carbs_g": null, "fat_g": null, "fiber_g": null},\n'
        '      "micros": {"sodium_mg": null, "sugar_g": null},\n'
        '      "confidence": null,\n'
        '      "evidence": {"visual_cues": [], "assumptions": []}\n'
        "    }\n"
        "  ],\n"
        '  "uncertainty": {"overall_level": "medium", "estimated_error_percent": 25, '
        '"notes": ["' + DEFAULT_UNCERTAINTY_NOTE + '"]},\n'
        '  "warnings": ["' + DEFAULT_WARNING + '"],\n'
        '  "raw": {"provider": "qwen", "provider_request_id": null}\n'
        "}\n"
        "Return JSON only. Do not use markdown or code fences."
    )


def extract_content(data: Any) -> str:
    if isinstance(data, dict):
        if isinstance(data.get("choices"), list) and data["choices"]:
            choice = data["choices"][0]
            message = choice.get("message") or {}
            content = message.get("content")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: List[str] = []
                for part in content:
                    if isinstance(part, dict):
                        text = part.get("text") or part.get("content")
                        if isinstance(text, str):
                            parts.append(text)
                    elif isinstance(part, str):
                        parts.append(part)
                combined = "".join(parts).strip()
                if combined:
                    return combined
        output = data.get("output")
        if isinstance(output, dict):
            text = output.get("text")
            if isinstance(text, str):
                return text
        output_text = data.get("output_text")
        if isinstance(output_text, str):
            return output_text
    raise ParseError("No assistant content found in response.")


def extract_provider_request_id(data: Any, response: httpx.Response) -> Optional[str]:
    if isinstance(data, dict):
        if isinstance(data.get("id"), str):
            return data.get("id")
        if isinstance(data.get("request_id"), str):
            return data.get("request_id")
    return response.headers.get("x-request-id")


def extract_json_object(text: str) -> Optional[Dict[str, Any]]:
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = text.strip("`")
        text = text.replace("json", "", 1).strip()
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        pass

    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end == -1 or end <= start:
        return None
    snippet = text[start : end + 1]
    try:
        parsed = json.loads(snippet)
        return parsed if isinstance(parsed, dict) else None
    except json.JSONDecodeError:
        return None


def normalize_response(
    payload: Dict[str, Any],
    request_id: str,
    ts: int,
    locale: str,
    meal_hint: Optional[str],
    model_alias: str,
    provider_request_id: Optional[str],
) -> Dict[str, Any]:
    payload = payload if isinstance(payload, dict) else {}
    payload = unwrap_payload(payload)
    items_raw = resolve_items(payload)
    if isinstance(items_raw, dict):
        items_raw = [items_raw]
    items: List[Dict[str, Any]] = []
    if isinstance(items_raw, list):
        for item in items_raw:
            if isinstance(item, dict):
                items.append(normalize_item(item))
            elif isinstance(item, str):
                items.append(
                    {
                        "name_zh": item if locale.startswith("zh") else None,
                        "name_en": item if not locale.startswith("zh") else None,
                        "category": None,
                        "quantity": None,
                        "unit": None,
                        "estimated_weight_g": None,
                        "calories_kcal": None,
                        "macros_g": {
                            "protein_g": None,
                            "carbs_g": None,
                            "fat_g": None,
                            "fiber_g": None,
                        },
                        "micros": {"sodium_mg": None, "sugar_g": None},
                        "confidence": None,
                        "evidence": {"visual_cues": [], "assumptions": []},
                    }
                )

    totals = compute_totals(items)
    meal = normalize_meal(payload.get("meal"), meal_hint)
    uncertainty = normalize_uncertainty(payload.get("uncertainty"))
    warnings = normalize_warnings(payload.get("warnings"))

    return {
        "request_id": request_id,
        "ts": ts,
        "source": {
            "model": model_alias,
            "method": "image_only_estimation",
            "locale": locale,
        },
        "meal": meal,
        "items": items,
        "totals": totals,
        "uncertainty": uncertainty,
        "warnings": warnings,
        "raw": {
            "provider": "qwen",
            "provider_request_id": provider_request_id,
        },
    }


def unwrap_payload(payload: Dict[str, Any]) -> Dict[str, Any]:
    for key in ("data", "result", "output", "analysis", "response"):
        nested = payload.get(key)
        if isinstance(nested, dict):
            return nested
    return payload


def resolve_items(payload: Dict[str, Any]) -> Optional[Any]:
    for key in ("items", "foods", "food_items", "dishes", "dish_items", "results"):
        value = payload.get(key)
        if value is not None:
            return value
    return find_items_candidate(payload)


def find_items_candidate(payload: Dict[str, Any]) -> Optional[List[Dict[str, Any]]]:
    stack = [payload]
    while stack:
        current = stack.pop()
        if isinstance(current, dict):
            for value in current.values():
                if isinstance(value, dict):
                    stack.append(value)
                elif isinstance(value, list):
                    if value and all(isinstance(item, dict) for item in value):
                        if list_has_food_keys(value):
                            return value
                    for item in value:
                        if isinstance(item, dict):
                            stack.append(item)
        elif isinstance(current, list):
            for item in current:
                if isinstance(item, dict):
                    stack.append(item)
    return None


def list_has_food_keys(items: List[Dict[str, Any]]) -> bool:
    keys = {
        "name",
        "name_zh",
        "name_en",
        "food",
        "food_name",
        "dish",
        "dish_name",
        "calories",
        "calories_kcal",
        "kcal",
        "weight",
        "estimated_weight_g",
        "quantity",
        "unit",
    }
    for item in items:
        if keys.intersection(item.keys()):
            return True
    return False


def normalize_meal(raw: Any, meal_hint: Optional[str]) -> Dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    detected = raw.get("detected") if isinstance(raw.get("detected"), str) else meal_hint
    confidence = clamp_confidence(raw.get("confidence"))
    return {"hint": meal_hint, "detected": detected, "confidence": confidence}


def normalize_uncertainty(raw: Any) -> Dict[str, Any]:
    raw = raw if isinstance(raw, dict) else {}
    notes = raw.get("notes")
    if not isinstance(notes, list):
        notes = [DEFAULT_UNCERTAINTY_NOTE]
    return {
        "overall_level": raw.get("overall_level") if isinstance(raw.get("overall_level"), str) else "medium",
        "estimated_error_percent": ensure_number(raw.get("estimated_error_percent")) or 25,
        "notes": notes,
    }


def normalize_warnings(raw: Any) -> List[str]:
    if isinstance(raw, list) and raw:
        return [str(item) for item in raw]
    return [DEFAULT_WARNING]


def normalize_item(item: Dict[str, Any]) -> Dict[str, Any]:
    macros = normalize_macros(item.get("macros_g"))
    micros = normalize_micros(item.get("micros"))
    evidence = normalize_evidence(item.get("evidence"))
    return {
        "name_zh": item.get("name_zh") if isinstance(item.get("name_zh"), str) else None,
        "name_en": item.get("name_en") if isinstance(item.get("name_en"), str) else None,
        "category": item.get("category") if isinstance(item.get("category"), str) else None,
        "quantity": ensure_number(item.get("quantity")),
        "unit": item.get("unit") if isinstance(item.get("unit"), str) else None,
        "estimated_weight_g": ensure_number(item.get("estimated_weight_g")),
        "calories_kcal": ensure_number(item.get("calories_kcal")),
        "macros_g": macros,
        "micros": micros,
        "confidence": clamp_confidence(item.get("confidence")),
        "evidence": evidence,
    }


def normalize_macros(raw: Any) -> Dict[str, Optional[float]]:
    raw = raw if isinstance(raw, dict) else {}
    return {
        "protein_g": ensure_number(raw.get("protein_g")),
        "carbs_g": ensure_number(raw.get("carbs_g")),
        "fat_g": ensure_number(raw.get("fat_g")),
        "fiber_g": ensure_number(raw.get("fiber_g")),
    }


def normalize_micros(raw: Any) -> Dict[str, Optional[float]]:
    raw = raw if isinstance(raw, dict) else {}
    return {
        "sodium_mg": ensure_number(raw.get("sodium_mg")),
        "sugar_g": ensure_number(raw.get("sugar_g")),
    }


def normalize_evidence(raw: Any) -> Dict[str, List[str]]:
    raw = raw if isinstance(raw, dict) else {}
    visual = raw.get("visual_cues") if isinstance(raw.get("visual_cues"), list) else []
    assumptions = raw.get("assumptions") if isinstance(raw.get("assumptions"), list) else []
    return {
        "visual_cues": [str(item) for item in visual],
        "assumptions": [str(item) for item in assumptions],
    }


def compute_totals(items: List[Dict[str, Any]]) -> Dict[str, Any]:
    totals: Dict[str, Any] = {
        "calories_kcal": sum_numbers([item.get("calories_kcal") for item in items]),
        "macros_g": {
            "protein_g": sum_numbers([item.get("macros_g", {}).get("protein_g") for item in items]),
            "carbs_g": sum_numbers([item.get("macros_g", {}).get("carbs_g") for item in items]),
            "fat_g": sum_numbers([item.get("macros_g", {}).get("fat_g") for item in items]),
            "fiber_g": sum_numbers([item.get("macros_g", {}).get("fiber_g") for item in items]),
        },
        "micros": {
            "sodium_mg": sum_numbers([item.get("micros", {}).get("sodium_mg") for item in items]),
            "sugar_g": sum_numbers([item.get("micros", {}).get("sugar_g") for item in items]),
        },
    }
    return totals


def sum_numbers(values: List[Any]) -> Optional[float]:
    total = 0.0
    has_value = False
    for value in values:
        number = ensure_number(value)
        if number is None:
            continue
        total += float(number)
        has_value = True
    return round(total, 3) if has_value else None


def ensure_number(value: Any) -> Optional[float]:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            return None
    return None


def clamp_confidence(value: Any) -> Optional[float]:
    number = ensure_number(value)
    if number is None:
        return None
    return max(0.0, min(1.0, float(number)))


def to_data_url(content_type: str, image_bytes: bytes) -> str:
    encoded = base64.b64encode(image_bytes).decode("ascii")
    return f"data:{content_type};base64,{encoded}"
