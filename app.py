import streamlit as st
from openai import OpenAI
import streamlit as st
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])

st.set_page_config(
    page_title="Assist- Smart Chat",
    layout="wide"
)

# CSS and layout
st.markdown("""
    <style>
        .big-font { font-size: 18px !important; }
        .css-1emrehy textarea { font-size: 16px !important; height: 150px !important; }
    </style>
""", unsafe_allow_html=True)

from PIL import Image

# Display logo and title using st.image for compatibility
col1, col2 = st.columns([1, 4])
with col1:
    st.image("anb_logo.png", width=60)
with col2:
    st.markdown("<h1 style='margin: 0; padding-top: 5px;'>Assist – Smart Chat</h1>", unsafe_allow_html=True)

# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Sidebar: Clear chat button
with st.sidebar:
    if st.button("🧹 Clear Chat"):
        st.session_state.messages = []
        st.rerun()

# Display existing messages
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"], unsafe_allow_html=True)

# Chat input area
user_input = st.chat_input("Paste email content or describe the issue…")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        thinking_placeholder = st.empty()
        thinking_placeholder.markdown("⏳ Thinking...")

        try:
            # Create response using full message history
            messages_for_gpt = [
{"role": "system", "content": (
                    "You are ANB Assist, a professional, concise, and polite chat assistant that helps summarize support tickets. "
                    "Always assume the platform is eTRACK+ (never ask for or mention it). Never ask for screenshots. Never say 'we will analyze' or imply the assistant is performing analysis. "
                    "If details are missing, ask helpful follow-up questions. It is up to the user to respond. Do not assume unanswered questions in the final summary. "
                    "Your role is to help gather relevant info. You may say: 'Providing these details will help generate a more complete and accurate ticket summary.'"
                )}
            ] + st.session_state.messages

            response = client.chat.completions.create(
                model="gpt-4",
                messages=messages_for_gpt,
                temperature=0.4
            )

            reply = response.choices[0].message.content.strip()
            thinking_placeholder.empty()
            st.markdown(reply)
            st.session_state.messages.append({"role": "assistant", "content": reply})

        except Exception as e:
            thinking_placeholder.markdown(f"❌ Error: {str(e)}")

# Generate Ticket Summary
if st.button("📄 Generate Ticket Summary"):
    with st.spinner("Generating structured summary..."):
        try:
            summary_prompt = """
            From the following support conversation, extract:
            1. Issue Description
            2. Root Cause Analysis / Findings
            3. Resolution / Action Points

            Format the result clearly using markdown. Do not refer to the assistant. Attribute all human actions without assuming who performed them.
            """ + "\n" + "\n".join([
                f"User: {m['content']}" if m['role'] == 'user' else f"Assistant: {m['content']}"
                for m in st.session_state.messages
            ])

            summary_response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are summarizing the conversation for structured support ticket fields. Avoid assuming the speaker’s role. Just describe what was done."},
                    {"role": "user", "content": summary_prompt}
                ],
                temperature=0.2
            )

            ticket_summary = summary_response.choices[0].message.content.strip()
            st.markdown("### 📝 Ticket Fields")
            st.markdown(ticket_summary, unsafe_allow_html=True)

        except Exception as e:
            st.error(f"Failed to generate summary: {e}")
#Redeploy
