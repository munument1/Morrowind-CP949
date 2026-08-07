# Morrowind CP949 Korean Support

Classic **The Elder Scrolls III: Morrowind 1.6.0.1820**에서 한국어를 표시하고, OpenMW용 한국어 재번역 데이터를 Classic 엔진에서 사용할 수 있도록 변환하는 프로젝트입니다.

> [!WARNING]
> 현재 **RC / 회귀 테스트 단계**입니다. CP949 한글 렌더링과 초기 `compiled Say` 방식은 실제 게임에서 동작을 확인했지만, `v1.0.7-rc4` 전체 compiled-script 통합판은 정적 검증까지 완료된 상태이며 게임 내 회귀 테스트가 남아 있습니다.

## 현재 상태

| 항목 | 상태 |
| --- | --- |
| CP949 엔진 출력 | ✅ 게임 내 확인 |
| 한글 폰트 출력 | ✅ 게임 내 확인 |
| 시작부 scripted `Say` | ✅ 게임 내 확인 |
| `v1.0.7-rc4` 토픽 정적 감사 | ✅ 완료 |
| Classic CP949 일반 문자열 변환 | ✅ 정적 검증 PASS |
| Classic compiled `MessageBox` | ✅ 빌드/정적 검증 PASS, 런타임 회귀 테스트 필요 |
| Classic compiled `AddTopic` | ✅ 빌드/정적 검증 PASS, 런타임 회귀 테스트 필요 |
| 전체 translated scripted `Say` 128개 | ✅ 빌드/정적 검증 PASS |
| 최종 배포판 | 🚧 RC |

## 현재 배포 방식

현재 저장소에는 Bethesda 실행 파일, 게임 원본 ESM, 폰트 바이너리를 올리지 않습니다. Classic RC4 패키지는 [`tools/build_classic_cp949_rc4.py`](tools/build_classic_cp949_rc4.py)로 **사용자가 소유한 GOTY 마스터 파일에서 재현 가능**하게 만들었습니다.

런타임 회귀 테스트가 끝나면 사전 빌드 MO2 ZIP도 GitHub Releases에 게시하는 것을 목표로 합니다.

현재 정적 검증을 통과한 테스트 산출물의 파일명은 다음과 같습니다.

```text
Morrowind_Korean_ReTranslation_v1.0.7-rc4_Classic_CP949_MO2.zip
```

결정적(deterministic) ZIP SHA-256:

```text
1905b245c7d926cdc645dd0b369e4c56620119819ccee58251ee61b92f6e4aaa
```

이 ZIP에는 **ESP / MRK / README만** 들어가며 `Morrowind.exe`와 폰트 바이너리는 포함하지 않습니다.

## 기준 번역

Classic판은 **Morrowind Korean ReTranslation v1.0.7-rc4 MANUAL TOPIC CLOSURE**를 기준으로 생성했습니다.

RC4에서 보류되었던 36개 토픽 경로는 수동 검수로 닫혔고, 프로케수스 비텔리우스 관련 중복 INFO도 제거된 상태를 기준으로 합니다.

기준 RC4 ESP SHA-256:

```text
c83299ebc70877b61b945a5124c5b224eb758c1fdde32e4f97a3b2434bde2fa1
```

## Classic CP949 변환 내용

이번 RC4 Classic 빌드는 번역 ESP의 `SCTX`를 게임 시작 시 다시 컴파일시키지 않습니다. 대신 소유한 게임의 공식 `Morrowind.esm`, `Tribunal.esm`, `Bloodmoon.esm`에 들어 있는 컴파일된 `SCDT`를 기준으로 사용자 표시 문자열만 CP949로 재구성합니다.

핵심 처리 내용:

