# RAG PDF Chat Assistant

A production-grade Retrieval-Augmented Generation (RAG) application that allows users to upload PDFs and have intelligent conversations with grounded answers and citations.

## ✨ Features

- **PDF Upload & Processing**: Extract text from any PDF with robust error handling
- **Semantic Chunking**: Intelligent text splitting that preserves paragraph context
- **Vector Embeddings**: OpenAI embeddings (text-embedding-3-small) for semantic search
- **FAISS Vector Store**: Fast similarity search with local persistence
- **RAG Q&A**: LLM-powered answers grounded in document context
- **Citations**: Every answer includes page numbers and text snippets
- **Chat History**: Maintains conversation context across multiple turns
- **Production Logging**: Rotating file handlers for observability
- **Modular Architecture**: Cleanly separated concerns for maintainability

## 📋 Tech Stack

| Component | Technology | Choice Rationale |
|-----------|-----------|-----------------|
| **Frontend** | Streamlit 1.35.0 | Fast web UI prototyping, interactive components |
| **PDF Parsing** | pdfplumber 0.10.3 | Accurate text extraction with table support |
| **Embeddings** | OpenAI text-embedding-3-small | High-quality semantic embeddings (1536 dims) |
| **Vector Store** | FAISS 1.7.4 | Fast in-memory search, local persistence |
| **LLM** | OpenAI GPT-3.5-Turbo | Fast, cost-effective for chat |
| **Framework** | LangChain 0.1.14 | Standardized components for RAG pipeline |
| **Logging** | Python logging | Built-in, rotating file handlers |

## 🏗️ Project Structure

```
rag-pdf-chatbot/
├── app.py                          # Streamlit main application
├── config.py                       # Configuration management
├── requirements.txt                # Python dependencies
├── .env.example                    # Environment variables template
│
├── src/                           # Source code
│   ├── __init__.py
│   ├── ingestion/                 # PDF processing
│   │   ├── __init__.py
│   │   ├── pdf_parser.py          # PDF text extraction
│   │   └── chunker.py             # Semantic text chunking
│   │
│   ├── vector_store/              # Vector storage
│   │   ├── __init__.py
│   │   └── faiss_store.py         # FAISS wrapper
│   │
│   ├── rag/                       # RAG pipeline
│   │   ├── __init__.py
│   │   ├── retriever.py           # Semantic search
│   │   └── qa_chain.py            # LLM Q&A with citations
│   │
│   └── utils/                     # Utilities
│       ├── __init__.py
│       ├── logger.py              # Logging setup
│       └── helpers.py             # Helper functions
│
├── eval/                          # Evaluation framework
│   ├── __init__.py
│   ├── test_questions.py          # Test suite
│   └── evaluation.py              # Evaluation metrics
│
├── storage/                       # Vector DB persistence
│   └── faiss_index/              # FAISS index files
│
├── logs/                          # Application logs
│   └── rag_app.log               # Rotating log file
│
└── README.md                      # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- OpenAI API key

### Installation

1. **Clone the repository** (or navigate to the project directory)
   ```bash
   cd rag-pdf-chatbot
   ```

2. **Create a virtual environment** (recommended)
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Setup environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

   **Required environment variables:**
   ```
   OPENAI_API_KEY=sk-...
   OPENAI_MODEL=gpt-3.5-turbo
   EMBEDDING_MODEL=text-embedding-3-small
   ```

5. **Run the Streamlit app**
   ```bash
   streamlit run app.py
   ```

   The app will open at `http://localhost:8501`

## 🔄 Pipeline Overview

### Data Flow

```
PDF Upload
    ↓
Text Extraction (pdfplumber)
    ↓
Semantic Chunking (recursive split)
    ↓
Embedding Generation (OpenAI)
    ↓
Vector Store (FAISS)
    ↓
User Query
    ↓
Query Embedding
    ↓
Similarity Search (L2 distance)
    ↓
Top-K Retrieval (default: 3)
    ↓
LLM Prompt Construction
    ↓
Answer Generation + Citations
```

## 📊 Configuration Details

### Chunking Strategy

**Algorithm**: Recursive semantic splitting with overlap

**Steps**:
1. Split by paragraph boundaries (`\n\n`)
2. Fall back to line breaks (`\n`)
3. Fall back to sentence boundaries (`. !? `)
4. Fall back to word boundaries (` `)

**Parameters** (configurable via `.env`):
- `CHUNK_SIZE`: 500 tokens (default)
- `CHUNK_OVERLAP`: 50 tokens for context preservation

**Rationale**: Preserves semantic structure while maintaining reasonable context windows.

### Embedding Model

- **Model**: `text-embedding-3-small`
- **Dimensions**: 1536
- **Cost**: Very low (cheaper than ada-v2)
- **Quality**: High similarity matching for semantic search

### Vector Store: FAISS

- **Index Type**: IndexFlatL2 (exhaustive L2 distance search)
- **Persistence**: Saves index and metadata to `./storage/faiss_index/`
- **Retrieval Method**: 
  - Generate query embedding
  - Compute L2 distance to all vectors
  - Return top-K with similarity threshold filter
  - Similarity = 1/(1+L2_distance)
- **Threshold**: 0.5 (configurable)

### LLM Model

