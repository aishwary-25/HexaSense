from html import escape
from pathlib import Path

import streamlit as st

from src.llm_client import LocalLLMClient
from src.pipeline import HexaSensePipeline, PipelineError

st.set_page_config(
    page_title="HexaSense | Private Local Intelligence",
    page_icon=":shield:",
    layout="wide",
    initial_sidebar_state="collapsed",
)

st.markdown(
    """
    <style>
    :root {
        --hex-black: #000000;
        --hex-surface: #111111;
        --hex-surface-raised: #171717;
        --hex-line: #2b2b2b;
        --hex-line-soft: rgba(255, 255, 255, .10);
        --hex-glass: rgba(17, 17, 17, .78);
        --hex-text: #f5f5f5;
        --hex-muted: #a3a3a3;
        --hex-red: #ef4444;
        --hex-red-dark: #391315;
        --hex-cyan: #48d7ef;
        --hex-mint: #5ee7bd;
        --hex-cursor: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M4 2l15 10-7 1 4 7-3 2-4-7-5 5z' fill='%23000' opacity='.7' transform='translate(.7 .9)'/%3E%3Cpath d='M4 2l15 10-7 1 4 7-3 2-4-7-5 5z' fill='%23fff' stroke='%23000' stroke-width='1.4' stroke-linejoin='round'/%3E%3C/svg%3E") 2 2, auto;
        --hex-cursor-active: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='24' height='24' viewBox='0 0 24 24'%3E%3Cpath d='M4 2l15 10-7 1 4 7-3 2-4-7-5 5z' fill='%23000' opacity='.7' transform='translate(.7 .9)'/%3E%3Cpath d='M4 2l15 10-7 1 4 7-3 2-4-7-5 5z' fill='%23fff' stroke='%23ef4444' stroke-width='1.4' stroke-linejoin='round'/%3E%3C/svg%3E") 2 2, pointer;
    }
    html, body, [data-testid="stApp"], [data-testid="stAppViewContainer"],
    [data-testid="stAppViewContainer"] > .main {
        background: var(--hex-black) !important;
        color: var(--hex-text);
    }
    .stApp { background: var(--hex-black) !important; }
    .stApp, [data-testid="stAppViewContainer"], [data-testid="stSidebar"] {
        cursor: var(--hex-cursor);
    }
    [data-testid="stButton"] button,
    [data-testid="stFileUploader"] button,
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],
    [data-testid="stExpander"] summary,
    a,
    textarea,
    input,
    [role="button"],
    [role="checkbox"],
    [role="switch"] {
        cursor: var(--hex-cursor-active);
        transition-duration: .18s;
        transition-timing-function: ease-out;
    }
    [data-testid="stAppViewContainer"]::before {
        content: "";
        position: fixed;
        inset: 0;
        pointer-events: none;
        z-index: 0;
        background: linear-gradient(180deg, rgba(239, 68, 68, .035), transparent 24%);
    }
    [data-testid="stHeader"], [data-testid="stToolbar"] {
        background: var(--hex-black) !important;
    }
    [data-testid="stHeader"] * { color: var(--hex-muted); }
    .block-container {
        box-sizing: border-box;
        max-width: 1180px;
        width: 100%;
        overflow-x: visible;
        min-width: 0;
        padding-top: 2.2rem;
        padding-bottom: 4rem;
    }
    [data-testid="stSidebar"],
    [data-testid="stSidebar"] > div:first-child,
    [data-testid="stSidebarContent"] {
        background: var(--hex-black) !important;
        border-right: 1px solid var(--hex-line);
    }
    [data-testid="stSidebar"] > div:first-child { padding-top: 2rem; }
    [data-testid="stSidebar"] {
        box-shadow: 16px 0 42px rgba(0, 0, 0, .28);
    }
    [data-testid="stSidebar"] .block-container {
        padding: 1.6rem 1.2rem 2.2rem !important;
    }
    [data-testid="stSidebar"] h2 {
        margin: 0 0 .35rem;
        font-size: 1.25rem;
        line-height: 1.25;
    }
    [data-testid="stSidebar"] h4 {
        margin: .35rem 0 .55rem;
        color: #d6d6d6 !important;
        font-size: .72rem;
        letter-spacing: .1em;
        line-height: 1.3;
        text-transform: uppercase;
    }
    [data-testid="stSidebar"] hr {
        margin: 1.15rem 0;
        border-color: var(--hex-line-soft) !important;
        opacity: 1;
    }
    [data-testid="stSidebar"] [data-testid="stFileUploader"],
    [data-testid="stSidebar"] [data-testid="stToggle"],
    [data-testid="stSidebar"] [data-testid="stExpander"] {
        margin-top: .55rem;
        margin-bottom: .9rem;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"],
    [data-testid="stSidebar"] [data-testid="stExpander"] details,
    [data-testid="stSidebar"] [data-testid="stExpander"] summary,
    [data-testid="stSidebar"] [data-testid="stExpander"] > div {
        background: rgba(17, 17, 17, .82) !important;
        border-color: var(--hex-line-soft) !important;
        color: var(--hex-text) !important;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary {
        border-radius: 10px;
    }
    [data-testid="stSidebar"] [data-testid="stExpander"] summary:hover {
        background: rgba(255, 255, 255, .055) !important;
    }
    [data-testid="stSidebar"] * { color: var(--hex-text); }
    [data-testid="stSidebar"] .stCaption,
    [data-testid="stSidebar"] small,
    [data-testid="stCaptionContainer"] { color: var(--hex-muted) !important; }
    h1, h2, h3, h4, h5, h6,
    [data-testid="stMarkdownContainer"] p,
    [data-testid="stMarkdownContainer"] li,
    label { color: var(--hex-text); }
    h1, h2, h3, h4, h5, h6 {
        overflow-wrap: anywhere;
        word-break: normal;
        letter-spacing: 0;
    }
    a { color: var(--hex-cyan); }
    .brand-kicker {
        display: inline-block;
        width: max-content;
        max-width: none;
        min-width: max-content;
        overflow: visible;
        white-space: nowrap;
        line-height: 1.35;
        padding: .08em .12em .12em;
        color: var(--hex-cyan);
        font-size: .76rem;
        font-weight: 800;
        letter-spacing: .14em;
        animation: hex-fade-in .35s ease-out both;
    }
    .brand-title {
        color: var(--hex-text);
        font-size: 2rem;
        line-height: 1.15;
        font-weight: 800;
        margin: .25rem 0 .55rem;
        max-width: 100%;
        overflow: visible;
        overflow-wrap: break-word;
        white-space: normal;
        animation: hex-fade-up .42s .04s ease-out both;
    }
    .brand-subtitle {
        color: var(--hex-muted);
        font-size: 1.05rem;
        margin-bottom: 1.35rem;
        animation: hex-fade-up .42s .08s ease-out both;
    }
    .status-strip {
        display: flex;
        flex-wrap: wrap;
        gap: .55rem;
        margin: .35rem 0 1.5rem;
        animation: hex-fade-up .42s .12s ease-out both;
    }
    .status-pill {
        border: 1px solid var(--hex-line-soft);
        border-radius: 999px;
        padding: .4rem .72rem;
        color: var(--hex-text);
        background: rgba(17, 17, 17, .68);
        backdrop-filter: blur(14px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .06);
        font-size: .8rem;
        transition: border-color .22s ease-out, box-shadow .22s ease-out;
    }
    .status-pill:hover { border-color: rgba(255, 255, 255, .20); box-shadow: 0 0 18px rgba(239, 68, 68, .08); }
    .status-pill.ready { border-color: #1d664f; background: #0c241d; color: var(--hex-mint); }
    .status-pill.offline { border-color: #713034; background: var(--hex-red-dark); color: #ff9b9f; }
    .section-label {
        color: var(--hex-muted);
        font-size: .75rem;
        font-weight: 800;
        letter-spacing: .1em;
        text-transform: uppercase;
        margin-bottom: .35rem;
    }
    .empty-state {
        position: relative;
        overflow: hidden;
        border: 1px dashed #3a3a3a;
        border-top-color: rgba(239, 68, 68, .48);
        background: linear-gradient(135deg, rgba(24, 24, 24, .88), rgba(10, 10, 10, .92));
        padding: 1.45rem 1.5rem;
        border-radius: 12px;
        margin: .75rem 0 1.5rem;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .045), 0 16px 48px rgba(0, 0, 0, .24);
        animation: hex-fade-up .35s ease-out both;
    }
    .empty-state strong { color: var(--hex-text); font-size: 1.05rem; }
    .privacy-copy { color: var(--hex-muted); font-size: .82rem; line-height: 1.65; }
    [data-testid="stVerticalBlockBorderWrapper"],
    [data-testid="stExpander"],
    [data-testid="stFileUploaderDropzone"],
    [data-testid="stAlert"] {
        background: var(--hex-glass) !important;
        border: 1px solid var(--hex-line-soft) !important;
        border-radius: 12px !important;
        color: var(--hex-text);
        backdrop-filter: blur(16px);
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .045), 0 14px 42px rgba(0, 0, 0, .20);
        animation: hex-fade-up .34s ease-out both;
    }
    [data-testid="stVerticalBlockBorderWrapper"] {
        transition: transform .22s ease-out, border-color .22s ease-out, box-shadow .22s ease-out;
    }
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-1px);
        border-color: rgba(255, 255, 255, .18) !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .06), 0 18px 48px rgba(0, 0, 0, .28);
    }
    [data-testid="stExpander"] {
        transition: border-color .22s ease-out, background .22s ease-out;
    }
    [data-testid="stExpander"]:hover { border-color: rgba(255, 255, 255, .18) !important; }
    [data-testid="stExpanderToggleIcon"] { color: var(--hex-muted); }
    [data-testid="stStatusWidget"] {
        background: var(--hex-surface) !important;
        border: 1px solid var(--hex-line-soft) !important;
        border-radius: 10px;
    }
    [data-testid="stFileUploaderDropzone"] section,
    [data-testid="stFileUploaderDropzone"] small { color: var(--hex-muted) !important; }
    [data-testid="stFileUploader"] {
        padding: .25rem;
        border-radius: 12px;
        background: rgba(17, 17, 17, .52);
    }
    [data-testid="stFileUploaderDropzone"] {
        border-style: dashed !important;
        border-color: rgba(239, 68, 68, .32) !important;
        transition: border-color .22s ease-out, background .22s ease-out;
    }
    [data-testid="stFileUploaderDropzone"]:hover {
        border-color: rgba(239, 68, 68, .72) !important;
        background: rgba(239, 68, 68, .055) !important;
    }
    .file-row {
        display: flex;
        align-items: center;
        gap: .65rem;
        padding: .65rem .7rem;
        margin: .38rem 0;
        border: 1px solid var(--hex-line-soft);
        border-radius: 9px;
        background: rgba(255, 255, 255, .035);
        color: var(--hex-text);
        font-size: .78rem;
        transition: background .2s ease-out, border-color .2s ease-out;
    }
    .file-row:hover { background: rgba(255, 255, 255, .06); border-color: rgba(255, 255, 255, .18); }
    .file-type {
        min-width: 2.2rem;
        padding: .2rem .28rem;
        border: 1px solid rgba(239, 68, 68, .38);
        border-radius: 5px;
        color: #ff9b9f;
        font-size: .64rem;
        font-weight: 800;
        letter-spacing: .06em;
        text-align: center;
    }
    .file-name { min-width: 0; overflow: hidden; text-overflow: ellipsis; white-space: nowrap; }
    .file-size { margin-left: auto; color: var(--hex-muted); white-space: nowrap; }
    .hex-footer {
        box-sizing: border-box;
        width: 100%;
        margin: 4rem auto 0;
        padding: 1.45rem 1rem .8rem;
        border-top: 1px solid var(--hex-line-soft);
        background: linear-gradient(180deg, rgba(17, 17, 17, .34), rgba(0, 0, 0, .12));
        color: var(--hex-muted);
        text-align: center;
    }
    .hex-footer-title,
    .hex-footer-byline {
        overflow-wrap: anywhere;
        white-space: normal;
    }
    .hex-footer-title {
        color: #d4d4d4;
        font-size: .78rem;
        font-weight: 650;
        letter-spacing: .02em;
    }
    .hex-footer-byline {
        margin-top: .38rem;
        color: #777777;
        font-size: .72rem;
    }
    .hex-footer-accent {
        color: #a9d9df;
    }
    textarea, input {
        background: var(--hex-surface-raised) !important;
        color: var(--hex-text) !important;
        border-color: var(--hex-line-soft) !important;
        border-radius: 10px !important;
    }
    textarea::placeholder, input::placeholder { color: #737373 !important; }
    [data-testid="stVerticalDivider"], hr { border-color: var(--hex-line) !important; }
    [data-testid="stButton"] button,
    [data-testid="stFileUploader"] button {
        background: var(--hex-surface-raised) !important;
        border-color: var(--hex-line-soft) !important;
        color: var(--hex-text) !important;
        border-radius: 9px !important;
        box-shadow: inset 0 1px 0 rgba(255, 255, 255, .045);
        transition: transform .2s ease-out, border-color .2s ease-out, box-shadow .2s ease-out, background .2s ease-out;
    }
    [data-testid="stButton"] button:hover,
    [data-testid="stFileUploader"] button:hover {
        border-color: rgba(239, 68, 68, .48) !important;
        color: #ffffff !important;
        transform: translateY(-1px);
        box-shadow: 0 8px 24px rgba(0, 0, 0, .28), 0 0 18px rgba(239, 68, 68, .08);
    }
    [data-testid="stButton"] button:active,
    [data-testid="stFileUploader"] button:active {
        transform: translateY(0) scale(.985);
    }
    [data-testid="stButton"] button[kind="primary"] {
        background: var(--hex-red) !important;
        border-color: var(--hex-red) !important;
        color: #ffffff !important;
    }
    [data-testid="stButton"] button[kind="primary"]:hover {
        background: #dc2626 !important;
        border-color: #dc2626 !important;
        box-shadow: 0 9px 28px rgba(239, 68, 68, .20);
    }
    [data-testid="stProgress"] [role="progressbar"] > div { background: var(--hex-red) !important; }
    [data-testid="stAlert"] { color: var(--hex-text) !important; }
    @keyframes hex-fade-up {
        from { opacity: 0; transform: translateY(5px); }
        to { opacity: 1; transform: translateY(0); }
    }
    @keyframes hex-fade-in {
        from { opacity: 0; }
        to { opacity: 1; }
    }
    @media (prefers-reduced-motion: reduce) {
        *, *::before, *::after {
            animation-duration: .01ms !important;
            animation-iteration-count: 1 !important;
            scroll-behavior: auto !important;
            transition-duration: .01ms !important;
        }
    }
    @media (max-width: 640px) {
        .brand-title { font-size: 1.45rem; }
        [data-testid="stAppViewContainer"] .main .block-container {
            max-width: 100%;
            min-width: 0;
            margin: 0;
            padding: 1.35rem 1rem 3rem;
        }
    }
    @media (max-width: 900px) {
        [data-testid="stSidebar"],
        [data-testid="stSidebar"] > div:first-child {
            width: 12rem !important;
            min-width: 12rem !important;
        }
        [data-testid="stAppViewContainer"] > .main {
            padding-left: 0;
        }
        [data-testid="stAppViewContainer"] .main .block-container {
            box-sizing: border-box;
            max-width: calc(100% - 12rem);
            width: 100%;
            margin-left: 0;
            margin-right: 0;
            transform: none;
        }
    }
    </style>
    """,
    unsafe_allow_html=True,
)