- 일반 표시 문자열 CP949 변환
- `FNAM` 32바이트 초과 33건 안전 축약
- Voice INFO의 문제 조건 `ANAM="Wilderness"` 제거, INFO 자체는 유지
- 프로케수스 중복 INFO 수정 유지
- 번역 스크립트 **236개**를 공식 compiled `SCDT`에서 재구성
- compiled `MessageBox` 본문 **413개**
- compiled `MessageBox` 버튼 **359개**
- compiled `AddTopic` **105개**
- translated scripted `Say` **128개**
- 출력 SCPT에는 `SCDT`만 유지하고 `SCTX`는 제거하여 소스 재컴파일 경고 방지
- `GetPCCell` 같은 기술용 ID/셀명은 공식 마스터 값을 유지
- RC4 `.mrk` 387행을 CP949로 변환

### 마스터 스크립트 우선순위

스크립트는 실제 게임 로드 순서와 같은

```text
Morrowind.esm -> Tribunal.esm -> Bloodmoon.esm
```

순서에서 **마지막 정의가 승리**하도록 처리합니다.

이 과정에서 이전 시험판의 중요한 오판도 하나 수정했습니다. `CavernIncarnateDoor`는 `Morrowind.esm` 버전만 보면 번역 소스의 `Say` 한 개가 없는 것처럼 보이지만, `Bloodmoon.esm`이 4개 `Say`를 가진 최종 스크립트로 덮어씁니다. 따라서 최종 기준에서는 translated `Say` **128개가 전부 1:1 대응**합니다.

같은 이유로 다음 확장팩 스크립트 변경도 보존합니다.

- `CharGen_ring_keley` -> Tribunal 최종 정의
- `CavernIncarnateDoor` -> Bloodmoon 최종 정의
- `VampireCheck` -> Bloodmoon 최종 정의

## 재현 빌드

필요한 입력:

- `v1.0.7-rc4 MANUAL TOPIC CLOSURE` ZIP
- 사용자가 소유한 `Morrowind.esm`
- `Tribunal.esm`
- `Bloodmoon.esm`
- Python 3

예시:

```bash
python tools/build_classic_cp949_rc4.py \
  --rc4 Morrowind_Korean_ReTranslation_v1.0.7-rc4_OpenMW_0.51.0_MANUAL_TOPIC_CLOSURE.zip \
  --morrowind Morrowind.esm \
  --tribunal Tribunal.esm \
  --bloodmoon Bloodmoon.esm \
  --output-dir build
```

검증에 사용한 마스터 SHA-256:

```text
5c3c8c2cbd20e25901b59b3ece33d36b7ef0e3d60ad8d11828bcc61a5ead1647  Morrowind.esm
2ace511f23cc2a9ddd5f3aa59c7919789b9378cf4b17c8ae3375dd6b782f3f2b  Tribunal.esm
bd27090d0e6ad4c1bf1abc83f1a2dac56fcc82cae7bfe8263c413fb301801357  Bloodmoon.esm
```

동일한 입력으로 빌더를 반복 실행해 ESP, MRK 및 ZIP 해시가 재현되는 것을 확인했습니다.

## 왜 CP949인가?

Classic Morrowind는 UTF-8/Unicode 기반 게임이 아닙니다. 기존 OpenMW용 한국어 번역은 레거시 `.fnt` 글리프를 조합하는 별도 바이트 표현을 사용하므로 Classic 엔진에 그대로 넣을 수 없습니다.

이 프로젝트에서는 MCP 일본어 로컬라이제이션 경로에 존재하는 DBCS 처리 코드를 조사해 CP949 lead/trail 범위를 처리하도록 수정했습니다. 사용자는 자신의 `Morrowind.exe`에 패치를 적용합니다.

패처:

[`tools/patch_morrowind_cp949.py`](tools/patch_morrowind_cp949.py)

지원 입력 SHA-256:

```text
8fe33fb11b6a682721e7456af78eefd228e8b60dc7c9f4253f89a361f8a4dfc5  MCP default
c3585b91741689057c18ff86a1c3381d47278cd1d81443d38ed3b179c2fa1cd8  MCP Japanese localization enabled
```

기존에 런타임 확인한 Korean Pilot 출력 SHA-256:

```text
710196b98d1a4efa174aebb5539e14b36cff20d008dc1f0c0610ce099d06cf72
```

실행 파일 패치 예시:

