import warnings

from django.apps import AppConfig


class SendgoConfig(AppConfig):
    """Sendgo Django 확장 앱 설정."""

    name = "sendgo_django"
    verbose_name = "Sendgo 메시지 발송"

    def ready(self) -> None:
        """앱 로드 시 SENDGO 설정 존재 여부를 검증합니다.

        설정이 없더라도 앱 로딩을 막지 않고 경고만 출력합니다.
        (실제 클라이언트 생성 시점에 ImproperlyConfigured가 발생합니다.)
        """
        from django.conf import settings

        if not getattr(settings, "SENDGO", None):
            warnings.warn(
                "settings.SENDGO 설정이 없습니다. "
                "Sendgo 클라이언트를 사용하려면 SENDGO 딕셔너리를 정의하세요.",
                stacklevel=2,
            )
