# Classic Morrowind CP949 폰트 생성

Classic Morrowind에서 CP949 한국어를 실제로 표시하려면 **실행 파일 패치와 별도로 CP949 글리프가 들어 있는 bitmap font가 필요**합니다.

현재 GitHub Pre-release의 번역 MO2 ZIP은 ESP/MRK/README만 포함하며 폰트 바이너리는 포함하지 않습니다. 따라서 깨끗한 설치에서는 폰트를 별도로 준비해야 합니다.

이 저장소의 `tools/build_classic_cp949_fonts.py`는 사용자가 가진 **원본 Morrowind bitmap font**와 사용자가 별도로 준비한 **한국어 TTF**를 입력으로 받아 Classic용 FNT/TEX를 생성합니다. 도구 자체에는 글꼴 데이터가 들어 있지 않습니다.

## 필요한 것

- Morrowind 1.6.0.1820의 원본 `Data Files/Fonts` 폴더
- 한국어 완성형 11,172자를 포함하는 TTF 한 개
- Python 3
- Pillow / fontTools

의존성 설치:

```bash
python -m pip install -r tools/requirements-fonts.txt
```

## 생성

Windows 예시:

```bat
python tools\build_classic_cp949_fonts.py ^
  --vanilla-fonts "C:\Games\Morrowind\Data Files\Fonts" ^
  --ttf "C:\Fonts\KoreanFont.ttf" ^
  --output "build\Classic_CP949_Fonts"
```

출력은 다음 구조로 만들어집니다.

```text
build/Classic_CP949_Fonts/
  Data Files/
    Fonts/
      Magic_Cards_Regular.fnt
      Magic_Cards_Regular_0_Lod_A.tex
      century_gothic_big.fnt
      century_gothic_big_0_Lod_A.tex
      century_gothic_font_regular.fnt
      century_gothic_font_regular_0_Lod_A.tex
      daedric_font.fnt
      Daedric_font_0_Lod_A.tex
  font_build_manifest.json
```

Windows 파일 시스템에서는 `Daedric_font_0_Lod_A.tex`의 대소문자는 문제가 되지 않습니다. 실제 TEX 이름은 각 원본 FNT 내부의 texture basename을 그대로 사용합니다.

## 빌더가 하는 일

- 원본 single-byte 글리프 atlas를 좌상단에 그대로 보존
- TEX를 `2048 x 2048 RGBA`로 확장
- CP949 DBCS grid를 `y=512`부터 생성
- lead `0x81..0xFD`
- trail `0x41..0x5A`, `0x61..0x7A`, `0x81..0xFE`
- 셀 크기 `8 x 11`
- 원본 FNT의 UV를 새 2048 atlas에 맞게 재계산
- FNT glyph slot `0xFF`를 CP949 DBCS template으로 설정
- `가`, `한`, `힝` 표본 위치와 현대 한글 11,172자 전체 coverage 검증
- 생성 파일 SHA-256을 `font_build_manifest.json`에 기록

`0xFF` template과 FNT UV 변환은 이전 런타임 확인 Pilot의 네 FNT와 **바이트 단위 동일하게 재현되는 것**을 개발 환경에서 확인했습니다. TEX의 픽셀 결과는 사용자가 선택한 TTF와 렌더러 버전에 따라 달라질 수 있습니다.

## 설치

가장 안전한 방법은 생성한 `Data Files/Fonts`를 별도 MO2 모드로 설치해 번역 모드와 함께 활성화하는 것입니다. 직접 설치한다면 기존 `Data Files/Fonts`의 동명 파일을 먼저 백업하세요.

Classic 쪽에서는 기존 `Morrowind.ini`의 폰트 이름을 바꿀 필요가 없습니다. 원래 사용하는 `magic_cards_regular`, `century_gothic_*`, `daedric_font` 경로에 호환 FNT/TEX를 제공하는 방식입니다.

## 전체 Classic 설치에 필요한 세 요소

1. `tools/patch_morrowind_cp949.py`로 만든 CP949 대응 `Morrowind.exe`
2. 이 문서의 폰트 빌더로 만든 CP949 bitmap font
3. `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp`가 들어 있는 번역 MO2 패키지

셋 중 폰트가 빠지면 엔진이 CP949 바이트를 처리하더라도 한글 글리프를 올바르게 표시할 수 없습니다.
