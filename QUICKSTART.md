# Quick Start Guide

Get the RAG PDF Chat application running in 5 minutes.

## Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one at https://platform.openai.com/api-keys)
- ~500MB free disk space

## Installation (Step-by-Step)

### 1. Setup Environment
```bash
# Navigate to the project directory
cd rag-pdf-chatbot

# Create virtual environment
python -m venv venv

# Activate it
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Configure API Key
```bash
# Copy example config
cp .env.example .env

# Edit .env and add your OpenAI API key
# On Windows: notepad .env
# On Mac/Linux: nano .env
```

Add this line to `.env`:
```
OPENAI_API_KEY=sk-your-api-key-here
```

### 4. Run the Application
```bash
streamlit run app.py
```

The app will open at `http://localhost:8501`

## First Use

### Step 1: Upload a PDF
1. Click the file uploader in the left sidebar
2. Select any PDF file (or use a sample PDF)
3. Click "📤 Process PDF" button
4. Wait for processing (you'll see status messages)

### Step 2: Ask Questions
1. In the main area, type a question about the PDF
2. Click "Send" button
3. Wait for the answer
4. View citations below the answer

### Step 3: Continue Conversation
- Ask follow-up questions
- Chat history is maintained automatically
- References are shown for each answer

## Example Questions to Try

After uploading a PDF, try these questions:

```
"What is the main topic of this document?"
"What are the key findings?"
"Can you summarize this in 2-3 sentences?"
"What data or statistics are mentioned?"
"Who is the author?"
```

## Configuration

### Adjust Retrieval Results
In the sidebar, change "Number of documents to retrieve" (1-10):
- **Lower (1-2)**: Faster, more focused
- **Higher (5-10)**: More context, slower

### Change Models

Edit `.env` to use different models:

**Embedding Model** (faster/cheaper):
```
EMBEDDING_MODEL=text-embedding-3-small  # Current (recommended)
EMBEDDING_MODEL=text-embedding-ada-002  # Older, similar quality
```

**LLM Model** (smarter but slower):
```
OPENAI_MODEL=gpt-3.5-turbo              # Current (recommended)
OPENAI_MODEL=gpt-4                      # Smarter but 20x slower
```

## Troubleshooting

### "OPENAI_API_KEY is not set"
- Make sure .env file exists in the project root
- Verify OPENAI_API_KEY is in the .env file
- Restart the app after adding the key

### "PDF processing failed"
- Check that the PDF isn't corrupted
- Try a different PDF file
- Check console for detailed error messages

### "No citations shown"
- The question may not match the document content
- Try different retrieval settings (increase k in sidebar)
- Verify the PDF was processed successfully

### App runs very slowly
- Reduce "Number of documents to retrieve" in sidebar
- Use text-embedding-3-small (faster than ada-002)
- Close other applications

## Testing the System

Run the evaluation framework:

```bash
python run_evaluation.py
```

This will:
1. Load your processed PDF
2. Ask 8 test questions
3. Print accuracy metrics
4. Save results to JSON file

## Project Files

### Core Application
- `app.py` - Streamlit main application
- `config.py` - Configuration management
- `requirements.txt` - Python dependencies

### Source Modules
- `src/ingestion/` - PDF parsing and chunking
- `src/vector_store/` - FAISS vector database
- `src/rag/` - Retrieval and QA chain
- `src/utils/` - Logging and helpers

### Evaluation & Testing
- `eval/` - Test framework
- `run_evaluation.py` - Standalone evaluation script
- `demo.py` - Interactive demo

### Documentation
- `README.md` - Comprehensive documentation
- `ARCHITECTURE.md` - Technical architecture
- `PROMPT_LOGS.md` - Development logs
- `QUICKSTART.md` - This file

### Storage
- `storage/` - Vector database persistence
- `logs/` - Application logs

## Next Steps

### Learn More
- Read `README.md` for comprehensive docs
- Check `ARCHITECTURE.md` for technical details
- Review `PROMPT_LOGS.md` for development approach

### Customize
- Modify chunking strategy in `src/ingestion/chunker.py`
- Adjust LLM prompt in `src/rag/qa_chain.py`
- Add custom metrics in `eval/evaluation.py`

### Deploy
1. Set up a proper environment with secrets management
2. Use Docker for containerization
3. Deploy to cloud (AWS, GCP, Azure, Heroku)
4. Add authentication layer

## Performance Tips

**For faster responses:**
- Reduce chunk size (default 500) in `.env`
- Reduce retrieval k (default 3) in sidebar
- Use text-embedding-3-small (default)

**For better answers:**
- Increase retrieval k (5-10)
- Use gpt-4 instead of gpt-3.5-turbo
- Upload longer PDFs (more context)

## Cost Estimate

For testing and light usage:

```
Embeddings:  $0.02 per 1M tokens  (~$0.01 per 100-page PDF)
LLM:         $0.0005 per 1K tokens (~$0.01 per 20 queries)
Storage:     Free (local FAISS)
Total:       ~$0.02 per PDF + $0.01 per 20 queries
```

## API Rate Limits

OpenAI has rate limits (depending on your plan):
- Embeddings: ~3,500 requests per minute
- Chat: ~500 requests per minute

For production, consider:
- Caching embeddings
- Batch processing
- Upgrading API plan

## Getting Help

1. **Check the logs**: `./logs/rag_app.log`
2. **Review README.md**: Comprehensive documentation
3. **Check ARCHITECTURE.md**: How things work
4. **Run demo.py**: Interactive example

## Example Workflow

```bash
# 1. Setup (first time only)
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
# Edit .env with your API key

# 2. Run app
streamlit run app.py

# 3. Upload PDF via UI
# (Use Streamlit interface)

# 4. Test system
python run_evaluation.py

# 5. Try demo
python demo.py
```

---

**Ready to start?** Run `streamlit run app.py` now!

For questions, check `README.md` or `ARCHITECTURE.md`.
