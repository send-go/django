# sendgo-django

> **Django에서 카카오 알림톡, 친구톡, SMS를 가장 쉽게 발송하는 공식 Django 확장 패키지**

[![PyPI](https://img.shields.io/pypi/v/sendgo-django)](https://pypi.org/project/sendgo-django/)
[![Django](https://img.shields.io/badge/Django-4.2%2B-092E20?logo=django)](https://www.djangoproject.com)
[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?logo=python)](https://python.org)
[![License](https://img.shields.io/badge/license-MIT-blue)](LICENSE)

`sendgo-django`는 [`sendgo-python`](https://github.com/send-go/python) 코어를 확장한 **Django 전용 패키지**입니다.
`settings.SENDGO` 설정 기반의 클라이언트 생성, 지연 로딩 프록시(`client`), AppConfig 통합을 제공합니다.

---

## 목차

- [설치](#설치)
- [빠른 시작](#빠른-시작)
- [프록시 사용법](#프록시-사용법)
- [상세 사용법](#상세-사용법)
  - [알림톡](#알림톡)
  - [친구톡](#친구톡)
  - [SMS / LMS / MMS](#sms--lms--mms)
- [서비스 클래스 패턴](#서비스-클래스-패턴)
- [예외 처리](#예외-처리)
- [설정 옵션](#설정-옵션)
- [자주 묻는 질문](#자주-묻는-질문-faq)

---

## 설치

```bash
pip install sendgo-django
```

`sendgo-python` 코어는 의존성으로 자동 설치됩니다.

---

## 빠른 시작

### 1단계 — `INSTALLED_APPS` 등록 (`settings.py`)

```python
INSTALLED_APPS += ["sendgo_django"]
```

### 2단계 — `SENDGO` 설정 추가 (`settings.py`)

```python
import os

SENDGO = {
    "ACCESS_KEY": os.environ["SENDGO_ACCESS_KEY"],
    "SECRET_KEY": os.environ["SENDGO_SECRET_KEY"],
    "KAKAO_SENDER_KEY": os.environ.get("SENDGO_KAKAO_SENDER_KEY"),
    "SMS_SENDER_KEY": os.environ.get("SENDGO_SMS_SENDER_KEY"),
    "API_VERSION": "v2",
    # "BASE_URL": "https://sendgo.io",  # 기본값
}
```

### 3단계 — 뷰에서 알림톡 전송

```python
# views.py
from django.http import JsonResponse
from sendgo_django import client


def confirm_order(request, order_id):
    order = get_order(order_id)

    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[
            {
                "contact": order.phone,
                "name": order.name,
                "var1": order.number,
                "var2": f"{order.total:,}원",
            },
        ],
    )

    return JsonResponse({"success": True})
```

---

## 프록시 사용법

`sendgo_django.client`는 `SimpleLazyObject` 기반 **지연 로딩 프록시**입니다.
패키지를 임포트하는 시점에는 클라이언트를 생성하지 않고, 실제로 속성에 접근할 때
`get_client()`를 호출합니다. 따라서 설정이 없어도 임포트만으로는 오류가 나지 않습니다.

```python
from sendgo_django import client

# 알림톡 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
)

# SMS 발송
client.sms.send_sms(
    content="[인증] 인증번호: 123456",
    contacts=[{"contact": "01012345678"}],
)
```

명시적으로 인스턴스를 얻고 싶다면 `get_client()`를 직접 호출할 수 있습니다.

```python
from sendgo_django import get_client

sendgo = get_client()
sendgo.friendtalk.send(content="안녕하세요!", contacts=[{"contact": "01012345678"}])
```

---

## 상세 사용법

### 알림톡

```python
from sendgo_django import client

# 다건 발송
client.alimtalk.send(
    template_code="ORDER_CONFIRM_001",
    contacts=[
        {"contact": "01011111111", "name": "홍길동", "var1": "ORD-001", "var2": "29,000원"},
        {"contact": "01022222222", "name": "김철수", "var1": "ORD-002", "var2": "15,000원"},
    ],
)
```

### 친구톡

```python
from sendgo_django import client

# 텍스트형
client.friendtalk.send(
    content="안녕하세요! 7월 한정 특가 이벤트를 확인해보세요.",
    contacts=[{"contact": "01012345678"}],
)
```

### SMS / LMS / MMS

```python
from sendgo_django import client

# SMS (90자 이하)
client.sms.send_sms(
    content="[Sendgo] 인증번호: 123456 (5분 이내 입력)",
    contacts=[{"contact": "01012345678"}],
)
```

---

## 서비스 클래스 패턴

```python
# app/services.py
import logging

from sendgo import SendgoError
from sendgo_django import client

logger = logging.getLogger(__name__)


class NotificationService:
    """알림 발송 로직을 캡슐화한 서비스 클래스."""

    def send_order_confirm(self, phone: str, order_no: str, amount: int) -> None:
        client.alimtalk.send(
            template_code="ORDER_CONFIRM_001",
            contacts=[{"contact": phone, "var1": order_no, "var2": f"{amount:,}원"}],
        )

    def send_verification_code(self, phone: str, code: str) -> None:
        try:
            client.alimtalk.send(
                template_code="VERIFY_CODE_001",
                contacts=[{"contact": phone, "var1": code}],
            )
        except SendgoError:
            logger.exception("Sendgo 인증번호 발송 실패")
            raise
```

---

## 예외 처리

```python
from sendgo import SendgoError
from sendgo_django import client

try:
    client.alimtalk.send(
        template_code="ORDER_CONFIRM_001",
        contacts=[{"contact": "01012345678", "var1": "ORD-001"}],
    )
except SendgoError as e:
    logger.error("Sendgo 발송 실패: %s", e)
```

---

## 설정 옵션

`settings.SENDGO` 딕셔너리 키:

| 키 | 필수 | 기본값 | 설명 |
|----|------|--------|------|
| `ACCESS_KEY` | ✅ | — | Sendgo 액세스 키 |
| `SECRET_KEY` | ✅ | — | Sendgo 시크릿 키 |
| `KAKAO_SENDER_KEY` | | `None` | 카카오 발신프로필 키 |
| `SMS_SENDER_KEY` | | `None` | SMS 발신자 키 |
| `API_VERSION` | | `"v2"` | API 버전 |
| `BASE_URL` | | `"https://sendgo.io"` | API 기본 URL |

`ACCESS_KEY` 또는 `SECRET_KEY`가 없으면 클라이언트 생성 시 `django.core.exceptions.ImproperlyConfigured`가 발생합니다.

---

## 자주 묻는 질문 (FAQ)

**Q. `sendgo-python`과의 차이는 무엇인가요?**
A. `sendgo-python`은 프레임워크 독립적인 순수 Python 코어 패키지입니다. `sendgo-django`는 이를 확장해 `settings.SENDGO` 설정 바인딩, 지연 로딩 프록시, AppConfig 통합을 추가합니다.

**Q. 설정 없이 임포트하면 오류가 나나요?**
A. 아니요. `client`는 지연 프록시이므로 임포트만으로는 오류가 없고, 실제 사용(속성 접근) 시점에 설정을 검증합니다.

**Q. 테스트 시 클라이언트를 초기화하려면?**
A. `sendgo_django.conf.reset()`을 호출하면 메모이즈된 클라이언트가 초기화됩니다.

**Q. Django 4.2, 5.x를 지원하나요?**
A. 네, `Django>=4.2`를 지원합니다.

---

## 관련 패키지

| 언어/프레임워크 | 패키지 | GitHub |
|----------------|--------|--------|
| Python (순수) | `sendgo-python` | [python](https://github.com/send-go/python) |
| Laravel | `sendgo/laravel` | [laravel](https://github.com/send-go/laravel) |
| Spring Boot | `io.sendgo:sendgo-spring` | [spring](https://github.com/send-go/spring) |
| Node.js | `@sendgo/node` | [node](https://github.com/send-go/node) |
| 전체 목록 | — | [send-go GitHub 조직](https://github.com/send-go) |

---

## 브랜드메시지 · 짧은 URL

이 패키지는 코어(`sendgo-python`)의 클라이언트를 그대로 노출하므로, 코어에 있는 채널이
모두 그대로 쓸 수 있습니다. 두 기능 모두 **v2 전용**입니다.

| 기능 | 접근 |
|------|------|
| 카카오 브랜드메시지 (친구톡의 후속 채널) | `client.brand_message` |
| 짧은 URL (단축 + 클릭 반응 분석) | `client.short_url` |

브랜드메시지는 채널 친구가 아닌 수신자에게도 보낼 수 있고(`targeting` = `N`),
수신 동의한 전체 채널 친구에게 동보 발송할 수도 있습니다(`targeting` = `F`).

짧은 URL 은 메시지 본문의 링크를 줄이고 클릭 반응(일별 추이·디바이스·유입경로·국가)을
집계합니다.

사용 예시와 파라미터는 [코어 README](https://github.com/send-go) 와
[SDK 가이드](https://sendgo.io/ko/sdk) 를 참고하세요.

## 변경 사항

### 1.1.0 (2026-08-11)

- 브랜드메시지·짧은 URL 접근 방법 문서화 (코어를 그대로 노출)

## 라이선스

MIT License © 2026 [Sendgo](https://sendgo.io)

---

*키워드: 카카오 알림톡 Django, 카카오 친구톡 Django, SMS 발송 Django, 알림톡 Django 패키지, Django 카카오 API 연동, Sendgo Django SDK*
