# AI Assistant Prompt Logs

This document records the prompts and iterations used to build the RAG PDF Chat Assistant.

## Project Overview

**Assignment**: Build a Streamlit app that lets users upload any PDF and chat with it using RAG.

**Key Requirements**:
- Streamlit UI with PDF upload and persistent chat history
- PDF processing pipeline with text extraction and chunking
- Vector embeddings and similarity search
- LLM-based Q&A with citations
- Modular, production-grade code

---

## Session 1: Initial System Design & Architecture Planning

### Prompt 1: Architecture Definition
**Context**: Starting the RAG system from scratch, needed to plan the overall architecture.

**Prompt Used**:
```
I need to build a production-grade RAG application with these requirements:
1. Streamlit UI for PDF upload and chat
2. Robust PDF text extraction with chunking
3. Vector embeddings and FAISS vector store
4. LLM-based Q&A with citations
5. Production logging with rotating files
6. Modular, well-documented code

Create a comprehensive project structure with:
- Separate modules for ingestion, vector store, RAG, and utils
- Clear separation of concerns
- Comprehensive docstrings
- Type hints throughout
- Configuration management with environment variables
- Logging module with rotating handlers
```

**Key Decisions Made**:
- **Embedding Model**: text-embedding-3-small (1536 dims, cost-effective)
- **Vector Store**: FAISS with local persistence
- **LLM**: GPT-3.5-Turbo (fast, cost-effective for chat)
- **Chunking Strategy**: Recursive semantic splitting (paragraph → sentence → word)
- **Citation Format**: Page number + snippet + similarity score

---

## Session 2: Core Modules Implementation

### Prompt 2: PDF Parser Implementation
**Context**: Building robust PDF text extraction with pdfplumber.

**Prompt Used**:
```
Create a PDFParser class that:
1. Uses pdfplumber for text extraction
2. Extracts tables and preserves their structure
3. Tracks page numbers for each chunk
4. Handles PDF metadata (title, author, pages)
5. Returns structured page data with metadata
6. Includes comprehensive error handling and logging

The parser should be resilient to:
- Blank pages
- Images without OCR
- Complex table layouts
- Large PDFs
```

**Implementation Details**:
- Uses pdfplumber's native table extraction
- Tracks page metadata for citations
- Graceful handling of missing text with informative messages
- Comprehensive error logging at each step

### Prompt 3: Semantic Text Chunking
**Context**: Implementing intelligent text chunking that preserves context.

**Prompt Used**:
```
Create a TextChunker class with:
1. Recursive splitting strategy respecting semantic boundaries
2. Fallback chain: paragraphs → lines → sentences → words
3. Configurable chunk size and overlap
4. Preservation of paragraph structure
5. Overlap addition for context continuity

The chunking should:
- Be efficient for large documents
- Preserve semantic meaning
- Handle edge cases (empty text, very large chunks)
- Support metadata attachment (page number, source)
```

**Design Decisions**:
- Recursive strategy prevents truncation of important content
- Overlap mechanism ensures context preservation between chunks
- Default size 500 tokens balances context and relevance
- Paragraph-first approach maintains semantic boundaries

### Prompt 4: FAISS Vector Store
**Context**: Building a persistent, efficient vector store.

**Prompt Used**:
```
Create a FAISSVectorStore class with:
1. IndexFlatL2 for exhaustive similarity search
2. Persistent storage (save/load index and metadata)
3. Efficient similarity search with L2 distance
4. Metadata storage alongside embeddings
5. Statistics and monitoring capabilities
6. Error handling for corrupted indexes

Features needed:
- Add embeddings with associated metadata
- Search with configurable k parameter
- Clear function to reset the store
- Save/load from disk automatically
```

**Implementation Details**:
- L2 distance chosen for normalized embeddings
- Separate pickle storage for metadata
- Automatic persistence after each operation
- Graceful recovery from corrupted index

---

## Session 3: RAG Pipeline & LLM Integration

