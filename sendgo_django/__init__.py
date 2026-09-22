"""
Sendgo Django 확장 — 카카오 알림톡/친구톡, SMS/LMS/MMS

Django 프로젝트에서 Sendgo 코어(`sendgo-python`)를 손쉽게 사용할 수 있도록
설정 기반의 클라이언트 생성과 지연 로딩 프록시를 제공합니다.

사용법:
    # settings.py
    INSTALLED_APPS += ["sendgo_django"]

    SENDGO = {
        "ACCESS_KEY": "your_access_key",
        "SECRET_KEY": "your_secret_key",
        "KAKAO_SENDER_KEY": "your_kakao_key",
        "SMS_SENDER_KEY": "your_sms_key",
        "API_VERSION": "v2",
    }

    # views.py
    from sendgo_django import client

    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
    )
"""

from django.utils.functional import SimpleLazyObject

from .conf import get_client, get_account_client

# 설정이 없어도 임포트 자체는 실패하지 않도록, 실제 접근 시점에만
# get_client()를 호출하는 지연 프록시를 제공합니다.
client = SimpleLazyObject(get_client)

from sendgo import AccountClient

__all__ = ["get_account_client", "AccountClient", "get_client", "client"]

try:
    from importlib.metadata import PackageNotFoundError, version as _pkg_version

    # 버전은 pyproject.toml 이 단일 출처다. 여기에 값을 또 적으면 릴리스마다
    # 두 곳을 맞춰야 하고, 실제로 1.0.0 에 머물러 있었다.
    __version__ = _pkg_version("sendgo-django")
except PackageNotFoundError:  # 설치되지 않은 소스 트리에서 import 한 경우
    __version__ = "0.0.0.dev0"
