# RC4 Classic CP949 런타임 회귀 테스트

정적 검증 PASS와 실제 게임 동작은 별개이므로, `v1.0.7-rc4_Classic_CP949`는 아래 항목을 우선 확인합니다.

## 테스트 환경

- Morrowind 1.6.0.1820
- Morrowind.esm / Tribunal.esm / Bloodmoon.esm 활성화
- 지원되는 MCP 기반 `Morrowind.exe`에 CP949 패치 적용
- 기존에 한글 표시가 확인된 Classic CP949 폰트 구성
- 이전 한국어 번역 ESP 시험판 비활성화
- `Morrowind_Korean_ReTranslation_v1.0.7-rc4_Classic_CP949.esp` 활성화

## 필수 회귀 테스트

- [ ] 게임 시작 시 `Script in file ... compiled.` 경고가 새로 발생하지 않는다.
- [ ] 새 게임에서 지웁의 첫 `Say` 자막이 한글로 표시된다.
- [ ] 배 안/부두 경비병의 시작부 `Say` 자막이 한글로 표시된다.
- [ ] 시작부 튜토리얼 `MessageBox` 본문이 한글로 표시된다.
- [ ] 시작부 `MessageBox` 버튼이 정상 표시되고 선택 가능하다.
- [ ] 흐리스카르 관련 토픽이 의도한 대화 경로에서 나타난다.
- [ ] 프로케수스 비텔리우스 살해 관련 토픽이 정상 동작한다.
- [ ] 프로케수스 관련 셀 조건 때문에 정상 대화가 누락되지 않는다.
- [ ] 전사 길드 토픽의 해금/연결이 정상이다.
- [ ] 마법사 길드 토픽의 해금/연결이 정상이다.
- [ ] 대장 찾기 관련 토픽의 해금/연결이 정상이다.
- [ ] Tribunal에서 scripted dialogue / AddTopic이 정상이다.
- [ ] Bloodmoon에서 scripted dialogue / AddTopic이 정상이다.
- [ ] 대화 중 새 토픽 링크가 깨진 문자열이나 영문 ID로 나타나지 않는다.
- [ ] 기존에 정상적으로 보이던 토픽이 사라지지 않는다.

## 문제 보고 시 같이 남기면 좋은 정보

- 발생 위치 / NPC 이름
- 클릭한 토픽과 직전 대화
- 새 게임인지 기존 세이브인지
- `Warnings.txt` 관련 부분
- MO2 플러그인 순서
- 사용한 ESP SHA-256

현재 RC4 Classic ESP의 기준 SHA-256:

```text
c8078451320dbe77c87463d7ead3a8f3b929ba5cc8460ee4a83cd9d8af8314c3
```

정적 검증 결과는 `validation/Morrowind_Korean_ReTranslation_v1.0.7-rc4_Classic_CP949_validation.json`을 참고하세요.
