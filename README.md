# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

> [!WARNING]
> 현재 **Pre-release / 런타임 회귀 테스트 단계**입니다. CP949 한글 렌더링과 초기 compiled `Say` 방식은 실제 Classic 게임에서 동작을 확인했습니다. 현재 후보인 **v1.0.7-rc6 Classic CP949 전체 통합판은 정적 검증 PASS이며, Classic 전체 회귀 테스트는 아직 진행 중**입니다.

## Classic에서 한글이 나오려면 세 가지가 모두 필요합니다

1. **CP949 대응 실행 파일** — `tools/patch_morrowind_cp949.py`
2. **CP949 bitmap font** — `tools/build_classic_cp949_fonts.py`
3. **CP949 번역 ESP** — 현재 RC6 Classic MO2 패키지

실행 파일 패치는 CP949 바이트를 올바른 DBCS 글리프 위치로 해석하게 만들 뿐입니다. 실제 한글 모양은 FNT/TEX bitmap font가 제공합니다. 따라서 **폰트가 없는 깨끗한 설치에서 번역 ZIP과 EXE 패처만 적용하면 한글이 정상 표시되지 않습니다.**

이 저장소는 폰트 바이너리를 배포하지 않습니다. 대신 사용자가 가진 원본 Morrowind 폰트와 사용자가 별도로 준비한 한국어 TTF에서 Classic용 FNT/TEX를 재현하는 빌더를 제공합니다.

자세한 절차: [`CLASSIC_FONT_SETUP.md`](CLASSIC_FONT_SETUP.md)

## 현재 후보: v1.0.7-rc6

기준 소스는 **Morrowind Korean ReTranslation v1.0.7-rc6 MRK WINDOWS SAFE**입니다.

RC6 OpenMW 소스에서 현재 실게임으로 확인된 토픽 표본:

- `금화 되찾기` 링크
- `파르고스의 은닉처` 링크 및 후속 선택지
- `그가 화내는` → `그가 화내는 걸 봤다` 링크

이 세 항목은 RC6 소스 측 런타임 확인입니다. **Classic RC6 전체 통합판의 동일 경로는 별도 회귀 테스트 대상**입니다.

### RC6 MRK 감사

- MRK: **373행**
- `0x1A`: **0**
- 중복 topic key: **0**
- 중복 keyword: **0**
- stale keyword: **0**
- 현재 ESP의 DIAL에 대응하지 않는 MRK key: **0**

MRK에 안전하게 넣기 어려웠던 13개 토픽은 MRK에서 제거하고, 검수된 **INFO 응답 26개**에 실제 한국어 `DIAL NAME`이 직접 나타나도록 수정했습니다. 별도 `AddTopic` 땜질은 추가하지 않았습니다.

RC4 → RC6 차분에서 레코드 수는 동일하며 변경된 ESP 레코드는 **INFO 29개뿐이고 전부 `NAME` 응답문만 변경**됐습니다. SCPT 238개는 RC4와 바이트 동일하고 `CELL=0`, `PGRD=0`입니다.

## Classic CP949 RC6 빌드

Classic 변환에서는 일반 표시 문자열을 CP949로 바꾸고, 번역 `SCTX`를 Classic 엔진이 시작 시 재컴파일하지 않도록 공식 마스터의 compiled `SCDT`를 기준으로 스크립트를 재구성합니다.

- compiled SCPT: **236개**
- compiled `MessageBox` 본문: **413개**
- `MessageBox` 버튼: **359개**
- compiled `AddTopic`: **105개**
- scripted `Say`: **128개**
- `FNAM` 32바이트 초과 처리: **33건**
- Voice INFO `ANAM="Wilderness"` 문제 조건 제거
- 프로케수스 INFO: **1개 유지**
- 프로케수스 기술 필터: `ANAM = Seyda Neen, Census and Excise Office`
- Classic MRK: **373행**, `0x1A/중복/stale = 0`
- 출력 SCPT: `SCDT` 포함, `SCTX` 없음
- 정적 검증: **PASS**

스크립트는 실제 로드 순서와 같은

```text
Morrowind.esm -> Tribunal.esm -> Bloodmoon.esm
```

순서에서 마지막 공식 정의를 기준으로 하므로 `CharGen_ring_keley`, `CavernIncarnateDoor`, `VampireCheck` 같은 확장팩 override도 보존합니다.

## CP949 실행 파일 패치

패처: [`tools/patch_morrowind_cp949.py`](tools/patch_morrowind_cp949.py)

지원 입력 SHA-256:

```text
8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5  MCP default
c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8  MCP Japanese localization enabled
```

