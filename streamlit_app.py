import streamlit as st
from openai import OpenAI

# 예시 장소 데이터
places = {
    "서울": [
        "서울숲 - 자연 속 산책과 놀이터",
        "키즈플라넷 삼성점 - 실내 놀이 공간",
        "국립과천과학관 - 어린이 체험전시"
    ],
    "부산": [
        "부산 어린이대공원 - 놀이기구와 동물원",
        "부산국립과학관 - 다양한 가족 체험",
        "해운대 키즈카페 리틀빅플레이"
    ],
    "대구": [
        "이월드 - 테마파크와 놀이기구",
        "대구수목원 - 자연 체험",
        "국립대구과학관 - 어린이 체험전시"
    ]
}

# 함수: 지역명 포함 여부 판단 & 추천
def check_for_region_and_reply(prompt):
    for region in places:
        if region in prompt:
            recs = places[region]
            return f"🔍 '{region}' 지역의 추천 장소입니다:\n" + "\n".join(f"- {r}" for r in recs)
    return None  # 지역명 없으면 None 반환

# Streamlit UI
st.title("👨‍👩‍👧 가족 나들이 장소 추천 챗봇")
st.write("지역명을 입력하면 가족이 놀기 좋은 장소를 추천해드려요!")

openai_api_key = st.text_input("OpenAI API Key", type="password")
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:
    client = OpenAI(api_key=openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("어디로 나들이 가고 싶으신가요?"):

        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 지역명 판단 먼저 시도
        region_reply = check_for_region_and_reply(prompt)

        if region_reply:
            with st.chat_message("assistant"):
                st.markdown(region_reply)
            st.session_state.messages.append({"role": "assistant", "content": region_reply})
        else:
            # OpenAI에게 전달
            stream = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ],
                stream=True,
            )
            with st.chat_message("assistant"):
                response = st.write_stream(stream)
            st.session_state.messages.append({"role": "assistant", "content": response})
