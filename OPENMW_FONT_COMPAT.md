# OpenMW 0.51 Font Compatibility — Import Wizard vs Default Config

RC7부터 OpenMW 패키지는 **사용자 `openmw.cfg`를 수정하지 않고** 두 정상적인 폰트 선택 경로를 모두 지원해야 합니다.

## 왜 두 경로가 모두 정상인가

OpenMW 0.51 공식 문서의 기본값은 다음과 같습니다.

```text
fallback=Fonts_Font_0,MysticCards
fallback=Fonts_Font_2,DemonicLetters
```

하지만 Installation / Import Wizard가 기존 `Morrowind.ini` 값을 사용자 `openmw.cfg`로 가져온 경우에는 비트맵 폰트 설정이 유지될 수 있습니다. 공식 문서의 예시는 다음 이름을 직접 사용합니다.

```text
fallback=Fonts_Font_0,magic_cards_regular
fallback=Fonts_Font_2,daedric_font
```

따라서 아래 두 설치 상태는 모두 정상입니다.

1. 사용자 `Fonts_Font_*` override가 없음 → `MysticCards` / `DemonicLetters`
2. Morrowind.ini Import 결과가 남아 있음 → `magic_cards_regular` / `daedric_font`

`Fonts_Font_1`은 OpenMW UI 폰트로 사용되지 않으므로 이 호환 처리 대상이 아닙니다.

공식 문서:
https://openmw.readthedocs.io/en/openmw-0.51.0/reference/modding/font.html

## RC6에서 놓친 부분

RC6 OpenMW 패키지는 다음 파일명을 제공합니다.

```text
Fonts/MysticCards.fnt
Fonts/DemonicLetters.fnt
```

따라서 글로벌 기본값을 쓰는 환경에서는 정상 동작하지만, Import Wizard가 만든 사용자 cfg가 `magic_cards_regular` / `daedric_font`를 요청하면 해당 이름의 FNT를 찾지 못합니다.

이 경우 사용자 설정이 잘못된 것이 아니라 **패키지가 정상적인 Import 환경을 놓친 것**으로 봅니다.

## RC7 패키징 규칙

RC7부터 아래 네 FNT 이름을 모두 제공하는 방향을 사용합니다.

```text
Fonts/MysticCards.fnt
Fonts/magic_cards_regular.fnt      # MysticCards.fnt와 바이트 동일 alias

Fonts/DemonicLetters.fnt
Fonts/daedric_font.fnt             # DemonicLetters.fnt와 바이트 동일 alias
```

alias는 Windows ZIP/MO2 호환성을 위해 symlink가 아니라 **실제 복사본**으로 만듭니다.

## TEX alias는 왜 필요하지 않은가

OpenMW FontLoader는 먼저 cfg가 요청한 이름으로 `Fonts/<requested>.fnt`를 찾습니다. 그러나 bitmap texture를 열 때는 **FNT 내부 헤더의 name 문자열**을 읽고 그 이름으로 `Fonts/<internal-name>.tex`를 엽니다.

OpenMW 소스의 동작은 요약하면 다음과 같습니다.

```text
requested cfg name
  -> Fonts/<requested>.fnt
  -> FNT 내부 name 읽기
  -> Fonts/<internal-name>.tex
```

현재 번역 패키지의 FNT 헤더 내부 이름은 각각 `MysticCards`, `DemonicLetters`이므로 alias FNT를 바이트 그대로 복사하면 다음 texture를 계속 사용합니다.

```text
MysticCards.tex
DemonicLetters.tex
```

따라서 RC7에서는 우선 **FNT 두 개만 alias 추가**하고 TEX는 중복 복사하지 않는 것을 기준으로 합니다.

OpenMW FontLoader source:
https://github.com/OpenMW/openmw/blob/master/components/fontloader/fontloader.cpp

## RC7 필수 런타임 매트릭스

패키지 배포 전 최소 아래 두 환경을 모두 확인합니다.

### A. OpenMW 기본 폰트 이름

```text
fallback=Fonts_Font_0,MysticCards
fallback=Fonts_Font_2,DemonicLetters
```

기대 결과: 한국어 UI 정상.

### B. Import Wizard / Morrowind.ini 계승 이름

```text
fallback=Fonts_Font_0,magic_cards_regular
fallback=Fonts_Font_2,daedric_font
```

기대 결과: **cfg 수정 없이** 한국어 UI 정상.

## 패키징 보조 도구

`tools/add_openmw_font_aliases.py`는 이미 존재하는 FNT 파일을 같은 디렉터리 안에 alias 이름으로 복사하고 SHA-256 동일성을 검증합니다.

이 도구는 폰트 바이너리를 포함하거나 생성하지 않습니다.