@st.cache_resource
def get_pipeline() -> HexaSensePipeline:
    return HexaSensePipeline()


@st.cache_data(ttl=10, show_spinner=False)
def get_local_ai_status(base_url: str, model_name: str) -> dict:
    client = LocalLLMClient(model_name)
    client.configure(base_url)
    return dict(client.health_check())


def format_size(size: int | None) -> str:
    if size is None:
        return "size unknown"
    if size < 1024:
        return f"{size} B"
    if size < 1024 * 1024:
        return f"{size / 1024:.1f} KB"
    return f"{size / (1024 * 1024):.1f} MB"


try:
    pipeline = get_pipeline()
except Exception as exc:
    st.error("HexaSense could not open its local workspace.")
    st.caption(str(exc))
    st.stop()


ai_status = get_local_ai_status(
    pipeline.config.ollama_base_url,
    pipeline.config.model_name,
)

st.markdown('<div class="brand-kicker">HEXASENSE</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="brand-title">Private Local Document Intelligence</div>',
    unsafe_allow_html=True,
)
st.markdown(
    '<div class="brand-subtitle">Ask your documents. Keep your data on-device.</div>',
    unsafe_allow_html=True,
)

if ai_status["ready"]:
    ai_pill = '<span class="status-pill ready">&bull; Local AI Ready</span>'
    ollama_pill = '<span class="status-pill ready">&bull; Ollama connected</span>'
