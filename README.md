# About Time

## 📌 연애 코칭 챗봇
**About Time**는 **Upstage sLLM : Sola** 를 이용하여 대화 상대에 대한 가상 페르소나를 생성하여 사용자의 연애 방향성을 코칭해 주는 챗봇 입니다. 채팅 평가, 상대방 성향 분석과 **Retrieval-Augmented Generation**를 통해 데이트 코스 및 맛집 추천 기능을 제공합니다.

## 🚀 사용 방법
1. API key 준비
- [Upstage AI](https://console.upstage.ai/)에서 Sola API key 발급
- [Google Cloud Platform](https://console.cloud.google.com/)에서 Google Search Engine API Key 발급
2. 설치

    프로젝트를 로컬에 복제하고 필요한 패키지를 설치합니다
    ```bash
    git clone https://github.com/246p/ABOUT_TIME ABOUT_TIME
    cd ABOUT_TIME
    python3 -m venv about_time_env
    source about_time_env/bin/activate
    pip3 install -r requirements.txt
    ```
3. API key 입력

    발급받은 API Key를 `config.py`에 입력합니다.

4. 실행:
    ``` bash
    streamlit run main.py --server.port 20242 --server.enableCORS=false --browser.gatherUsageStats=false
    ```
5. 접속

   `http://127.0.0.1:20242`

## 🛠️ 사용된 도구
- Upstage Sola : 모델 기반 대화 및 분석 기능 구현
- Google Search Engine : RAG를 위한 API Key 제공
- Python: 전반적인 애플리케이션 로직 및 API 연동
- Streamlit: 사용자 인터페이스 구성

## 👥 팀원 정보
| 이름     | 역할 | GitHub |  이메일 |
| -------- | ----------------- | ----------------------------------- | ------ |
| 김민준 | 팀장 | [246p](https://github.com/246p) | 0016kmj@u.sogang.ac.kr|
| 김우영 | RAG | [drew0523](https://github.com/drew0523) |  drew0523@sogang.ac.kr |
| 이경연 | Promporting, UI | [l0k0y](https://github.com/l0k0y) | joinme2000@sogang.ac.kr|

---
