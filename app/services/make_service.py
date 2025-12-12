import requests
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

# Webhook endpoints (change to env if you prefer)
WEBHOOK_SUBSCRIPTION = "https://hook.eu2.make.com/xcgt6zuc2lxcpqp3vlhwpuspqswm77rf"
WEBHOOK_ACCOUNT_CREATED = "https://hook.eu2.make.com/67oht2141ucgn7sjx4oysaj8ybxmhcan"
MAKE_WEBHOOK_URL = "https://hook.eu2.make.com/j64u5rj9rtsuczkrllgydwvsyy8xay2h"

DEFAULT_TIMEOUT = 10


def send_webhook(url: str, payload: dict, timeout: int = DEFAULT_TIMEOUT) -> tuple:
    """POST payload to Make webhook and return (success, response)

    Returns (True, parsed_json_or_text) on 2xx, else (False, response_text_or_exception).
    """
    try:
        resp = requests.post(url, json=payload, timeout=timeout)
        try:
            parsed = resp.json()
        except Exception:
            parsed = resp.text

        if 200 <= resp.status_code < 300:
            logger.info(f"Webhook POST success to {url}: {parsed}")
            return True, parsed
        else:
            logger.warning(f"Webhook POST non-2xx ({resp.status_code}) to {url}: {parsed}")
            return False, parsed
    except requests.exceptions.RequestException as e:
        logger.error(f"Webhook POST error to {url}: {e}")
        return False, str(e)


def send_subscription_webhook(subscription, ecocash_response=None):
    payload = {
        'subscription_id': getattr(subscription, 'id', None),
        'user_id': getattr(subscription, 'user_id', None),
        'plan_id': getattr(subscription, 'plan_id', None),
        'status': getattr(subscription, 'status', None),
        'billing_interval': getattr(subscription, 'billing_interval', None),
        'amount': getattr(subscription, 'amount_billed', None) or None,
        'ecocash_response': ecocash_response,
        'timestamp': datetime.utcnow().isoformat()
    }
    return send_webhook(WEBHOOK_SUBSCRIPTION, payload)


def send_account_created_webhook(user):
    payload = {
        'user_id': getattr(user, 'id', None),
        'email': getattr(user, 'email', None),
        'name': getattr(user, 'name', None),
        'facebook_id': getattr(user, 'facebook_id', None),
        'created_at': getattr(user, 'created_at', None).isoformat() if getattr(user, 'created_at', None) else None
    }
    return send_webhook(WEBHOOK_ACCOUNT_CREATED, payload)


def send_page_selection_webhook(page_id: str, page_access_token: str, user_id: int = None):
    payload = {
        'page_id': page_id,
        'page_access_token': page_access_token,
        'user_id': user_id,
        'timestamp': datetime.utcnow().isoformat()
    }
    return send_webhook(MAKE_WEBHOOK_URL, payload)