- **Model**: `gpt-3.5-turbo`
- **Temperature**: 0.7 (balanced creativity/consistency)
- **Context**: Uses chat history (last 3 exchanges) for follow-ups
- **Prompt Design**: Emphasizes grounding in retrieved context

## 💬 Chat History Management

- **Storage**: In-memory Streamlit session state
- **Context Window**: Last 6 messages (3 exchanges) for LLM
- **Persistence**: Conversation history maintained during session
- **Reset**: Clearing PDF resets conversation history

## 🔍 Retrieval Strategy

1. **Query Embedding**: Generate embedding for user query
2. **Similarity Search**: Compute L2 distance to all stored embeddings
3. **Ranking**: Sort by similarity score (1/(1+distance))
4. **Filtering**: Apply threshold (default: 0.5)
5. **Top-K Selection**: Return `k` most relevant chunks (default: 3)

**Why L2 distance?**
- Normalized embeddings: L2 distance = 2 - 2*cosine_similarity
- Efficient in FAISS
- Works well with normalized embeddings

## 📝 Citation Format

Each answer includes citations with:
- **Document**: Source PDF filename
- **Page Number**: Which page the information came from
- **Similarity Score**: Relevance percentage (0-100%)
- **Snippet**: First 150 characters of the source text

## 📚 Logging & Observability

**Configuration**:
```
Log File: ./logs/rag_app.log
Max File Size: 10 MB
Backup Count: 5 files
Format: %(asctime)s - %(name)s - %(levelname)s - %(message)s
```

**Log Levels**:
- `DEBUG`: Detailed operations
- `INFO`: Major steps (PDF loaded, embeddings generated, etc.)
- `WARNING`: Non-critical issues (failed to extract metadata)
- `ERROR`: Critical failures (API errors, parsing failures)

**Key Events Logged**:
- PDF upload and processing
- Chunk creation
- Vector store operations
- Query retrieval
- Answer generation
- Errors and exceptions

## 🧪 Evaluation Framework

### Running Tests

```python
from eval import TEST_QUESTIONS, evaluate_qa_chain

# Test questions
results = evaluate_qa_chain(qa_chain, TEST_QUESTIONS)
print(results['summary'])
```

### Test Coverage

- 8 generic test questions covering document aspects
- Difficulty levels: Easy, Medium, Hard
- Metrics: Success rate, avg citations, avg sources

### Evaluation Output

```
========================================
Summary Metrics
========================================
Total Questions: 8
Successful: 8
Failed: 0
Success Rate: 100.0%
Avg Citations: 2.5
Avg Sources: 2.5
```

## ⚙️ Advanced Configuration

### Custom Chunking

```python
from src.ingestion import TextChunker

chunker = TextChunker(chunk_size=300, chunk_overlap=30)
chunks = chunker.chunk_text(text, page_number=1, source="doc.pdf")
```

### Custom Retrieval

```python
from src.rag import Retriever

retriever = Retriever()
retriever.add_documents(chunks)
results = retriever.retrieve(query, k=5)  # Get top 5
```

### Custom LLM

```python
from langchain_openai import ChatOpenAI

llm = ChatOpenAI(
    model_name="gpt-4",
    temperature=0.9,
    api_key=settings.openai_api_key
)
```

## 🐛 Known Limitations

1. **PDF Complexity**: May struggle with:
   - Scanned PDFs without OCR (images only)
   - Complex layout PDFs with sidebars/columns
   - PDFs with embedded objects

2. **Token Limits**:
   - OpenAI API rate limits apply
   - Large documents may exceed embedding token limits
   - Context window limited to ~4k tokens for gpt-3.5-turbo

3. **Citation Accuracy**:
   - Page numbers tracked from PDF structure
   - May not be perfectly accurate for complex layouts
   - Overlapping chunks may cite same content multiple times

4. **Language Coverage**:
   - Optimized for English
   - Other languages may work but not tested

5. **Cost Considerations**:
   - Each query costs embeddings + LLM tokens
   - Text-embedding-3-small: ~$0.02 per 1M tokens
   - GPT-3.5-turbo: ~$0.0005 per 1K input tokens

## 🔐 Security Notes

- OpenAI API key should be kept in `.env` (not committed to git)
- PDFs are processed locally
- Vector embeddings stored locally in `./storage/`
- No data sent to external services except OpenAI APIs

## 📈 Performance Tips

1. **Chunk Size**: Smaller chunks = more relevant but slower. Default 500 is balanced.
2. **Top-K**: More results = slower but potentially better answers. Default 3 is fast.
3. **Batch Processing**: Process many PDFs in background jobs
4. **Vector Store**: FAISS is single-threaded; consider Qdrant for concurrent access

## 🤝 Contributing

To extend this system:

1. **New Embedding Models**: Modify `src/rag/retriever.py`
2. **Custom Chunking**: Create new class in `src/ingestion/chunker.py`
3. **Different Vector Store**: Implement `src/vector_store/` interface
4. **New LLM Providers**: Update `src/rag/qa_chain.py`

## 📄 License

This project is provided as-is for educational and evaluation purposes.

## 📞 Support

For issues or questions:
1. Check logs at `./logs/rag_app.log`
2. Verify `.env` configuration
3. Ensure OpenAI API key is valid
4. Check network connectivity

---

**Built with** ❤️ using Streamlit, LangChain, and OpenAI APIs.