else:
    ai_pill = '<span class="status-pill offline">&bull; Local AI Offline</span>'
    ollama_pill = '<span class="status-pill offline">&bull; Ollama unavailable</span>'
st.markdown(
    f'<div class="status-strip">{ai_pill}{ollama_pill}<span class="status-pill">&bull; No cloud inference</span></div>',
    unsafe_allow_html=True,
)
if not ai_status["ready"]:
    st.info(ai_status["message"])

flash_message = st.session_state.pop("flash_message", None)
if flash_message:
    st.success(flash_message)

with st.sidebar:
    st.markdown("## Workspace")
    st.caption("Build a private knowledge base from local files.")
    st.divider()
    uploaded_files = st.file_uploader(
        "Upload documents",
        type=["pdf", "docx", "txt", "md"],
        accept_multiple_files=True,
        help="Supported formats: PDF, DOCX, TXT, and Markdown.",
    )
    enable_redaction = st.toggle(
        "PII Redaction",
        value=pipeline.config.pii_redaction_enabled,
        help="Mask obvious emails, phone numbers, secrets, IP addresses, and card-like numbers before embedding.",
    )

    if uploaded_files:
        st.markdown("#### Ready to index")
        for uploaded_file in uploaded_files:
            suffix = Path(uploaded_file.name).suffix.upper().lstrip(".") or "FILE"
            st.markdown(
                f"""<div class="file-row">
                <span class="file-type">{suffix}</span>
                <span class="file-name">{escape(uploaded_file.name)}</span>
                <span class="file-size">{format_size(uploaded_file.size)}</span>
                </div>""",
                unsafe_allow_html=True,
            )

        if st.button("Index Documents", type="primary", use_container_width=True):
            progress = st.progress(0, text="Starting local indexing...")
            indexed_count = 0
            updated_count = 0
            for file_index, uploaded_file in enumerate(uploaded_files):
                status = st.status(
                    f"{uploaded_file.name} | preparing",
                    expanded=False,
                )

                def update_stage(stage: str) -> None:
                    status.update(
                        label=f"{uploaded_file.name} | {stage.capitalize()}",
                        state="running",
                    )

                try:
                    result = pipeline.index_bytes(
                        uploaded_file.getvalue(),
                        uploaded_file.name,
                        redact=enable_redaction,
                        progress=update_stage,
                    )
                    indexed_count += 1
                    updated_count += int(result.get("updated", False))
                    status.update(
                        label=f"{uploaded_file.name} | Indexed ({result['chunk_count']} chunks)",
                        state="complete",
                    )
                except PipelineError as exc:
                    status.update(
                        label=f"{uploaded_file.name} | Could not index",
                        state="error",
                    )
                    st.error(f"{uploaded_file.name}: {exc}")
                progress.progress(
                    (file_index + 1) / len(uploaded_files),
                    text=f"Processed {file_index + 1} of {len(uploaded_files)} document(s)",
                )
            progress.empty()
            if indexed_count:
                if updated_count:
                    st.session_state["flash_message"] = (
                        f"{indexed_count} document(s) processed successfully; "
                        f"{updated_count} updated."
                    )
                else:
                    st.session_state["flash_message"] = (
                        f"{indexed_count} document(s) indexed successfully."
                    )
                st.rerun()

    st.divider()
    st.markdown("#### Configuration")
    st.caption(f"Embedding: {pipeline.config.embedding_model_name}")
    st.caption(f"Answer model: {pipeline.config.model_name}")
    st.caption("Storage: Local")

    with st.expander("Privacy by design"):
        st.markdown(
            """
            <div class="privacy-copy">
            - Documents processed locally<br>
            - Local embeddings and vector search<br>
            - Local LLM via Ollama<br>
            - Optional PII redaction before indexing<br>
            - Selective document forgetting<br>
            - No cloud inference required
            </div>
            """,
            unsafe_allow_html=True,
        )