기존 런타임 확인 Korean Pilot 출력 SHA-256:

```text
710196b98d1a4efa174aebb5539e14b36cff20d008dc1f0c0610ce099d06cf72
```

```bash
python tools/patch_morrowind_cp949.py Morrowind.exe Morrowind.MCP-Korean-Pilot.exe
```

## Classic CP949 폰트 생성

필요한 Python 패키지:

```bash
python -m pip install -r tools/requirements-fonts.txt
```

예시:

```bash
python tools/build_classic_cp949_fonts.py \
  --vanilla-fonts "C:/Games/Morrowind/Data Files/Fonts" \
  --ttf "C:/Fonts/KoreanFont.ttf" \
  --output "build/Classic_CP949_Fonts"
```

빌더는 원본 single-byte 글리프를 보존하고 2048×2048 TEX에 CP949용 8×11 DBCS grid를 추가하며, FNT `0xFF` slot을 실행 파일 패치가 사용하는 template으로 설정합니다. 현대 한글 11,172자 coverage와 대표 셀 위치를 검증하고 SHA-256 manifest를 생성합니다.

개발 환경에서 이 빌더의 네 FNT는 과거 런타임 확인 Pilot의 네 FNT와 **바이트 단위 동일**하게 재현됐습니다. TEX 픽셀은 사용자가 선택한 TTF에 따라 달라집니다.

## Pre-release

현재 테스트 대상 태그:

```text
v1.0.7-rc6-classic-cp949-pre1
```

현재 RC6 Classic 산출물:

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949_MO2.zip
```

이 ZIP에는 **ESP / MRK / README만** 들어 있으며 실행 파일과 폰트 바이너리는 포함하지 않습니다. 따라서 신규 설치자는 위의 EXE 패처와 폰트 빌더도 함께 사용해야 합니다.

## SHA-256

```text
9bfe99f9e296c692ba15cee9540cc9de193d49dad6b5421a31a642da62c237f4  RC6 OpenMW source ZIP
26da6c578d7136eb0e12f63d4e2d326cef2c10d7e4a148684c65136f753052e2  RC6 source ESP
030bb6acb37f1d5718d0af7c4c49367f596dc95e7f75805113a5707bb69b675f  RC6 source MRK
d876e2fd60b84380a3bca4750033ac6a36f776e173f5f2476433c66e519a9762  Classic RC6 ESP
27bf3f214da101518829ec450a476f4d81e60553f2e778a16888e42713fcd0b2  Classic RC6 MRK
f744692d151a65ff1718cbfaf858063aa7e4daaae2beefd05613b6af1b24eca2  Deterministic MO2 ZIP
```

자세한 검증은 [`validation/`](validation/)을 참고하세요.

## 설치 순서

1. Morrowind GOTY 1.6.0.1820과 `Morrowind.esm`, `Tribunal.esm`, `Bloodmoon.esm` 준비
2. 지원되는 MCP 상태의 자신의 `Morrowind.exe`에 CP949 패치 적용
3. `build_classic_cp949_fonts.py`로 CP949 bitmap font 생성 후 별도 MO2 모드로 설치
4. RC6 Classic MO2 ZIP 설치
5. `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp` 활성화
6. 이전 한국어 번역 ESP 시험판 비활성화

Classic 쪽에서는 `Morrowind.ini` 폰트 이름을 바꾸지 않는 것이 기준입니다.

## 우선 회귀 테스트

- 게임 시작 시 `Script in file ... compiled.` 경고 여부
- 지웁 및 시작부 경비병 `Say` 자막
- 시작부 `MessageBox` 본문/버튼
- 세이다 닌의 파르고스/흐리스카르/프로케수스 관련 토픽
- `금화 되찾기`
- `그가 화내는 걸 봤다`

뒤쪽 전사 길드/마법사 길드/Tribunal/Bloodmoon 사례는 자연스럽게 플레이가 진행되면서 추가 표본을 쌓습니다. 정적 PASS와 실제 게임 동작은 같은 의미가 아닙니다.

## OpenMW 폰트 파일명 호환성

OpenMW 쪽은 글로벌 기본 `MysticCards / DemonicLetters`와 Import Wizard 계승 `magic_cards_regular / daedric_font` 두 정상 경로가 있으므로 별도 alias 정책을 사용합니다. 자세한 내용은 [`OPENMW_FONT_COMPAT.md`](OPENMW_FONT_COMPAT.md)를 참고하세요.

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM
- 폰트 바이너리

## Status

**v1.0.7-rc6 / Pre-release / runtime regression testing**
