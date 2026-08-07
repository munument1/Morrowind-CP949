# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

> [!WARNING]
> 현재 **Pre-release / 런타임 회귀 테스트 단계**입니다. CP949 한글 렌더링과 초기 compiled `Say` 방식은 실제 Classic 게임에서 동작을 확인했습니다. 현재 후보인 **v1.0.7-rc6 Classic CP949 전체 통합판은 정적 검증 PASS이며, Classic 전체 회귀 테스트는 아직 진행 중**입니다.

## 현재 후보: v1.0.7-rc6

기준 소스는 **Morrowind Korean ReTranslation v1.0.7-rc6 MRK WINDOWS SAFE**입니다.

RC6 OpenMW 소스에서 현재 실게임으로 확인된 토픽 표본:

- `금화 되찾기` 링크
- `파르고스의 은닉처` 링크 및 후속 선택지
- `그가 화내는` → `그가 화내는 걸 봤다` 링크

이 세 항목은 RC6 소스 측 런타임 확인입니다. **Classic RC6 전체 통합판의 동일 경로는 별도 회귀 테스트 대상**입니다.

### RC6 MRK 감사

RC6 `.mrk`는 Windows-safe 기준으로 다시 전수 감사했습니다.

- MRK: **373행**
- `0x1A`: **0**
- 중복 topic key: **0**
- 중복 keyword: **0**
- stale keyword: **0**
- 현재 ESP의 DIAL에 대응하지 않는 MRK key: **0**

MRK에 안전하게 넣기 어려웠던 13개 토픽은 MRK에서 제거했습니다. 대신 검수된 **INFO 응답 26개**에 현재 한국어 `DIAL NAME`이 실제 문구로 직접 나타나도록 수정하여 기본 인라인 토픽 링크 경로를 사용합니다. 별도 `AddTopic` 땜질은 추가하지 않았습니다.

RC4 → RC6 독립 차분에서도 레코드 수는 동일하고, 달라진 ESP 레코드는 **INFO 29개뿐이며 전부 `NAME` 응답문만 변경**됐습니다. SCPT 238개는 RC4와 바이트 단위로 동일하고 `CELL=0`, `PGRD=0`입니다.

## Classic CP949 RC6 빌드

Classic 변환에서는 일반 표시 문자열을 CP949로 바꾸는 것 외에, 번역 `SCTX`를 Classic 엔진이 시작 시 다시 컴파일하지 않도록 공식 마스터의 compiled `SCDT`를 기준으로 스크립트를 재구성합니다.

현재 RC6 Classic 빌드의 정적 검증 결과:

- compiled SCPT: **236개**
- compiled `MessageBox` 본문: **413개**
- `MessageBox` 버튼: **359개**
- compiled `AddTopic`: **105개**
- scripted `Say`: **128개**
- `FNAM` 32바이트 초과 처리: **33건**
- Voice INFO의 `ANAM="Wilderness"` 문제 조건 제거, INFO 자체는 유지
- 프로케수스 INFO: **1개 유지**
- 프로케수스 기술 필터: `ANAM = Seyda Neen, Census and Excise Office`
- Classic MRK: **373행**, `0x1A/중복/stale = 0`
- 출력 SCPT: `SCDT` 포함, `SCTX` 없음
- 정적 검증: **PASS**

스크립트는 실제 로드 순서와 같은

```text
Morrowind.esm -> Tribunal.esm -> Bloodmoon.esm
```

순서에서 마지막 공식 정의를 기준으로 합니다. 따라서 `CharGen_ring_keley`, `CavernIncarnateDoor`, `VampireCheck` 같은 확장팩 override도 보존합니다.

## Pre-release

현재 테스트 대상 태그:

```text
v1.0.7-rc6-classic-cp949-pre1
```

RC4 Pre-release는 비교/회귀 bisect용으로 그대로 남겨 둡니다. RC6은 별도 태그로 배포합니다.

현재 RC6 Classic 산출물:

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949_MO2.zip
```

이 ZIP에는 **ESP / MRK / README만** 들어가며 Bethesda 실행 파일, 게임 원본 ESM, 폰트 바이너리는 포함하지 않습니다.

## SHA-256

RC6 OpenMW source ZIP:

```text
9bfe99f9e296c692ba15cee9540cc9de193d49dad6b5421a31a642da62c237f4
```

RC6 source ESP:

```text
26da6c578d7136eb0e12f63d4e2d326cef2c10d7e4a148684c65136f753052e2
```

RC6 source MRK:

```text
030bb6acb37f1d5718d0af7c4c49367f596dc95e7f75805113a5707bb69b675f
```

Classic RC6 ESP:

```text
d876e2fd60b84380a3bca4750033ac6a36f776e173f5f2476433c66e519a9762
```

Classic RC6 MRK:

```text
27bf3f214da101518829ec450a476f4d81e60553f2e778a16888e42713fcd0b2
```

Deterministic MO2 ZIP:

```text
f744692d151a65ff1718cbfaf858063aa7e4daaae2beefd05613b6af1b24eca2
```

자세한 검증은 [`validation/`](validation/)을 참고하세요.

## CP949 실행 파일 패치

Classic Morrowind는 UTF-8/Unicode 기반 게임이 아닙니다. 이 프로젝트에서는 MCP 일본어 로컬라이제이션 경로에 존재하는 DBCS 처리 코드를 조사해 CP949 lead/trail 범위를 처리하도록 수정합니다.

패처:

[`tools/patch_morrowind_cp949.py`](tools/patch_morrowind_cp949.py)

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

## 설치 개요

1. Morrowind GOTY 1.6.0.1820과 `Morrowind.esm`, `Tribunal.esm`, `Bloodmoon.esm`을 준비합니다.
2. 지원되는 MCP 상태의 자신의 `Morrowind.exe`에 CP949 패치를 적용합니다.
3. 이미 정상 동작이 확인된 Classic CP949 호환 폰트 구성을 사용합니다. **이 저장소는 폰트 바이너리를 배포하지 않습니다.**
4. RC6 MO2 ZIP을 설치합니다.
5. `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp`를 활성화합니다.
6. 이전 한국어 번역 ESP 시험판은 비활성화합니다.

## 우선 회귀 테스트

뒤쪽 퀘스트를 억지로 진행하기보다 초반에 바로 확인 가능한 항목을 우선합니다.

- 게임 시작 시 `Script in file ... compiled.` 경고가 새로 발생하지 않는지
- 지웁 및 시작부 경비병 `Say` 자막
- 시작부 `MessageBox` 본문/버튼
- 세이다 닌의 파르고스/흐리스카르/프로케수스 관련 토픽
- `금화 되찾기`
- `그가 화내는 걸 봤다`

뒤쪽 전사 길드/마법사 길드/Tribunal/Bloodmoon 사례는 자연스럽게 플레이가 진행되면서 추가 표본을 쌓습니다.

정적 PASS와 실제 게임 동작은 같은 의미가 아닙니다. 문제 보고 시 `Warnings.txt`, 발생 NPC/토픽, MO2 플러그인 순서, 사용 ESP SHA-256을 함께 남겨 주세요.

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM
- 폰트 바이너리

게임을 소유한 사용자가 자신의 파일에 패치를 적용하는 방식을 사용합니다.

## Status

**v1.0.7-rc6 / Pre-release / runtime regression testing**