st.markdown('<div class="section-label">Workspace memory</div>', unsafe_allow_html=True)
st.header("Indexed documents")
documents = pipeline.list_documents()

if not documents:
    st.markdown(
        """
        <div class="empty-state">
        <strong>Your local knowledge base is empty.</strong><br>
        Upload documents in the Workspace panel, index them, then ask a question grounded in your files.
        </div>
        """,
        unsafe_allow_html=True,
    )
    st.caption("1. Upload documents   2. Index them   3. Ask a question")
else:
    for document in documents:
        with st.container(border=True):
            details, action = st.columns([5, 1])
            with details:
                redaction_label = (
                    "PII redacted" if document["redacted"] else "redaction off"
                )
                st.markdown(f"**{document['file_name']}**")
                st.caption(
                    f"{document['chunk_count']} chunks | {redaction_label} | indexed locally"
                )
            with action:
                if st.button(
                    "Forget",
                    key=f"request_forget_{document['doc_id']}",
                    use_container_width=True,
                ):
                    st.session_state["pending_forget"] = document
                    st.rerun()

pending_forget = st.session_state.get("pending_forget")
if pending_forget:
    st.warning(
        f"Forget {pending_forget['file_name']}? This removes the document, its indexed chunks, and its stored local copy from this workspace."
    )
    cancel, confirm = st.columns(2)
    with cancel:
        if st.button("Cancel", key="cancel_forget", use_container_width=True):
            st.session_state.pop("pending_forget", None)
            st.rerun()
    with confirm:
        if st.button(
            "Forget document",
            key="confirm_forget",
            type="primary",
            use_container_width=True,
        ):
            try:
                pipeline.forget_document(pending_forget["doc_id"])
                st.session_state.pop("pending_forget", None)
                st.session_state["flash_message"] = (
                    f"{pending_forget['file_name']} has been forgotten."
                )
                st.rerun()
            except PipelineError as exc:
                st.error(str(exc))

