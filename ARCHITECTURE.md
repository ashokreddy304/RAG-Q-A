# System Architecture

This document provides a detailed technical overview of the RAG PDF Chat Assistant architecture.

## High-Level Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                      Streamlit Web UI (app.py)                  │
│  - PDF Upload  - Chat Interface  - Citation Display             │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        │                    │                    │
        ▼                    ▼                    ▼
┌──────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│    Ingestion     │ │   RAG Pipeline   │ │  Vector Store   │
│   (pdf_parser,   │ │ (retriever,      │ │  (FAISS Index   │
│    chunker)      │ │  qa_chain)       │ │  + Metadata)    │
└──────┬───────────┘ └──────┬───────────┘ └────────┬────────┘
       │                    │                       │
       └────────────────────┼───────────────────────┘
                            │
                   ┌────────┴────────┐
                   │                 │
                   ▼                 ▼
            ┌─────────────┐   ┌──────────────┐
            │  OpenAI API │   │  LangChain   │
            │  Embeddings │   │  ChatOpenAI  │
            └─────────────┘   └──────────────┘
```

## Component Architecture

### 1. Ingestion Layer (`src/ingestion/`)

#### PDF Parser (`pdf_parser.py`)
```python
PDFParser
├── extract_text()          # Returns pages with text + metadata
├── get_full_text()         # Returns concatenated document
└── get_metadata()          # Returns title, author, pages
```

**Flow**:
```
PDF File → pdfplumber → Extract Text & Tables → Page Objects
         → Track Page Numbers → Return Metadata
```

**Key Features**:
- Preserves table structure
- Tracks page numbers for citations
- Handles both text and scanned content gracefully
- Extracts document metadata

#### Text Chunker (`chunker.py`)
```python
TextChunker
├── chunk_text()            # Main chunking interface
├── _recursive_split()      # Recursive semantic splitting
├── _merge_and_split_chunks()  # Size optimization
└── _add_overlap()          # Add context overlap
```

**Chunking Strategy**:
```
Input Text
    ↓
Clean & Normalize
    ↓
Try Split by Paragraphs (\n\n)
    ├─ Success? → Go to Merge/Split
    └─ Fail? → Try Split by Lines (\n)
                    ├─ Success? → Go to Merge/Split
                    └─ Fail? → Try Split by Sentences
                                    ├─ Success? → Go to Merge/Split
                                    └─ Fail? → Split by Words
    ↓
Merge Small Chunks
Split Large Chunks (> chunk_size)
    ↓
Add Overlap Between Chunks
    ↓
Return Chunks with Metadata
```

**Parameters**:
- `chunk_size`: 500 tokens (configurable)
- `chunk_overlap`: 50 tokens (overlap words)

**Chunk Structure**:
```python
{
    "text": "chunk content...",
    "page_number": 2,
    "source": "document.pdf",
    "chunk_index": 0,
    "chunk_length": 487
}
```

### 2. Vector Store Layer (`src/vector_store/`)

#### FAISS Vector Store (`faiss_store.py`)
```python
FAISSVectorStore
├── add_embeddings()        # Add vectors + metadata
├── search()                # Similarity search
├── clear()                 # Reset store
├── get_stats()             # Statistics
└── _save_index()           # Persist to disk
```

**Storage Structure**:
```
./storage/faiss_index/
├── index.faiss             # Binary FAISS index
└── metadata.pkl            # Pickled metadata list
```

**Index Type**: IndexFlatL2
- Exhaustive search (compares with all vectors)
- No approximation, 100% recall
- O(n) complexity but fast in practice for <1M vectors

**Similarity Computation**:
```
L2 Distance = √(∑(x_i - y_i)²)  [for normalized vectors, range: 0-2]

Similarity Score = 1 / (1 + L2_distance)  [normalized to 0-1]

Quality Threshold = 0.5  [configurable]
```

**Persistence**:
```python
# On add_embeddings():
FAISS Index  → faiss.write_index() → index.faiss
Metadata    → pickle.dump()        → metadata.pkl

# On load:
index.faiss  → faiss.read_index() → Restored Index
metadata.pkl → pickle.load()      → Restored Metadata
```

### 3. RAG Pipeline Layer (`src/rag/`)

#### Retriever (`retriever.py`)
```python
Retriever
├── add_documents()         # Add chunks to store
├── retrieve()              # Semantic search + ranking
├── clear()                 # Clear all vectors
└── get_stats()             # Statistics
```

**Retrieval Flow**:
```
User Query
    ↓
Generate Embedding (OpenAI API)
    ↓
Search Vector Store (L2 distance)
    ↓
Convert to Similarity Scores
    ↓
Apply Threshold Filter (default: 0.5)
    ↓
Return Top-K Results (default: 3)
    ↓