### Prompt 5: Semantic Retriever
**Context**: Building the retrieval component that finds relevant documents.

**Prompt Used**:
```
Create a Retriever class that:
1. Uses OpenAI embeddings API (text-embedding-3-small)
2. Generates embeddings for documents and queries
3. Performs similarity search in vector store
4. Applies similarity threshold filtering
5. Returns top-K results with similarity scores

Retrieval strategy should:
- Convert L2 distance to similarity scores (0-1)
- Apply configurable threshold (default 0.5)
- Support variable k parameter
- Cache embeddings appropriately
- Log all retrieval operations
```

**Design Decisions**:
- Similarity = 1/(1+L2_distance) for interpretability
- Threshold filtering prevents low-quality results
- Separate retrieval from LLM to enable testing

### Prompt 6: QA Chain with Citations
**Context**: Building the final LLM component with proper citation extraction.

**Prompt Used**:
```
Create a QAChain class that:
1. Uses ChatOpenAI for LLM-based responses
2. Combines retrieved context with user query
3. Includes chat history in prompt for follow-ups
4. Extracts and formats citations from sources
5. Returns structured response with answer + citations

The QA chain should:
- Build rich context from multiple documents
- Reference document sources in prompt
- Extract page numbers and snippets for citations
- Support conversation history
- Handle empty retrieval gracefully

Prompt should emphasize:
- Answering only with provided context
- Being clear about information sources
- Referencing specific documents
```

**Implementation Details**:
- System prompt emphasizes factual grounding
- Last 6 messages (3 exchanges) included for context
- Citations include page, source, and snippet
- Graceful handling when no relevant documents found

---

## Session 4: Streamlit UI & Integration

### Prompt 7: Streamlit Application
**Context**: Building the user-facing web interface.

**Prompt Used**:
```
Create a Streamlit app (app.py) that:
1. Provides PDF upload interface
2. Displays document metadata after processing
3. Maintains persistent chat history
4. Shows citations with each answer
5. Displays retriever statistics
6. Allows configurable retrieval parameters

UI Features:
- Sidebar for controls (upload, settings, info)
- Main area for chat conversation
- Citation display with expandable snippets
- Error messages with helpful context
- Progress indicators during processing

Must handle:
- Large PDF files
- Long conversations
- Quick reloads without reprocessing
```

**Design Decisions**:
- Left sidebar for controls (upload, settings)
- Main content for chat
- Session state for persistence
- Color-coded boxes for answers/citations/errors

---

## Session 5: Configuration & Utilities

### Prompt 8: Configuration Management
**Context**: Setting up environment-based configuration.

**Prompt Used**:
```
Create a config.py with:
1. Pydantic BaseSettings for type-safe config
2. Support for .env file loading
3. Validation of required settings
4. Path creation for storage directories
5. Default values for all parameters

Must include:
- OpenAI API key validation
- Model specifications
- Chunk size and overlap
- Vector store path
- Logging configuration
- Retrieval parameters
```

**Configuration Parameters**:
- All environment-based for flexibility
- Defaults provided for all non-required values
- Validation ensures required keys are set
- Automatic directory creation

### Prompt 9: Logging Module
**Context**: Building production-grade logging.

**Prompt Used**:
```
Create a logging module (logger.py) with:
1. Rotating file handlers (10MB per file, 5 backups)
2. Console and file output
3. Structured logging format with timestamps
4. Configurable log levels per logger
5. Centralized logger creation function

Features:
- Prevent duplicate handlers
- Automatic directory creation
- Clean formatting for readability
- Separate loggers for different modules
- Persistent logs across sessions
```

**Implementation**:
- RotatingFileHandler for file management
- Consistent format across all loggers
- Info level by default
- Separate console and file streams

---

## Session 6: Testing & Evaluation

### Prompt 10: Evaluation Framework
**Context**: Building tools to test system performance.

