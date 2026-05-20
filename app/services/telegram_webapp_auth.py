import hashlib
import hmac
import json
from urllib.parse import parse_qsl

from fastapi import HTTPException


def validate_telegram_init_data(init_data: str, bot_token: str) -> dict:
    parsed_data = dict(parse_qsl(init_data, keep_blank_values=True))

    received_hash = parsed_data.pop("hash", None)
    if not received_hash:
        raise HTTPException(status_code=401, detail="missing_telegram_hash")

    data_check_string = "\n".join(
        f"{key}={value}"
        for key, value in sorted(parsed_data.items())
    )

    secret_key = hmac.new(
        key=b"WebAppData",
        msg=bot_token.encode(),
        digestmod=hashlib.sha256,
    ).digest()

    calculated_hash = hmac.new(
        key=secret_key,
        msg=data_check_string.encode(),
        digestmod=hashlib.sha256,
    ).hexdigest()

    if not hmac.compare_digest(calculated_hash, received_hash):
        raise HTTPException(status_code=401, detail="invalid_telegram_init_data")

    user_raw = parsed_data.get("user")
    if not user_raw:
        raise HTTPException(status_code=401, detail="telegram_user_not_found")

    return json.loads(user_raw)