Sorted by Similarity Descending
```

**Output**:
```python
[
    {
        "text": "chunk text...",
        "page_number": 2,
        "source": "document.pdf",
        "chunk_index": 0,
        "similarity_score": 0.85
    },
    ...
]
```

#### QA Chain (`qa_chain.py`)
```python
QAChain
├── generate_answer()       # Main QA interface
├── _build_context()        # Format retrieved docs
├── _generate_llm_response()# Call LLM
└── _extract_citations()    # Format citations
```

**QA Flow**:
```
User Query + Chat History
    ↓
Retrieve Relevant Documents (via Retriever)
    ↓
Build Context String
    ├─ Format: [Document N - Page X from source]
    ├─ Include: First 500 chars of each chunk
    └─ Max: Top 3 chunks
    ↓
Build Prompt
    ├─ System: Emphasize grounding in context
    ├─ History: Last 6 messages (3 exchanges)
    ├─ Context: Retrieved document chunks
    └─ Query: User question
    ↓
Call LLM (OpenAI GPT-3.5-Turbo)
    ├─ Temperature: 0.7 (balanced)
    ├─ Model: gpt-3.5-turbo
    └─ Token limit: 4K (sufficient for context)
    ↓
Extract Answer + Format Citations
    ↓
Return Structured Response
```

**Response Structure**:
```python
{
    "answer": "The document discusses...",
    "sources": [
        {
            "text": "...",
            "page_number": 2,
            "similarity_score": 0.85,
            ...
        },
        ...
    ],
    "citations": [
        {
            "source_id": 1,
            "page": 2,
            "document": "document.pdf",
            "snippet": "...",
            "similarity_score": 0.85
        },
        ...
    ]
}
```

### 4. Application Layer (`app.py`)

#### Streamlit Interface
```
Sidebar                          Main Content
├─ PDF Upload                    ├─ Chat History
├─ Process Button                ├─ User Query Input
├─ Document Info                 └─ Assistant Response
├─ RAG Settings (k)                 ├─ Answer
├─ Clear Button                     └─ Citations (expandable)
└─ About Section
```

**Session State Management**:
```python
st.session_state
├─ qa_chain              # QAChain instance
├─ retriever             # Retriever instance
├─ pdf_loaded            # Boolean flag
├─ chat_history          # List of messages
├─ document_metadata     # PDF metadata
└─ k_results             # Current retrieval k
```

### 5. Utility Layer (`src/utils/`)

#### Logger (`logger.py`)
```python
setup_logger(name) → Logger
    ├─ Console Handler (stdout)
    ├─ Rotating File Handler
    │   ├─ Max Size: 10 MB
    │   ├─ Backups: 5 files
    │   └─ File: ./logs/rag_app.log
    └─ Format: timestamp - name - level - message
```

**Log Levels**:
- `DEBUG`: Detailed operations (save operations)
- `INFO`: Major steps (PDF loaded, chunks created)
- `WARNING`: Non-critical issues (metadata extraction failed)
- `ERROR`: Critical failures (API errors, parsing failures)

#### Helpers (`helpers.py`)
```python
clean_text()           # Remove extra whitespace
extract_page_numbers() # Track page numbers
format_citation()      # Pretty-print citations
batch_list()          # Split into batches
```

### 6. Configuration (`config.py`)

```python
Settings (Pydantic)
├─ OpenAI
│  ├─ openai_api_key
│  ├─ openai_model (gpt-3.5-turbo)
│  └─ embedding_model (text-embedding-3-small)
├─ Vector Store
│  ├─ vector_store_path (./storage/faiss_index)
│  └─ embedding_dimension (1536)
├─ Chunking
│  ├─ chunk_size (500)
│  └─ chunk_overlap (50)
├─ Retrieval
│  ├─ top_k_results (3)
│  └─ similarity_threshold (0.5)
└─ Logging
   ├─ log_level (INFO)
   └─ log_file (./logs/rag_app.log)
```

### 7. Evaluation Framework (`eval/`)

```python
RAGEvaluator
├─ evaluate_questions()    # Run tests
├─ _calculate_metrics()    # Compute scores
├─ _save_results()        # Export JSON
└─ print_results_table()  # Display table

TEST_QUESTIONS
├─ 8 generic questions
├─ Difficulty levels
└─ Coverage: main topic, authors, findings, data, conclusion, tables, references, summary
```

## Data Flows

### Flow 1: PDF Upload & Processing
```
PDF File (Streamlit Upload)
    ↓ (save to temp)
PDF Parser
    ├─ Extract pages with text + tables
    └─ Return pages + metadata
    ↓
Text Chunker
    ├─ Split each page into chunks
    └─ Attach page number + source
    ↓
Retriever.add_documents()
    ├─ OpenAI Embeddings API (batch)
    ├─ FAISS Vector Store (add vectors)
    └─ Save to ./storage/ (persistence)
    ↓
Session State Updated
    ├─ qa_chain ready
    ├─ chat_history reset
    └─ document_metadata stored
```

### Flow 2: User Query → Answer with Citations
```
User Query (Streamlit Input)
    ↓