**Prompt Used**:
```
Create an evaluation framework with:
1. Test questions covering document aspects
2. Generic questions that work with any PDF
3. Difficulty levels (easy, medium, hard)
4. Evaluation metrics (success rate, citations, sources)
5. Results saving to JSON with timestamps
6. Pretty-printed results table

Should measure:
- Answer generation success rate
- Citation quality and quantity
- Document retrieval accuracy
- System reliability
```

**Test Coverage**:
- 8 questions covering different document aspects
- Difficulty levels for comprehensive testing
- Metrics for citation quality
- JSON export for analysis

---

## Key Iterations & Improvements

### Iteration 1: Error Handling
**Challenge**: PDFs could fail at various stages.

**Solution**:
- Try-catch blocks at each major step
- Graceful fallbacks (e.g., default page 1 if extraction fails)
- Informative error messages for users
- Comprehensive logging of failures

### Iteration 2: Citation Quality
**Challenge**: Citations needed to be useful and accurate.

**Solution**:
- Include similarity scores
- Provide text snippets (first 150 chars)
- Track source documents
- Show confidence levels

### Iteration 3: Chunking Strategy
**Challenge**: Chunks too small = lost context, too large = lost relevance.

**Solution**:
- Recursive splitting to find semantic boundaries
- Configurable sizes for flexibility
- Overlap between chunks
- Paragraph-first approach for structure preservation

### Iteration 4: Prompt Engineering
**Challenge**: LLM tends to make up information outside context.

**Solution**:
- System prompt emphasizes grounding
- Clear instructions to reference sources
- Explicit warning about staying within context
- Example format for citations

---

## Design Patterns Used

### 1. Modular Architecture
```
ingestion/ → vector_store/ → rag/ → app.py
```
Each component is independent and testable.

### 2. Configuration Pattern
```
.env → config.py → modules
```
Centralized configuration with environment variables.

### 3. Logging Pattern
```
setup_logger(module_name) → rotating handler
```
Consistent logging across all modules.

### 4. Session State Pattern (Streamlit)
```
st.session_state → persistence during session
```
Maintains chat history and PDF state.

---

## Performance Considerations

### 1. Embedding Generation
- **Cost**: $0.02 per 1M tokens with text-embedding-3-small
- **Speed**: ~1000 embeddings per second
- **Storage**: 1536 dims × float32 = 6KB per vector

### 2. Similarity Search
- **Time**: FAISS IndexFlatL2 is O(n) exhaustive search
- **Alternative**: Could use HNSW index for approximate search
- **Current**: Sufficient for <1M documents

### 3. LLM Calls
- **Cost**: ~$0.0005 per 1K input tokens (gpt-3.5-turbo)
- **Latency**: ~1-2 seconds per query
- **Optimization**: Could batch multiple questions

---

## Known Limitations & Future Improvements

### Current Limitations
1. No OCR for scanned PDFs
2. Single-threaded FAISS operations
3. Limited to document context window
4. No multi-user support

### Potential Improvements
1. **OCR Integration**: Add Tesseract/EasyOCR for scanned PDFs
2. **Scaling**: Use Qdrant/Weaviate for distributed search
3. **Caching**: Cache embeddings to reduce API calls
4. **Multi-user**: Add user sessions and persistence
5. **Advanced Chunking**: Implement semantic chunking with sentence-transformers

---

## Summary

This RAG system was built following:
- **Best Practices**: Modular design, proper logging, type hints, documentation
- **Production Standards**: Error handling, configuration management, metrics
- **User Experience**: Intuitive Streamlit interface, clear citations, chat history
- **Flexibility**: Configurable parameters, support for custom models

The system successfully bridges the gap between document understanding and LLM capabilities through retrieval-augmented generation, providing grounded, cited answers to user questions.

---

**Total Prompts Used**: 10 major iterations + numerous refinements
**Development Approach**: Iterative refinement with focus on production quality
**Testing**: Unit-testable components with evaluation framework
