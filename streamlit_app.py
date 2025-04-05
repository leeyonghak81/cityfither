import streamlit as st
from openai import OpenAI
import urllib.parse

# [임시] 날씨 정보 가져오기 - 실제 API 연동 필요
def get_weather_summary(region):
    # TODO: 실제 날씨 API 연동 시 수정
    fake_weather = {
        "서울": "맑음",
        "부산": "비",
        "대구": "흐림"
    }
    return fake_weather.get(region, "맑음")

# 구글 지도 링크 생성
def generate_map_link(place_name):
    query = urllib.parse.quote(place_name)
    return f"https://www.google.com/maps/search/{query}"

# GPT 응답 가공: 장소 줄별로 링크 붙이기
def add_links_to_places(response_text):
    lines = response_text.split("\n")
    new_lines = []
    for line in lines:
        if line.strip().startswith("-"):
            place_name = line.split(":")[0].replace("-", "").strip()
            link = generate_map_link(place_name)
            new_line = f"{line}  \n👉 [지도 보기]({link})"
            new_lines.append(new_line)
        else:
            new_lines.append(line)
    return "\n".join(new_lines)

# 지역명 추출
known_regions = ["서울", "부산", "대구", "대전", "광주", "인천", "제주", "수원", "울산", "춘천"]
def extract_region(prompt):
    for region in known_regions:
        if region in prompt:
            return region
    return None

# Streamlit 앱 시작
st.title("👨‍👩‍👧 가족 나들이 장소 추천 챗봇")
st.write("지역명을 입력하면 GPT가 가족이 놀기 좋은 장소를 추천하고, 지도 링크도 제공해드려요! 날씨에 따라 실내/실외 장소를 자동으로 고려해드려요.")

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
            weather = get_weather_summary(region)
            indoor_or_outdoor = "실내" if "비" in weather or "우천" in weather else "야외"
            gpt_prompt = (
                f"{region} 지역은 현재 날씨가 '{weather}'입니다. "
                f"{indoor_or_outdoor} 활동에 적합한 가족 나들이 장소 3곳을 추천해줘. "
                "장소 이름과 간단한 설명을 줄바꿈해서 제공해줘."
            )
            messages = [{"role": "system", "content": "너는 여행지 추천 전문가야. 장소 추천만 간단하고 명확하게 해줘."}]
            messages += [{"role": "user", "content": gpt_prompt}]
        else:
            messages = [{"role": m["role"], "content": m["content"]} for m in st.session_state.messages]

        stream = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            stream=True,
        )

        with st.chat_message("assistant"):
            raw_response = st.write_stream(stream)

        # 지도 링크 추가
        if region:
            response_with_links = add_links_to_places(raw_response)
        else:
            response_with_links = raw_response

        st.session_state.messages.append({"role": "assistant", "content": response_with_links})