QAChain.generate_answer()
    ├─ Call Retriever.retrieve(query)
    │   ├─ OpenAI Embedding API (query)
    │   ├─ FAISS Search (similarity)
    │   └─ Return top-k chunks
    ├─ Build Context String
    │   └─ Format: [Doc N - Page X] content...
    ├─ Build Prompt
    │   ├─ System: grounding instructions
    │   ├─ History: last 3 exchanges
    │   ├─ Context: retrieved chunks
    │   └─ Query: user question
    ├─ Call OpenAI ChatOpenAI API
    │   ├─ Model: gpt-3.5-turbo
    │   ├─ Messages: [system, history, context, query]
    │   └─ Temperature: 0.7
    ├─ Parse LLM Response
    ├─ Extract Citations
    │   └─ Page + source + snippet
    └─ Return Structured Response
    ↓
Streamlit UI
    ├─ Display Answer (green box)
    ├─ Display Citations (expandable)
    └─ Update Chat History
```

## External APIs & Dependencies

### 1. OpenAI APIs
```
OpenAI Embeddings (text-embedding-3-small)
├─ Input: Text chunks (1-8192 tokens)
├─ Output: Vector (1536 dimensions)
├─ Cost: $0.02 per 1M tokens
└─ Rate: ~1000/sec

OpenAI Chat (gpt-3.5-turbo)
├─ Input: Messages (4K token context)
├─ Output: Text response
├─ Cost: $0.0005 per 1K input tokens
└─ Latency: 1-2 seconds
```

### 2. LangChain
```
OpenAIEmbeddings
├─ Wraps OpenAI API
└─ Handles batching + error retry

ChatOpenAI
├─ Wraps OpenAI Chat API
├─ Message format handling
└─ Temperature/parameter control
```

### 3. FAISS
```
Local Library (CPU)
├─ No network calls
├─ Pure similarity search
└─ Persists locally
```

## Security & Privacy

### Data Handling
- **PDFs**: Processed locally, deleted after temp use
- **Embeddings**: Stored locally in ./storage/
- **API Keys**: Stored in .env (not committed)
- **Chat History**: In-memory only (session duration)

### API Security
- OpenAI API key validated on startup
- No sensitive data in logs
- Errors logged without exposing keys
- No data transmitted except to OpenAI APIs

## Performance Characteristics

### Time Complexity
```
PDF Processing: O(pages) where pages = num pages
Chunking:       O(words) where words = total words
Embedding:      O(chunks) where chunks = text chunks
Search:         O(vectors) = O(1) FAISS exhaustive
LLM:            Fixed ~1-2 seconds per query
```

### Space Complexity
```
Vectors:        O(chunks × 1536) floats ≈ 6KB per vector
Metadata:       O(chunks × metadata_size) ≈ 1-2KB per chunk
Index:          Same as vectors (FAISS uses dense format)
Chat History:   O(messages × avg_length)
```

### Example Numbers
- 100-page PDF: 1500-2000 chunks
- 1500 chunks: ~9MB embeddings + 3MB metadata = 12MB total
- Vector search: <50ms for 1M vectors

## Scaling Considerations

### Current Limitations
1. **Single-threaded**: FAISS doesn't parallelize searches
2. **In-memory**: Limited by available RAM
3. **Single document**: One PDF at a time

### Scaling Options

**For Multiple PDFs**:
```
Option 1: Multiple Vector Stores
├─ One FAISS per document
└─ Query all, rank results

Option 2: Namespace Filtering
├─ Single FAISS with document field
└─ Filter search by document
```

**For Larger Scale**:
```
Option 1: Distributed Vector DB (Qdrant)
├─ Multi-user support
├─ Partition data
└─ Horizontal scaling

Option 2: Managed Service (Pinecone)
├─ Fully managed
├─ Pay per request
└─ Automatic scaling
```

**For Concurrent Users**:
```
Option 1: FastAPI + Background Tasks
├─ Async document processing
├─ Queue-based submissions
└─ Multiple workers

Option 2: Docker + Kubernetes
├─ Containerize application
├─ Load balancing
└─ Auto-scaling
```

## Monitoring & Observability

### Logging Points
```
- PDF upload: filename, size, page count
- Chunking: chunks created, avg size
- Embedding: vectors added, timing
- Query: query text, retrieved chunks
- Answer: answer length, citations count
- Errors: full stack trace + context
```

### Metrics Tracked
```
- Total vectors in store
- Embedding generation time
- Search latency
- LLM response time
- Citation count per answer
- Error rate
```

### Log Levels by Component
```
pdf_parser    → INFO (major steps), WARNING (missing text)
chunker       → INFO (chunks created), WARNING (large chunks)
faiss_store   → DEBUG (save ops), INFO (add/search)
retriever     → INFO (retrieval), WARNING (no results)
qa_chain      → INFO (generation), ERROR (LLM fails)
app           → INFO (UI events), ERROR (user errors)
```

---

**Last Updated**: May 2026
**Architecture Version**: 1.0
**Status**: Production-Ready
