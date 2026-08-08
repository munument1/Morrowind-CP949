# Classic Morrowind CP949 폰트 설치

Classic Morrowind에서 CP949 한국어를 실제로 표시하려면 **CP949 글리프가 들어 있는 bitmap font**가 필요합니다. 실행 파일 패치는 CP949 바이트를 해석할 뿐이고 실제 글자 모양은 FNT/TEX가 제공합니다.

## 일반 사용자 권장 방식

일반 사용자는 폰트 생성 스크립트를 실행하지 않는 것을 기본으로 합니다. 정식 배포에서는 사전 생성된 Classic CP949 폰트팩을 Release asset으로 제공하고, 사용자는 그 ZIP을 MO2로 설치하면 됩니다.

권장 asset 이름:

```text
Morrowind_CP949_Classic_Fonts.zip
```

권장 구조:

```text
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
```

Classic 쪽에서는 기존 `Morrowind.ini`의 폰트 이름을 바꾸지 않는 것을 기준으로 합니다. 패키지가 원래 경로에 호환 FNT/TEX를 제공하도록 합니다.

## clean install에 필요한 것

1. CP949 대응 `Morrowind.exe`
2. 사전 생성 Classic CP949 폰트팩
3. `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp`가 들어 있는 번역 패키지

셋 중 폰트가 빠지면 엔진이 CP949 바이트를 처리하더라도 한글 글리프를 올바르게 표시할 수 없습니다.

## 현재 RC6 Pre-release 주의

Release asset 목록에 `Morrowind_CP949_Classic_Fonts.zip` 같은 사전 생성 폰트팩이 아직 없다면, 그 시점의 RC6 Pre-release는 기존 테스트용 한글 폰트가 이미 설치된 환경에서는 사용할 수 있지만 **clean install 사용자용 배포는 아직 완결되지 않은 상태**입니다.

폰트팩이 Release에 추가되면 일반 사용자는 생성 도구 없이 그대로 설치하는 방식이 기준입니다.

## 재현·개발·커스텀 글꼴용 선택 도구

`tools/build_classic_cp949_fonts.py`는 일반 사용자 필수 단계가 아닙니다. 다음 용도로만 유지합니다.

- 배포 폰트팩 재현
- 개발 검증
- 다른 TTF로 커스텀 폰트 제작
- FNT/TEX 구조 실험

필요한 Python 패키지:

```bash
python -m pip install -r tools/requirements-fonts.txt
```

예시:

```bat
python tools\build_classic_cp949_fonts.py ^
  --vanilla-fonts "C:\Games\Morrowind\Data Files\Fonts" ^
  --ttf "C:\Fonts\KoreanFont.ttf" ^
  --output "build\Classic_CP949_Fonts"
```

빌더는 다음을 처리합니다.

- 원본 single-byte 글리프 atlas 보존
- TEX를 `2048 x 2048 RGBA`로 확장
- CP949 DBCS grid를 `y=512`부터 생성
- lead `0x81..0xFD`
- trail `0x41..0x5A`, `0x61..0x7A`, `0x81..0xFE`
- 셀 크기 `8 x 11`
- 원본 FNT UV를 2048 atlas에 맞게 재계산
- FNT glyph slot `0xFF`를 CP949 DBCS template으로 설정
- 현대 한글 11,172자 coverage 검증
- 생성 파일 SHA-256 manifest 작성

개발 환경에서 이 빌더로 생성한 네 FNT는 과거 런타임 확인 Pilot의 네 FNT와 **바이트 단위 동일**하게 재현됐습니다. TEX 픽셀은 선택한 TTF와 렌더러에 따라 달라질 수 있습니다.

## 설치

MO2 사용 시 사전 생성 폰트팩 ZIP을 별도 모드로 설치해 번역 모드와 함께 활성화합니다. 직접 설치한다면 기존 `Data Files/Fonts`의 동명 파일을 먼저 백업하세요.

일반 사용자 문서와 Release에서는 **사전 생성 폰트팩 설치가 기본**, 빌더는 **선택적 재현 도구**로 취급합니다.
