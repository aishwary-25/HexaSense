import streamlit as st

st.set_page_config(page_title="HexaSense", page_icon="🛡️")

st.title("HexaSense")
st.caption("Private AI memory for Snapdragon PCs")

with st.sidebar:
    st.header("Controls")
    uploaded_files = st.file_uploader("Upload documents", accept_multiple_files=True)
    enable_redaction = st.toggle("Enable PII redaction", value=True)
    forget_mode = st.toggle("Forget mode", value=False)

st.write("HexaSense is a private, on-device knowledge assistant.")
st.write("Upload local documents, ask a question, and keep sensitive content private.")

if uploaded_files:
    st.success(f"{len(uploaded_files)} file(s) ready for local indexing.")

sample_prompt = "What did the client say about the launch timeline?"
user_query = st.text_area("Ask a question", value=sample_prompt)

if st.button("Run local Q&A"):
    st.info("This is a scaffold. Connect to your local retrieval and LLM pipeline here.")
    st.code(
        "HexaSense will retrieve relevant chunks, redact sensitive text, ground the answer in source snippets, and return citations."
    )

if forget_mode:
    st.warning("Forget mode enabled: the selected file or document will be deleted from the local memory store.")