st.divider()
st.markdown(
    '<div class="section-label">Grounded retrieval</div>', unsafe_allow_html=True
)
st.header("Ask your documents")
st.caption("Answers are generated only from retrieved document evidence.")

if "question" not in st.session_state:
    st.session_state["question"] = ""

st.caption("Try an example")
example_columns = st.columns(3)
examples = [
    ("Launch timeline", "What did the client say about the launch timeline?"),
    ("Payment terms", "What are the payment terms?"),
    ("Privacy priorities", "What are the project's privacy priorities?"),
]
for column, (label, question) in zip(example_columns, examples):
    with column:
        if st.button(label, key=f"example_{label}", use_container_width=True):
            st.session_state["question"] = question
            st.rerun()

user_query = st.text_area(
    "Question",
    key="question",
    placeholder="What did the client say about the launch timeline?",
    height=100,
    disabled=not documents,
)

search_clicked = st.button(
    "Search & Answer",
    type="primary",
    use_container_width=True,
    disabled=not documents,
)

if search_clicked:
    try:
        with st.status(
            "Searching your local knowledge base...", expanded=False
        ) as answer_status:
            result = pipeline.query(user_query)
            answer_status.update(label="Answer ready", state="complete")
        st.markdown("### Answer")
        with st.container(border=True):
            st.write(result.answer)

        st.markdown("### Source evidence")
        if not result.sources:
            st.info("No supporting source chunks were found.")
        for source_index, source in enumerate(result.sources, start=1):
            with st.expander(
                f"Source {source_index} | {source['file_name']} | relevance {source['score']:.2f}"
            ):
                st.caption(f"Chunk {source['chunk_id']}")
                st.write(source["text"])
    except PipelineError as exc:
        st.error(str(exc))

st.markdown(
    """
    <footer class="hex-footer" aria-label="HexaSense footer">
        <div class="hex-footer-title">HexaSense &middot; Private Local Document Intelligence</div>
        <div class="hex-footer-byline">Built by <span class="hex-footer-accent">Aishwary Swarnkar</span> &middot; JECRC University</div>
    </footer>
    """,
    unsafe_allow_html=True,
)
