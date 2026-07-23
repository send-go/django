"""Sendgo Django 설정 로딩 및 클라이언트 생성 모듈.

`settings.SENDGO` 딕셔너리를 읽어 `Sendgo` 코어 클라이언트를 생성/메모이즈합니다.
"""

from __future__ import annotations

from typing import Optional

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from sendgo import Sendgo

# 기본값
DEFAULT_API_VERSION = "v2"
DEFAULT_BASE_URL = "https://sendgo.io"

# 메모이즈된 클라이언트 인스턴스
_client: Optional[Sendgo] = None


def _get_settings() -> dict:
    """settings.SENDGO 딕셔너리를 반환합니다. 없으면 빈 딕셔너리."""
    return getattr(settings, "SENDGO", None) or {}


def get_client() -> Sendgo:
    """설정 기반 Sendgo 클라이언트를 생성하고 메모이즈합니다.

    ACCESS_KEY 또는 SECRET_KEY가 없으면 ImproperlyConfigured 예외를 발생시킵니다.
    """
    global _client

    if _client is not None:
        return _client

    config = _get_settings()

    access_key = config.get("ACCESS_KEY")
    secret_key = config.get("SECRET_KEY")

    if not access_key or not secret_key:
        raise ImproperlyConfigured(
            "Sendgo 설정이 올바르지 않습니다. "
            "settings.SENDGO 에 ACCESS_KEY 와 SECRET_KEY 를 지정하세요."
        )

    _client = Sendgo(
        access_key=access_key,
        secret_key=secret_key,
        kakao_sender_key=config.get("KAKAO_SENDER_KEY"),
        sms_sender_key=config.get("SMS_SENDER_KEY"),
        api_version=config.get("API_VERSION", DEFAULT_API_VERSION),
        base_url=config.get("BASE_URL", DEFAULT_BASE_URL),
    )
    return _client


def reset() -> None:
    """메모이즈된 클라이언트를 초기화합니다. (주로 테스트용)"""
    global _client
    _client = None
