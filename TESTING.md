# RC6 Classic CP949 런타임 회귀 테스트

정적 검증 PASS와 실제 게임 동작은 별개입니다. 현재 테스트 대상은 `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp`입니다.

## 이미 확인된 기반

Classic에서 이전 시험판으로 확인된 항목:

- CP949 한글 렌더링
- 시작부 compiled `Say` 한글 자막

OpenMW RC6 소스에서 실게임으로 확인된 토픽 표본:

- `금화 되찾기`
- `파르고스의 은닉처` 링크 및 후속 선택지
- `그가 화내는` → `그가 화내는 걸 봤다`

위 OpenMW 토픽 결과는 RC6 소스의 런타임 증거이며, Classic RC6에서도 다시 표본 확인합니다.

## 테스트 환경

- Morrowind 1.6.0.1820
- Morrowind.esm / Tribunal.esm / Bloodmoon.esm 활성화
- 지원되는 MCP 기반 `Morrowind.exe`에 CP949 패치 적용
- 기존에 한글 표시가 확인된 Classic CP949 폰트 구성
- 이전 한국어 번역 ESP 시험판 비활성화
- `Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949.esp` 활성화

## 우선 확인

- [ ] 게임 시작 시 `Script in file ... compiled.` 경고가 새로 발생하지 않는다.
- [ ] 새 게임에서 지웁의 첫 `Say` 자막이 한글로 표시된다.
- [ ] 배 안/부두 경비병의 시작부 `Say` 자막이 한글로 표시된다.
- [ ] 시작부 튜토리얼 `MessageBox` 본문이 한글로 표시된다.
- [ ] 시작부 `MessageBox` 버튼이 정상 표시되고 선택 가능하다.
- [ ] 파르고스/흐리스카르 관련 초반 토픽이 정상 연결된다.
- [ ] `금화 되찾기` 링크가 정상이다.
- [ ] `그가 화내는 걸 봤다` 링크가 정상이다.
- [ ] 프로케수스 비텔리우스 살해 관련 토픽이 정상 동작한다.
- [ ] 프로케수스 셀 조건 때문에 정상 대화가 누락되지 않는다.
- [ ] 대화 중 깨진 문자열이나 영문 내부 ID가 새 토픽 링크로 나타나지 않는다.
- [ ] 기존에 정상적으로 보이던 초반 토픽이 사라지지 않는다.

## 뒤쪽 표본

다음 항목은 해당 구간에 자연스럽게 도달하면 추가 확인합니다. 이 테스트만을 위해 플레이를 강제로 진행할 필요는 없습니다.

- [ ] 전사 길드 관련 직접 DIAL phrase 복구
- [ ] 마법사 길드 관련 토픽
- [ ] Tribunal scripted dialogue / AddTopic
- [ ] Bloodmoon scripted dialogue / AddTopic
- [ ] MRK에서 제외한 13개 직접 복구 토픽의 추가 런타임 표본

## 문제 보고 시

- 발생 위치 / NPC 이름
- 클릭한 토픽과 직전 대화
- 새 게임인지 기존 세이브인지
- `Warnings.txt` 관련 부분
- MO2 플러그인 순서
- 사용한 ESP SHA-256

현재 RC6 Classic ESP SHA-256:

```text
d876e2fd60b84380a3bca4750033ac6a36f776e173f5f2476433c66e519a9762
```

MO2 ZIP SHA-256:

```text
f744692d151a65ff1718cbfaf858063aa7e4daaae2beefd05613b6af1b24eca2
```

정적 검증:

- `validation/Morrowind_Korean_ReTranslation_v1.0.7-rc6_Classic_CP949_validation.json`
- `validation/Morrowind_v1.0.7-rc6_independent_structural_audit.json`
