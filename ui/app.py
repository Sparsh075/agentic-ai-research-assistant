import streamlit as st

st.set_page_config(page_title="Chat Test", layout="centered")

st.title("🧪 Streamlit Chat Test")

if "messages" not in st.session_state:
    st.session_state.messages = []

user_input = st.text_input(
    "Type something here 👇",
    placeholder="Hello..."
)

if st.button("Send"):
    if user_input:
        st.session_state.messages.append(user_input)

st.write("### Messages")
for msg in st.session_state.messages:
    st.write("🧑‍💻", msg)
