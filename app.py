# ============================================================
#  📜 AI 교과서 속 인물 인터뷰 광장
#  파일명: app.py
#  실행 방법: streamlit run app.py
#  필요 패키지: pip install streamlit anthropic
#  API: 충남대학교 AI 포털 (Mindlogic Gateway)
# ============================================================

import streamlit as st
import anthropic
from datetime import datetime

# ── 페이지 기본 설정 ─────────────────────────────────────────
st.set_page_config(
    page_title="📜 AI 교과서 속 인물 인터뷰 광장",
    page_icon="📜",
    layout="wide",
)

# ── 커스텀 CSS ───────────────────────────────────────────────
st.markdown("""
<style>
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a1a2e 0%, #16213e 100%);
    }
    [data-testid="stSidebar"] * { color: #e0e0e0 !important; }
    div[data-testid="stRadio"] label {
        font-size: 1.05rem !important;
        padding: 6px 0 !important;
    }
    .report-box {
        background: #f8f4e8;
        border: 2px solid #c9a84c;
        border-radius: 12px;
        padding: 1.5rem 2rem;
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
CHARACTERS = {
    "⚔️ 이순신 장군": {
        "emoji": "⚔️",
        "era": "조선 선조 시대 (임진왜란, 1592~1598)",
        "intro": "임진왜란을 승리로 이끈 조선의 명장",
        "system_prompt": """당신은 조선 시대의 명장 이순신 장군입니다.
임진왜란(1592~1598)이 한창인 시대를 배경으로 학생과 대화합니다.

말투: 엄숙하고 진중하며 나라와 백성에 대한 깊은 책임감이 느껴집니다.
"그대의 물음이 가볍지 않소이다.", "이 몸은 오직 나라를 위해..." 같은 표현을 씁니다.
1인칭은 "나" 또는 "이 몸"을 사용합니다.

지식 범위: 거북선, 한산도 대첩, 명량 해전, 노량 해전, 난중일기, 임진왜란 흐름, 조선 수군 전략.

답변은 3~5문장으로 간결하되 깊이 있게. 역사적 사실에 기반하고, 오직 이순신 장군으로만 답하세요.""",
    },
    "📚 세종대왕": {
        "emoji": "📚",
        "era": "조선 세종 시대 (훈민정음 창제, 1443년 전후)",
        "intro": "훈민정음을 창제한 조선 제4대 임금",
        "system_prompt": """당신은 조선의 제4대 임금, 세종대왕입니다.
훈민정음을 창제하고 반포한 시기(1443~1446년)를 배경으로 학생과 대화합니다.

말투: 온화하고 따뜻하며 백성을 진심으로 사랑하는 어진 왕.
"그것은 참으로 좋은 물음이로다.", "짐이 글자를 만든 것은 오직 백성을 위함이니..."
1인칭은 "짐" 또는 "과인"을 사용합니다.

지식 범위: 훈민정음 창제 동기와 원리, 집현전, 측우기·앙부일구·자격루, 농업 장려, 조세 개혁.

답변은 3~5문장으로 간결하되 깊이 있게. 오직 세종대왕으로만 답하세요.""",
    },
    "🌸 유관순 열사": {
        "emoji": "🌸",
        "era": "일제강점기 (3.1 운동, 1919년)",
        "intro": "3.1 운동을 이끈 독립운동가 (당시 17세)",
        "system_prompt": """당신은 독립운동가 유관순 열사입니다.
1919년 3.1 운동 당시 17세의 유관순으로서 학생과 대화합니다.

말투: 당차고 열정적이며 독립에 대한 굳은 의지가 느껴집니다.
"우리도 할 수 있어요!", "두렵지 않았다고 하면 거짓말이겠죠. 하지만 옳은 일이니까요."
1인칭은 "저" 또는 "나"를 사용합니다.

지식 범위: 3.1 운동 배경, 이화학당 생활, 아우내 장터 만세운동(1919년 4월 1일), 서대문 형무소, 순국(1920년).

답변은 3~5문장으로 간결하되 감동적으로. 오직 유관순 열사로만 답하세요.""",
    },
}


# ── 충남대 AI 포털 클라이언트 초기화 ────────────────────────
# Anthropic SDK를 그대로 사용하되, base_url만 충남대 포털 주소로 변경합니다.
try:
    client = anthropic.Anthropic(
        api_key=st.secrets["CNU_API_KEY"],
        base_url="https://factchat-cloud.mindlogic.ai/v1/gateway/claude",
    )
except Exception:
    st.error("⚠️ API 키가 설정되지 않았습니다. `.streamlit/secrets.toml` 파일에 `CNU_API_KEY`를 입력해 주세요.")
    st.stop()


def get_ai_response(system_prompt: str, chat_history: list, user_message: str) -> str:
    """충남대 AI 포털을 통해 Claude 응답을 생성합니다."""
    messages = []
    for msg in chat_history:
        messages.append({
            "role": msg["role"],
            "content": msg["content"]
        })
    messages.append({"role": "user", "content": user_message})

    response = client.messages.create(
        model="claude-sonnet-4-6",   # 충남대 포털에서 제공하는 Claude 4.6 Sonnet
        max_tokens=1000,
        system=system_prompt,
        messages=messages,
    )
    return response.content[0].text


def generate_report(character_name: str, chat_history: list, student_name: str) -> str:
    """대화 기록을 바탕으로 수행평가용 보고서를 생성합니다."""
    conversation_text = "\n".join(
        [f"{'학생' if m['role'] == 'user' else character_name}: {m['content']}"
         for m in chat_history]
    )

    report_prompt = f"""아래는 학생 '{student_name}'이(가) '{character_name}'과(와) 나눈 인터뷰 대화입니다.

=== 대화 내용 ===
{conversation_text}
=================

위 대화를 분석하여 수행평가 보고서를 한국어로 작성해 주세요.
마크다운 없이 순수 텍스트로만 출력하세요.

---
[수행평가 인터뷰 보고서]

작성일: {datetime.now().strftime('%Y년 %m월 %d일')}
학습자 이름: {student_name}
인터뷰 인물: {character_name}

▶ 주요 대화 요약
(학생이 질문한 핵심 주제 3~5가지와 인물의 답변 핵심을 간략히 정리)

▶ 이 인물에게 배운 점
(이 인터뷰를 통해 역사적·인간적으로 배울 수 있는 교훈 2~3가지를 구체적으로 서술)

▶ 인상 깊은 한마디
(인터뷰에서 가장 인상 깊었던 인물의 말 한 문장을 인용하고, 그 이유를 한 줄로 설명)
---"""

    response = client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=1000,
        messages=[{"role": "user", "content": report_prompt}],
    )
    return response.content[0].text


# ── 세션 상태 초기화 ─────────────────────────────────────────
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "current_character" not in st.session_state:
    st.session_state.current_character = None
if "report_text" not in st.session_state:
    st.session_state.report_text = None
if "student_name" not in st.session_state:
    st.session_state.student_name = ""


# ── 사이드바 구성 ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 📜 인물 인터뷰 광장")
    st.markdown("역사 속 인물과 직접 대화해 보세요!")
    st.divider()

    student_name = st.text_input(
        "👤 내 이름 입력",
        placeholder="예: 홍길동",
        value=st.session_state.student_name,
    )
    if student_name:
        st.session_state.student_name = student_name

    st.divider()
    st.markdown("**🏛️ 대화할 인물 선택**")
    character_options = list(CHARACTERS.keys())
    selected_char = st.radio(
        label="인물 선택",
        options=character_options,
        label_visibility="collapsed",
    )

    if selected_char != st.session_state.current_character:
        st.session_state.current_character = selected_char
        st.session_state.chat_history = []
        st.session_state.report_text = None

    char_data = CHARACTERS[selected_char]
    st.divider()
    st.markdown(f"**{char_data['emoji']} {selected_char.split(' ', 1)[1]}**")
    st.caption(f"📅 {char_data['era']}")
    st.caption(f"💡 {char_data['intro']}")

    st.divider()
    if st.button("🔄 대화 초기화", use_container_width=True):
        st.session_state.chat_history = []
        st.session_state.report_text = None
        st.rerun()

    st.markdown("---")
    st.caption("Powered by 충남대학교 AI 포털")


# ── 메인 화면 ────────────────────────────────────────────────
st.title("📜 AI 교과서 속 인물 인터뷰 광장")
st.markdown(
    f"**현재 대화 상대:** {selected_char} &nbsp;|&nbsp; "
    f"**시대 배경:** {char_data['era']}"
)
st.divider()

if not st.session_state.chat_history:
    st.info(
        f"👋 **{selected_char}**과(와)의 인터뷰를 시작해 보세요!\n\n"
        "예시 질문:\n"
        "- 가장 어려웠던 순간은 언제였나요?\n"
        "- 그 결정을 내리게 된 이유가 무엇인가요?\n"
        "- 지금의 우리에게 전하고 싶은 말이 있나요?",
        icon="💬"
    )

for message in st.session_state.chat_history:
    if message["role"] == "user":
        with st.chat_message("user"):
            st.write(message["content"])
    else:
        with st.chat_message("assistant", avatar=char_data["emoji"]):
            st.write(message["content"])

user_input = st.chat_input(f"{selected_char}에게 질문해 보세요...")

if user_input:
    with st.chat_message("user"):
        st.write(user_input)

    with st.chat_message("assistant", avatar=char_data["emoji"]):
        with st.spinner(f"{selected_char}이(가) 답변 중..."):
            try:
                response = get_ai_response(
                    system_prompt=char_data["system_prompt"],
                    chat_history=st.session_state.chat_history,
                    user_message=user_input,
                )
                st.write(response)
                st.session_state.chat_history.append({"role": "user", "content": user_input})
                st.session_state.chat_history.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"응답 생성 중 오류가 발생했습니다: {e}")

# ── 보고서 생성 섹션 ──────────────────────────────────────────
st.divider()
st.markdown("### 📋 수행평가 보고서 생성")

col1, col2 = st.columns([2, 1])
with col1:
    st.caption("지금까지의 대화를 AI가 분석하여 수행평가용 보고서를 자동 생성합니다.")
with col2:
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

if st.session_state.report_text:
    st.markdown("---")
    st.markdown("#### 📄 생성된 보고서")
    st.markdown(
        f'<div class="report-box">'
        f'<div class="report-title">🏛️ 역사 인물 인터뷰 수행평가 보고서</div>'
        f'{st.session_state.report_text}'
        f'</div>',
        unsafe_allow_html=True,
    )
    st.download_button(
        label="⬇️ 보고서 텍스트 파일 다운로드",
        data=st.session_state.report_text.encode("utf-8"),
        file_name=f"인터뷰보고서_{st.session_state.student_name}_{selected_char[:5]}.txt",
        mime="text/plain",
    )
