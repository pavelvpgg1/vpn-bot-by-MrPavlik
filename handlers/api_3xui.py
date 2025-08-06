import uuid
from datetime import datetime, timedelta
from os import environ

import py3xui
import pytz
from py3xui import Client

from config import XUI_HOST, XUI_USERNAME, XUI_PASSWORD, PBK, SID

environ["XUI_HOST"] = XUI_HOST
environ["XUI_USERNAME"] = XUI_USERNAME
environ["XUI_PASSWORD"] = XUI_PASSWORD

api = py3xui.AsyncApi.from_env()


async def login_api():
    await api.login()


async def create_client_for_user(tg_user_id: int, duration_days: int):
    """Асинхронное создание клиента"""
    email = f"{tg_user_id}@MrPavlik.ru"

    tz = pytz.timezone("Asia/Yekaterinburg")
    expiry_dt = datetime.now(tz) + timedelta(days=duration_days)
    expiry_dt_utc = expiry_dt.astimezone(pytz.utc)
    expiry_timestamp = int(expiry_dt_utc.timestamp() * 1000)

    client = Client(
        id=str(uuid.uuid4()),
        email=email,
        enable=True,
        flow="xtls-rprx-vision",
        limit_ip=0,
        total_gb=0,
        expiry_time=expiry_timestamp,
        tg_id=str(tg_user_id)
    )

    # Добавление клиента в основной инбаунд с ID 7
    await api.client.add(inbound_id=7, clients=[client])


async def generate_vpn_link(user_email: str) -> str:
    """Асинхронная генерация ссылки на VPN"""
    inbound = await api.inbound.get_by_id(7)

    clients = inbound.settings.clients or []
    client = next((c for c in clients if c.email == user_email), None)
    if not client:
        return "❌ Ошибка: клиент не найден."

    uuid = client.id
    port = inbound.port
    server_ip = "45.145.163.190"

    reality = getattr(inbound.stream_settings, "reality_settings", None)
    if not reality:
        return "❌ Ошибка: reality_settings не найден."

    public_key = PBK
    server_names = getattr(reality, "server_names", [])
    sni = server_names[0] if server_names else "yahoo.com"

    fingerprint = "chrome"
    sid = SID
    flow = "xtls-rprx-vision"
    spx = "%2F"
    tag = user_email.split("@")[0].replace(".", "_").replace("-", "_") + "%40" + user_email.split("@")[1]

    link = (
        f"vless://{uuid}@{server_ip}:{port}"
        f"?type=tcp"
        f"&security=reality"
        f"&pbk={public_key}"
        f"&fp={fingerprint}"
        f"&sni={sni}"
        f"&sid={sid}"
        f"&spx={spx}"
        f"&flow={flow}"
        f"#Sell_VPN-{tag}"
    )

    return link
