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

from .conf import get_client

# 설정이 없어도 임포트 자체는 실패하지 않도록, 실제 접근 시점에만
# get_client()를 호출하는 지연 프록시를 제공합니다.
client = SimpleLazyObject(get_client)

__all__ = ["get_client", "client"]
__version__ = "1.0.0"
