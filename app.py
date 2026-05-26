"""
Streamlit-based RAG Application.
Provides a web interface for PDF upload, processing, and Q&A with citations.
"""

import streamlit as st
import tempfile
from pathlib import Path

from config import settings
from src.ingestion import PDFParser, TextChunker
from src.rag import Retriever, QAChain
from src.guardrails import InputValidator, OutputValidator, SafetyChecker
from src.utils.logger import setup_logger

logger = setup_logger(__name__)

# Configure Streamlit
st.set_page_config(
    page_title="RAG PDF Chat",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply custom CSS for Claude-like interface
st.markdown("""
<style>
    /* Main container */
    .main {
        background: #ffffff;
    }

    /* Chat messages */
    .user-message {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-left: auto;
        width: fit-content;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.1);
    }

    .assistant-message {
        background: #f0f0f0;
        color: #000;
        padding: 12px 16px;
        border-radius: 12px;
        margin: 8px 0;
        margin-right: auto;
        width: fit-content;
        max-width: 80%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }

    /* Citation styling */
    .citation-box {
        background-color: #f5f5f5;
        border-left: 4px solid #667eea;
        padding: 12px;
        margin: 8px 0;
        border-radius: 8px;
        font-size: 0.9em;
    }

    .answer-box {
        background-color: #f0f8ff;
        border-left: 4px solid #4caf50;
        padding: 15px;
        margin: 10px 0;
        border-radius: 8px;
    }

    .error-box {
        background-color: #fff5f5;
        border-left: 4px solid #f44336;
        padding: 12px;
        margin: 10px 0;
        border-radius: 8px;
    }

    /* Search box */
    .search-box {
        background: #f5f5f5;
        padding: 12px;
        border-radius: 8px;
        margin-bottom: 16px;
    }

    /* Header styling */
    h1, h2, h3 {
        color: #1a1a1a;
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: 600;
    }

    .stButton > button:hover {
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialize Streamlit session state."""
    if 'qa_chain' not in st.session_state:
        st.session_state.qa_chain = None
        st.session_state.retriever = None

    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = []

    if 'pdf_loaded' not in st.session_state:
        st.session_state.pdf_loaded = False

    if 'document_metadata' not in st.session_state:
        st.session_state.document_metadata = None

    # Initialize guardrails
    if 'input_validator' not in st.session_state:
        st.session_state.input_validator = InputValidator()

    if 'output_validator' not in st.session_state:
        st.session_state.output_validator = OutputValidator()

    if 'safety_checker' not in st.session_state:
        st.session_state.safety_checker = SafetyChecker()


def process_pdf(pdf_file) -> bool:
    """
    Process an uploaded PDF file.

    Args:
        pdf_file: Uploaded PDF file object

    Returns:
        True if processing successful
    """
    try:
        # Guardrail: Validate PDF file
        file_size_mb = len(pdf_file.getbuffer()) / (1024 * 1024)
        is_valid, error_msg = st.session_state.input_validator.validate_pdf_file(
            pdf_file.name, file_size_mb
        )

        if not is_valid:
            logger.error(f"PDF validation failed: {error_msg}")
            st.error(f"❌ {error_msg}")
            return False

        st.info(f"✅ PDF validation passed ({file_size_mb:.2f}MB)")

        # Save uploaded file temporarily
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
            tmp_file.write(pdf_file.getbuffer())
            tmp_path = tmp_file.name

        # Parse PDF
        with st.spinner("📄 Extracting text from PDF..."):
            parser = PDFParser(tmp_path)
            pages = parser.extract_text()
            metadata = parser.get_metadata()
            st.session_state.document_metadata = metadata

        logger.info(f"Extracted {len(pages)} pages from PDF")

        # Chunk text
        with st.spinner("✂️ Chunking text..."):
            chunker = TextChunker()
            all_chunks = []

            for page in pages:
                chunks = chunker.chunk_text(
                    text=page['text'],
                    page_number=page['page_number'],
                    source=metadata['title']
                )
                all_chunks.extend(chunks)

        logger.info(f"Created {len(all_chunks)} chunks")

        # Initialize RAG pipeline
        with st.spinner("🔍 Initializing vector store and embeddings..."):
            retriever = Retriever()
            retriever.add_documents(all_chunks)

            qa_chain = QAChain(retriever)

            st.session_state.retriever = retriever
            st.session_state.qa_chain = qa_chain
            st.session_state.pdf_loaded = True
            st.session_state.chat_history = []

        logger.info("PDF processing completed successfully")
        return True

    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        st.error(f"Error processing PDF: {str(e)}")
        return False

    finally:
        # Clean up temp file
        try:
            Path(tmp_path).unlink()
        except:
            pass


def display_answer_with_citations(response: dict):
    """
    Display answer with formatted citations in Claude-style.

    Args:
        response: QA chain response dictionary
    """
    # Display answer in assistant message style
    st.markdown(f"""
    <div class="assistant-message" style="max-width: 100%; width: auto;">
        <strong>Assistant</strong><br>
        {response.get('answer', 'No answer generated')}
    </div>
    """, unsafe_allow_html=True)

    # Display citations
    citations = response.get('citations', [])
    if citations:
        st.write("### 📚 Sources")
        cols = st.columns(len(citations))
        for i, (col, citation) in enumerate(zip(cols, citations)):
            with col:
                st.markdown(f"""
                <div class="citation-box">
                <strong>Source {i+1}</strong><br>
                📄 {citation['document']}<br>
                📄 Page {citation['page']}<br>
                ⭐ {citation['similarity_score']:.0%} relevant<br>
                <small style="color: #666;">"{citation['snippet'][:100]}..."</small>
                </div>
                """, unsafe_allow_html=True)


def main():
    """Main Streamlit application."""
    # Initialize session state
    initialize_session_state()

    # Header
    st.title("📚 RAG PDF Chat Assistant")
    st.markdown("""
    Upload a PDF document and ask questions about it. The system will retrieve relevant sections
    and provide answers with citations.
    """)

    # Sidebar
    with st.sidebar:
        st.header("⚙️ Configuration")

        # PDF Upload
        st.subheader("1️⃣ Upload PDF")
        uploaded_file = st.file_uploader("Choose a PDF file", type=['pdf'])

        if uploaded_file:
            if st.button("📤 Process PDF", use_container_width=True):
                if process_pdf(uploaded_file):
                    st.success("✅ PDF processed successfully!")
                else:
                    st.error("❌ Failed to process PDF")

        # Show document info
        if st.session_state.pdf_loaded and st.session_state.document_metadata:
            st.subheader("📄 Document Info")
            metadata = st.session_state.document_metadata
            st.info(f"""
            **Title:** {metadata.get('title', 'N/A')}
            **Pages:** {metadata.get('pages', 'N/A')}
            **Author:** {metadata.get('author', 'N/A')}
            """)

            # Show retriever stats
            if st.session_state.retriever:
                stats = st.session_state.retriever.get_stats()
                st.metric("Vectors in Store", stats['vector_store_stats']['total_vectors'])

        # Configuration options
        st.subheader("⚙️ RAG Settings")
        k_results = st.slider(
            "Number of documents to retrieve:",
            min_value=1,
            max_value=10,
            value=settings.top_k_results,
            help="How many relevant document chunks to retrieve for each query"
        )
        st.session_state.k_results = k_results

        # Clear button
        if st.button("🗑️ Clear All", use_container_width=True):
            st.session_state.qa_chain = None
            st.session_state.chat_history = []
            st.session_state.pdf_loaded = False
            st.rerun()

    # Main content area
    if not st.session_state.pdf_loaded:
        st.info("👈 Upload a PDF file from the sidebar to get started!")
        return

    # Chat interface
    st.subheader("💬 Conversation")

    # Search box for chat history
    search_query = st.text_input(
        "🔍 Search conversations:",
        placeholder="Search in messages...",
        key="search_input"
    )

    # Display chat history with search filter
    filtered_history = st.session_state.chat_history
    if search_query:
        filtered_history = [
            msg for msg in st.session_state.chat_history
            if search_query.lower() in msg['content'].lower()
        ]
        if filtered_history:
            st.success(f"✓ Found {len(filtered_history)} message(s)")
        else:
            st.warning(f"✗ No messages found matching '{search_query}'")

    # Create a container for chat messages
    chat_container = st.container()

    with chat_container:
        for i, message in enumerate(filtered_history):
            if message['role'] == 'user':
                # User message - right aligned, purple
                col1, col2 = st.columns([1, 3])
                with col2:
                    st.markdown(f"""
                    <div class="user-message">
                        <strong>You</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)
            else:
                # Assistant message - left aligned, gray
                col1, col2 = st.columns([3, 1])
                with col1:
                    st.markdown(f"""
                    <div class="assistant-message">
                        <strong>Assistant</strong><br>
                        {message['content']}
                    </div>
                    """, unsafe_allow_html=True)

                    if message.get('citations'):
                        with st.expander("📚 Show sources"):
                            for j, citation in enumerate(message['citations'], 1):
                                st.markdown(f"""
                                <div class="citation-box">
                                <strong>[Source {j}]</strong> {citation['document']} - Page {citation['page']}<br>
                                <em>Relevance: {citation['similarity_score']:.0%}</em><br>
                                <small>"{citation['snippet']}"</small>
                                </div>
                                """, unsafe_allow_html=True)

    # Divider
    st.divider()

    # Query input - modern design
    st.write("")  # Spacing
    col1, col2 = st.columns([0.92, 0.08])

    with col1:
        user_query = st.text_area(
            "Message",
            placeholder="Ask something about the PDF...",
            key="user_input",
            height=50,
            label_visibility="collapsed"
        )

    with col2:
        send_button = st.button("↑", use_container_width=True, help="Send message")

    # Generate answer
    if send_button and user_query:
        # Guardrail: Validate user input
        is_valid, error_msg, metadata = st.session_state.input_validator.validate_query(user_query)

        if not is_valid:
            logger.error(f"Input validation failed: {error_msg}")
            st.error(f"❌ {error_msg}")
            st.stop()

        # Guardrail: Check rate limit
        user_id = "session_user"  # Use session ID in production
        is_allowed, rate_msg = st.session_state.safety_checker.check_rate_limit(user_id)

        if not is_allowed:
            logger.warning(f"Rate limit exceeded: {rate_msg}")
            st.warning(f"⚠️ {rate_msg}")
            st.stop()

        # Add user message to history
        st.session_state.chat_history.append({
            "role": "user",
            "content": user_query
        })

        try:
            # Generate answer
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.qa_chain.generate_answer(
                    query=user_query,
                    chat_history=st.session_state.chat_history,
                    k=st.session_state.k_results
                )

                # Guardrail: Validate answer
                is_valid, val_error, val_metadata = st.session_state.output_validator.validate_answer(
                    response.get("answer", ""), user_query
                )

                if not is_valid:
                    logger.error(f"Output validation failed: {val_error}")
                    st.error(f"⚠️ {val_error}")
                    return

                # Guardrail: Validate citations
                cit_valid, cit_error = st.session_state.output_validator.validate_citations(
                    response.get("citations", []), response.get("answer", "")
                )

                if not cit_valid:
                    logger.warning(f"Citation validation warning: {cit_error}")
                    st.warning(f"⚠️ {cit_error}")

            # Display answer and citations
            display_answer_with_citations(response)

            # Add to chat history
            st.session_state.chat_history.append({
                "role": "assistant",
                "content": response.get("answer", ""),
                "citations": response.get("citations", [])
            })

            logger.info(f"Answered query: {user_query[:50]}")

        except Exception as e:
            error_msg = f"Error generating answer: {str(e)}"
            logger.error(error_msg)
            st.markdown(f'<div class="error-box">{error_msg}</div>', unsafe_allow_html=True)

    # Sidebar info
    with st.sidebar:
        st.divider()
        st.subheader("ℹ️ About")
        st.markdown("""
        This is a Retrieval-Augmented Generation (RAG) application.

        **How it works:**
        1. You upload a PDF
        2. The app extracts text and creates embeddings
        3. Embeddings are stored in a vector database
        4. When you ask a question, it retrieves relevant sections
        5. An LLM generates answers based on retrieved context
        6. Citations show where answers come from

        **Models Used:**
        - **Embedding:** text-embedding-3-small (1536 dims)
        - **LLM:** gpt-3.5-turbo
        - **Vector Store:** FAISS
        """)


if __name__ == "__main__":
    try:
        settings.validate_config()
        settings.get_paths()
        main()
    except ValueError as e:
        st.error(f"Configuration Error: {str(e)}")
        st.info("Please set OPENAI_API_KEY environment variable before running the app.")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        st.error(f"Application Error: {str(e)}")