```bash
python tools/patch_morrowind_cp949.py Morrowind.exe Morrowind.MCP-Korean-Pilot.exe
```

## 설치 개요

1. Morrowind GOTY 1.6.0.1820과 `Morrowind.esm`, `Tribunal.esm`, `Bloodmoon.esm`을 준비합니다.
2. 지원되는 MCP 상태의 자신의 `Morrowind.exe`에 `tools/patch_morrowind_cp949.py`를 적용합니다.
3. Classic Morrowind에서 CP949를 표시할 수 있는 호환 폰트 구성을 준비합니다. **이 저장소는 폰트 바이너리를 배포하지 않습니다.**
4. 빌더로 생성한 MO2 ZIP을 설치합니다.
5. `Morrowind_Korean_ReTranslation_v1.0.7-rc4_Classic_CP949.esp`를 활성화합니다.
6. 이전 한국어 번역 ESP 시험판은 비활성화합니다.

## scripted `Say`, `MessageBox`, `AddTopic`

Morrowind의 모든 표시 문자열이 `DIAL / INFO`에 있는 것은 아닙니다. 시작 시 지웁과 경비병의 음성 자막은 MWScript의 `Say` 안에 들어 있고, 튜토리얼 문구 등은 `MessageBox`, 일부 토픽 해금은 `AddTopic`에 들어 있습니다.

Classic에서 번역 `SCTX`를 그대로 넣으면 게임이 로드할 때 스크립트를 재컴파일하며 경고가 발생할 수 있습니다. 이 프로젝트는 공식 마스터의 compiled bytecode에서 문자열 인수만 교체합니다.

확인한 대표 형식은 다음과 같습니다.

```text
Say:
1B 11 + sound-path length + sound path + uint16 subtitle length + subtitle bytes

AddTopic:
22 10 + uint8 topic length + topic bytes

MessageBox:
00 10 + uint16 message length + message bytes + format args/buttons
```

변환 후 `SCHD`의 compiled-data 크기도 새 `SCDT` 길이에 맞게 다시 기록합니다.

## Dialogue / Topic 감사

이 번역 작업에서 중요한 문제 중 하나는 `INFO INAM`이 플러그인 전체에서 절대적으로 고유하지 않다는 점이었습니다. 서로 다른 `DIAL` 아래에서 같은 `INAM`이 재사용될 수 있으므로 Dialogue INFO는 최소한 다음 관계로 식별해야 합니다.

```text
(parent DIAL, INFO INAM)
```

RC4는 이 구조 문제와 후속 수동 토픽 감사를 반영한 현재 기준본입니다.

## 회귀 테스트가 필요한 항목

RC4 Classic 전체 통합판에서는 다음 경로를 우선 확인할 예정입니다.

- 새 게임 시작부 지웁 / 경비병 `Say`
- 시작부 튜토리얼 `MessageBox`
- 흐리스카르 관련 토픽
- 프로케수스 비텔리우스 살해 토픽
- 전사 길드 / 마법사 길드 토픽
- 대장 찾기 관련 토픽
- Tribunal / Bloodmoon scripted dialogue

정적 검증이 PASS여도 실제 게임 테스트와 동일한 의미는 아닙니다.

## 현재 빌드 해시

Classic ESP:

```text
c8078451320dbe77c87463d7ead3a8f3b929ba5cc8460ee4a83cd9d8af8314c3
```

Classic MRK:

```text
60be56aff5bd7954e062df812a367be679a924907d8e45620c9a46de97787fe4
```

Deterministic MO2 ZIP:

```text
1905b245c7d926cdc645dd0b369e4c56620119819ccee58251ee61b92f6e4aaa
```

자세한 정적 검증 결과는 [`validation/`](validation/)을 참고하세요.

## 저장소에 포함하지 않는 것

- Bethesda의 `Morrowind.exe` 원본/수정본
- 게임 원본 ESM
- 폰트 바이너리

게임을 소유한 사용자가 자신의 파일에 패치를 적용하는 방식을 사용합니다.

## Status

**Release Candidate / runtime regression testing**
