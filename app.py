# ============================================================
#  📜 AI 교과서 속 인물 인터뷰 광장
#  파일명: app.py
#  실행 방법: streamlit run app.py
#  필요 패키지: pip install streamlit google-generativeai
# ============================================================

import streamlit as st
import google.generativeai as genai
from datetime import datetime

# ── 페이지 기본 설정 ─────────────────────────────────────────
st.set_page_config(
    page_title="📜 AI 교과서 속 인물 인터뷰 광장",
    page_icon="📜",
    layout="wide",
)

# ── 커스텀 CSS (UI 폴리싱) ───────────────────────────────────
st.markdown("""
<style>
    /* 사이드바 배경 */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }

    /* 인물 선택 라디오 버튼 강조 */
    div[data-testid="stRadio"] label {
        font-size: 1.05rem !important;
        padding: 6px 0 !important;
    }

    /* 보고서 출력 박스 */
    .report-box {
        background: #f8f4e8;
        border: 2px solid #c9a84c;
        border-radius: 12px;
        padding: 1.5rem 2rem;
        font-family: 'Nanum Myeongjo', serif;
        color: #2c2c2c;
        line-height: 1.9;
        white-space: pre-wrap;
    }
    .report-title {
        font-size: 1.3rem;
        font-weight: bold;
        color: #7a4f00;
        margin-bottom: 1rem;
        border-bottom: 1px solid #c9a84c;
        padding-bottom: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# ── 인물 데이터 정의 ─────────────────────────────────────────
# 각 인물의 시스템 프롬프트와 소개 정보를 딕셔너리로 관리합니다.
CHARACTERS = {
    "⚔️ 이순신 장군": {
        "emoji": "⚔️",
        "era": "조선 선조 시대 (임진왜란, 1592~1598)",
        "intro": "임진왜란을 승리로 이끈 조선의 명장",
        "system_prompt": """당신은 조선 시대의 명장 이순신 장군입니다.
임진왜란(1592~1598)이 한창인 시대를 배경으로, 학생과 대화합니다.

[말투 지침]
- 엄숙하고 진중하며, 나라와 백성에 대한 깊은 책임감이 느껴지는 말투를 사용합니다.
- 고어(古語)를 약간 섞되, 현대 학생이 이해할 수 있는 수준을 유지합니다.
- 예: "그대의 물음이 가볍지 않소이다.", "나는 오직 나라를 위해 이 한 몸을 바칠 따름이오."
- 1인칭은 "나" 또는 "이 몸"을 사용합니다.

[지식 범위]
- 거북선 설계, 한산도 대첩, 명량 해전, 노량 해전 등 주요 전투
- 난중일기의 내용과 감정 (외로움, 나라 걱정, 어머니 그리움)
- 임진왜란의 전체적인 흐름과 왜군의 침략 배경
- 조선 수군의 전략과 지리적 이점 활용

[행동 지침]
- 역사적 사실에 기반하여 답변하되, 인물의 내면을 풍부하게 묘사합니다.
- 학생이 잘못된 역사적 사실을 말하면, 부드럽지만 단호하게 바로잡습니다.
- 답변은 3~6문장 내외로 간결하게, 그러나 깊이 있게 답합니다.
- 오직 이순신 장군의 역할만 수행하며, AI임을 밝히거나 캐릭터를 벗어나지 않습니다.""",
    },

    "📚 세종대왕": {
        "emoji": "📚",
        "era": "조선 세종 시대 (훈민정음 창제, 1443년 전후)",
        "intro": "훈민정음을 창제한 조선 제4대 임금",
        "system_prompt": """당신은 조선의 제4대 임금, 세종대왕입니다.
훈민정음을 창제하고 반포한 시기(1443~1446년)를 배경으로 학생과 대화합니다.

[말투 지침]
- 온화하고 따뜻하며, 백성을 진심으로 사랑하는 어진 왕의 말투를 사용합니다.
- 학문을 좋아하고 논리적이며, 상대방의 의견을 경청하는 모습을 보입니다.
- 예: "그것은 참으로 좋은 물음이로다.", "짐이 글자를 만든 것은 오직 백성을 위함이니..."
- 1인칭은 "짐(朕)" 또는 "과인(寡人)"을 사용합니다.

[지식 범위]
- 훈민정음 창제 동기 (백성의 문자 생활 불편함 해소)와 원리
- 집현전 학자들과의 협력 (성삼문, 박팽년 등)
- 과학 발명: 측우기, 앙부일구, 자격루 등
- 농업 장려, 조세 개혁, 음악 정리 등 민생 정책
- 당시 한자 위주의 지배층과 훈민정음 창제에 대한 반발

[행동 지침]
- 백성에 대한 사랑과 학문적 호기심을 자연스럽게 드러냅니다.
- 역사적 사실에 기반하되, 세종의 인간적인 면모도 함께 표현합니다.
- 답변은 3~6문장 내외로 간결하게, 그러나 깊이 있게 답합니다.
- 오직 세종대왕의 역할만 수행하며, AI임을 밝히거나 캐릭터를 벗어나지 않습니다.""",
    },

    "🌸 유관순 열사": {
        "emoji": "🌸",
        "era": "일제강점기 (3.1 운동, 1919년)",
        "intro": "3.1 운동을 이끈 독립운동가 (당시 17세)",
        "system_prompt": """당신은 독립운동가 유관순 열사입니다.
1919년 3.1 운동이 전국으로 번지던 시기, 아우내 장터 만세운동을 이끌었던 17세의 유관순으로서 학생과 대화합니다.

[말투 지침]
- 당차고 열정적이며, 독립에 대한 굳은 의지가 느껴지는 말투를 사용합니다.
- 또래 학생들에게 공감하는 밝고 진솔한 어조를 기본으로 합니다.
- 독립과 나라에 관한 이야기가 나오면 단호하고 비장해집니다.
- 예: "우리도 할 수 있어요! 나라를 되찾는 건 어른들만의 일이 아니에요.", "두렵지 않았다고 하면 거짓말이겠죠. 하지만 옳은 일이니까요."
- 1인칭은 "저" 또는 "나"를 사용합니다.

[지식 범위]
- 3.1 운동의 배경 (고종 황제 서거, 2.8 독립선언)
- 이화학당에서의 생활과 독립운동 참여 계기
- 아우내 장터 만세운동 (1919년 4월 1일)과 부모님의 순국
- 서대문 형무소 수감 생활과 고문, 1920년 순국
- 당시 일제 식민지 교육과 민족 차별의 현실

[행동 지침]
- 17세 소녀의 시각에서 느끼는 두려움과 용기를 솔직하게 표현합니다.
- 학생들이 역사를 단순 암기가 아닌 공감으로 느낄 수 있도록 생생하게 묘사합니다.
- 답변은 3~6문장 내외로 간결하게, 그러나 감동적으로 답합니다.
- 오직 유관순 열사의 역할만 수행하며, AI임을 밝히거나 캐릭터를 벗어나지 않습니다.""",
    },
}


# ── Gemini API 초기화 ─────────────────────────────────────────
# Streamlit Cloud의 secrets.toml에 GEMINI_API_KEY를 등록해야 합니다.
try:
    genai.configure(api_key=st.secrets["GEMINI_API_KEY"])
except Exception:
    st.error("⚠️ API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일에 `GEMINI_API_KEY`를 입력해 주세요.")
    st.stop()


def get_ai_response(system_prompt: str, chat_history: list, user_message: str) -> str:
    """
    Gemini API를 호출하여 AI 응답을 생성합니다.
    - system_prompt: 인물의 정체성을 정의하는 시스템 프롬프트
    - chat_history: 지금까지의 대화 기록 (role, content 형식)
    - user_message: 학생이 방금 입력한 메시지
    """
    model = genai.GenerativeModel(
        model_name="gemini-2.0-flash",      # 무료 티어에서 사용 가능한 빠른 모델
        system_instruction=system_prompt,   # 인물 역할 고정
    )

    # Gemini는 대화 기록을 'user'/'model' 형식으로 받습니다.
    gemini_history = []
    for msg in chat_history:
        role = "user" if msg["role"] == "user" else "model"
        gemini_history.append({"role": role, "parts": [msg["content"]]})

    # 대화 세션 생성 후 메시지 전송
    chat = model.start_chat(history=gemini_history)
    response = chat.send_message(user_message)
    return response.text


def generate_report(character_name: str, chat_history: list, student_name: str) -> str:
    """
    대화 기록을 바탕으로 수행평가용 인터뷰 보고서를 생성합니다.
    """
    # 대화 내용을 텍스트로 변환
    conversation_text = "\n".join(
        [f"{'학생' if m['role'] == 'user' else character_name}: {m['content']}"
         for m in chat_history]
    )

    report_prompt = f"""아래는 학생 '{student_name}'이(가) '{character_name}'과(와) 나눈 인터뷰 대화입니다.

=== 대화 내용 ===
{conversation_text}
=================

위 대화를 분석하여 다음 형식에 맞는 수행평가 보고서를 한국어로 작성해 주세요.
보고서는 아래 형식을 반드시 따르고, 마크다운 없이 순수 텍스트로 출력하세요.

---
[수행평가 인터뷰 보고서]

작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
학습자 이름: {student_name}
인터뷰 인물: {character_name}

▶ 주요 대화 요약
(학생이 질문한 핵심 주제 3~5가지와 인물의 답변 핵심을 간략히 정리)

▶ 이 인물에게 배운 점
(이 인터뷰를 통해 학생이 역사적으로, 인간적으로 배울 수 있는 교훈 2~3가지를 구체적으로 서술)

▶ 인상 깊은 한마디
(인터뷰에서 가장 인상 깊었던 인물의 말 한 문장을 인용하고, 그 이유를 한 줄로 설명)
---"""

    model = genai.GenerativeModel(model_name="gemini-2.0-flash")
    response = model.generate_content(report_prompt)
    return response.text


# ── 세션 상태 초기화 ─────────────────────────────────────────
# 페이지를 새로고침해도 대화 기록이 유지됩니다.
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []         # 대화 기록 저장
if "current_character" not in st.session_state:
    st.session_state.current_character = None  # 현재 선택된 인물
if "report_text" not in st.session_state:
    st.session_state.report_text = None        # 생성된 보고서 저장
if "student_name" not in st.session_state:
    st.session_state.student_name = ""


# ── 사이드바 구성 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📜 인물 인터뷰 광장")
    st.markdown("역사 속 인물과 직접 대화해 보세요!")
    st.divider()

    # 학생 이름 입력
    student_name = st.text_input(
        "👤 내 이름 입력",
        placeholder="예: 홍길동",
        value=st.session_state.student_name,
    )
    if student_name:
        st.session_state.student_name = student_name

    st.divider()

    # 인물 선택 라디오 버튼
    st.markdown("**🏛️ 대화할 인물 선택**")
    character_options = list(CHARACTERS.keys())
    selected_char = st.radio(
        label="인물 선택",
        options=character_options,
        label_visibility="collapsed",
    )

    # 인물이 바뀌면 대화 기록과 보고서를 초기화합니다.
    if selected_char != st.session_state.current_character:
        st.session_state.current_character = selected_char
        st.session_state.chat_history = []
        st.session_state.report_text = None

    # 선택된 인물 소개 표시
    char_data = CHARACTERS[selected_char]
    st.divider()
    st.markdown(f"**{char_data['emoji']} {selected_char.split(' ', 1)[1]}**")
    st.caption(f"📅 {char_data['era']}")
    st.caption(f"💡 {char_data['intro']}")

    st.divider()
    # 대화 초기화 버튼
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.report_text = None
        st.rerun()

    st.markdown("---")
    st.caption("Powered by Google Gemini API")


# ── 메인 화면 구성 ────────────────────────────────────────────
st.title("📜 AI 교과서 속 인물 인터뷰 광장")
st.markdown(
    f"**현재 대화 상대:** {selected_char} &nbsp;|&nbsp; "
    f"**시대 배경:** {char_data['era']}"
)
st.divider()

# 대화가 없을 때 안내 메시지 표시
if not st.session_state.chat_history:
    st.info(
        f"👋 안녕하세요! **{selected_char}**과(와)의 인터뷰를 시작해 보세요.\n\n"
        "예시 질문:\n"
        "- 가장 어려웠던 순간은 언제였나요?\n"
        "- 그 결정을 내리게 된 이유가 무엇인가요?\n"
        "- 지금의 우리에게 전하고 싶은 말이 있나요?",
        icon="💬"
    )

# ── 채팅 기록 출력 (Streamlit Chat UI) ──────────────────────
for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        # 인물의 이름과 아바타 이모지를 활용합니다.
        with st.chat_message("assistant", avatar=char_data["emoji"]):
            st.write(message["content"])

# ── 사용자 입력 처리 ─────────────────────────────────────────
user_input = st.chat_input(f"{selected_char}에게 질문해 보세요...")

if user_input:
    # 1) 학생 메시지를 화면에 즉시 표시하고 기록에 추가
    with st.chat_message("user"):
        st.write(user_input)
    st.session_state.chat_history.append({"role": "user", "content": user_input})

    # 2) AI 응답 생성 (로딩 스피너 표시)
    with st.chat_message("assistant", avatar=char_data["emoji"]):
        with st.spinner(f"{selected_char}이(가) 답변 중..."):
            try:
                response = get_ai_response(
                    system_prompt=char_data["system_prompt"],
                    # 마지막 메시지(방금 추가한 것)를 제외한 이전 기록을 넘깁니다.
                    chat_history=st.session_state.chat_history[:-1],
                    user_message=user_input,
                )
                st.write(response)
                st.session_state.chat_history.append(
                    {"role": "assistant", "content": response}
                )
            except Exception as e:
                st.error(f"응답 생성 중 오류가 발생했습니다: {e}")

# ── 인터뷰 보고서 생성 섹션 ──────────────────────────────────
st.divider()
st.markdown("### 📋 수행평가 보고서 생성")

col1, col2 = st.columns([2, 1])
with col1:
    st.caption("지금까지의 대화를 AI가 분석하여 수행평가용 보고서를 자동 생성합니다.")

with col2:
    # 대화가 4턴(사용자 2회 이상) 이상일 때만 버튼 활성화
    can_generate = len(st.session_state.chat_history) >= 4
    if st.button(
        "📝 인터뷰 보고서 생성",
        use_container_width=True,
        disabled=not can_generate,
        type="primary",
    ):
        if not st.session_state.student_name:
            st.warning("⚠️ 사이드바에서 먼저 이름을 입력해 주세요!")
        else:
            with st.spinner("AI가 보고서를 작성 중입니다..."):
                try:
                    st.session_state.report_text = generate_report(
                        character_name=selected_char,
                        chat_history=st.session_state.chat_history,
                        student_name=st.session_state.student_name,
                    )
                except Exception as e:
                    st.error(f"보고서 생성 중 오류: {e}")

    if not can_generate:
        st.caption("💡 최소 2번 이상 대화 후 생성 가능합니다.")

# 생성된 보고서 출력
if st.session_state.report_text:
    st.markdown("---")
    st.markdown("#### 📄 생성된 보고서")
    # 예쁜 박스 형태로 출력 (복사·캡처 용이)
    st.markdown(
        f'<div class="report-box">'
        f'<div class="report-title">🏛️ 역사 인물 인터뷰 수행평가 보고서</div>'
        f'{st.session_state.report_text}'
        f'</div>',
        unsafe_allow_html=True,
    )
    # 텍스트 파일로 다운로드 기능
    st.download_button(
        label="⬇️ 보고서 텍스트 파일 다운로드",
        data=st.session_state.report_text.encode("utf-8"),
        file_name=f"인터뷰보고서_{st.session_state.student_name}_{selected_char[:5]}.txt",
        mime="text/plain",
    )
