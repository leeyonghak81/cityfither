import streamlit as st
from openai import OpenAI

# 지역명 리스트 (필요시 추가 가능)
known_regions = ["서울", "부산", "대구", "대전", "광주", "인천", "제주", "수원", "울산", "춘천"]

def extract_region(prompt):
    for region in known_regions:
        if region in prompt:
            return region
    return None

st.title("👨‍👩‍👧 가족 나들이 장소 추천 챗봇")
st.write("지역명을 입력하면, GPT가 그 지역에서 가족이 놀기 좋은 장소를 실시간으로 추천해줘요!")

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

        region = extract_region(prompt)
        if region:
            auto_prompt = f"{region}에서 가족이 함께 놀기 좋은 장소 3곳을 추천해줘. 장소 이름과 간단한 설명도 포함해줘."
            full_messages = [{"role": "system", "content": "너는 여행지 추천 전문가야. 장소 추천만 간단하고 명확하게 해줘."}]
            full_messages += [{"role": "user", "content": auto_prompt}]
        else:
            full_messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=full_messages,
            stream=True,
        )

        with st.chat_message("assistant"):
            response = st.write_stream(stream)
        st.session_state.messages.append({"role": "assistant", "content": response})
