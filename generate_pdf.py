"""
Generate a comprehensive PDF document for the RAG PDF Chat project.
"""

from datetime import datetime
from pathlib import Path

try:
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
except ImportError:
    print("Installing reportlab...")
    import subprocess
    subprocess.check_call(["pip", "install", "reportlab"])
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.units import inch
    from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak, Table, TableStyle
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY


def create_project_pdf():
    """Generate comprehensive project PDF."""

    pdf_path = "RAG_PDF_Chat_Documentation.pdf"
    doc = SimpleDocTemplate(pdf_path, pagesize=letter, topMargin=0.5*inch, bottomMargin=0.5*inch)

    # Container for the 'Flowable' objects
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=28,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=6,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    heading_style = ParagraphStyle(
        'CustomHeading',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=colors.HexColor('#667eea'),
        spaceAfter=8,
        spaceBefore=8,
        fontName='Helvetica-Bold'
    )

    subheading_style = ParagraphStyle(
        'CustomSubHeading',
        parent=styles['Heading3'],
        fontSize=11,
        textColor=colors.HexColor('#333333'),
        spaceAfter=6,
        fontName='Helvetica-Bold'
    )

    body_style = ParagraphStyle(
        'CustomBody',
        parent=styles['Normal'],
        fontSize=10,
        alignment=TA_JUSTIFY,
        spaceAfter=6,
        leading=14
    )

    # Title Page
    elements.append(Spacer(1, 1.5*inch))
    elements.append(Paragraph("RAG PDF Chat Assistant", title_style))
    elements.append(Spacer(1, 0.3*inch))
    elements.append(Paragraph("A Production-Grade Retrieval-Augmented Generation Application",
                            ParagraphStyle('subtitle', parent=styles['Normal'], fontSize=12,
                                         alignment=TA_CENTER, textColor=colors.HexColor('#666666'))))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(f"Generated: {datetime.now().strftime('%B %d, %Y')}",
                            ParagraphStyle('date', parent=styles['Normal'], fontSize=10,
                                         alignment=TA_CENTER, textColor=colors.HexColor('#999999'))))

    elements.append(PageBreak())

    # Table of Contents
    elements.append(Paragraph("Table of Contents", heading_style))
    elements.append(Spacer(1, 0.2*inch))
    toc_items = [
        "1. Executive Summary",
        "2. Project Overview",
        "3. Features & Capabilities",
        "4. Architecture & Components",
        "5. Technology Stack",
        "6. Installation & Setup",
        "7. Usage Guide",
        "8. Configuration",
        "9. API Documentation",
        "10. Performance & Scalability",
        "11. Security & Best Practices",
        "12. Troubleshooting",
        "13. Future Enhancements"
    ]

    for item in toc_items:
        elements.append(Paragraph(item, body_style))

    elements.append(PageBreak())

    # 1. Executive Summary
    elements.append(Paragraph("1. Executive Summary", heading_style))
    elements.append(Paragraph(
        "The RAG PDF Chat Assistant is a production-grade Retrieval-Augmented Generation (RAG) application "
        "built with Streamlit, LangChain, and OpenAI APIs. It enables users to upload any PDF document and have "
        "intelligent conversations with the content, receiving grounded answers backed by specific citations.",
        body_style
    ))
    elements.append(Paragraph(
        "<b>Key Highlights:</b><br/>"
        "• Supports any PDF document with robust text extraction<br/>"
        "• Semantic chunking preserves document structure<br/>"
        "• Vector embeddings enable fast similarity search<br/>"
        "• Citations include page numbers and text snippets<br/>"
        "• Chat history maintained throughout session<br/>"
        "• Production-grade logging and error handling<br/>"
        "• Fully modular and extensible architecture",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 2. Project Overview
    elements.append(Paragraph("2. Project Overview", heading_style))
    elements.append(Paragraph(
        "<b>Purpose:</b><br/>"
        "This project implements a complete RAG pipeline that bridges the gap between document understanding and "
        "large language models. Users can upload PDFs and ask natural language questions, receiving answers grounded "
        "in the document with proper citations.",
        body_style
    ))

    elements.append(Paragraph(
        "<b>Core Components:</b><br/>"
        "• <b>Ingestion:</b> PDF parsing with pdfplumber, semantic text chunking<br/>"
        "• <b>Embeddings:</b> OpenAI text-embedding-3-small (1536 dimensions)<br/>"
        "• <b>Vector Store:</b> FAISS for efficient similarity search with local persistence<br/>"
        "• <b>RAG Pipeline:</b> LangChain integration for retrieval and LLM-based QA<br/>"
        "• <b>Frontend:</b> Streamlit for interactive user interface<br/>"
        "• <b>Logging:</b> Production-grade rotating file handlers",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 3. Features & Capabilities
    elements.append(Paragraph("3. Features & Capabilities", heading_style))

    elements.append(Paragraph("<b>User Features:</b>", subheading_style))
    elements.append(Paragraph(
        "• Upload and process PDF documents<br/>"
        "• Ask natural language questions about document content<br/>"
        "• Receive grounded answers with citations<br/>"
        "• View page numbers and text snippets for sources<br/>"
        "• Ask follow-up questions with chat context<br/>"
        "• Search chat history<br/>"
        "• Adjustable retrieval parameters",
        body_style
    ))

    elements.append(Paragraph("<b>Developer Features:</b>", subheading_style))
    elements.append(Paragraph(
        "• Modular architecture (7 main modules)<br/>"
        "• Full type hints for code safety<br/>"
        "• Comprehensive docstrings<br/>"
        "• Production logging with rotating handlers<br/>"
        "• Environment-based configuration<br/>"
        "• Evaluation framework with test questions<br/>"
        "• Easy to extend and customize",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 4. Architecture & Components
    elements.append(Paragraph("4. Architecture & Components", heading_style))

    elements.append(Paragraph("<b>Layered Architecture:</b>", subheading_style))
    elements.append(Paragraph(
        "<b>Layer 1 - UI:</b> Streamlit interface with chat, search, and document management<br/>"
        "<b>Layer 2 - Ingestion:</b> PDF parsing and semantic text chunking<br/>"
        "<b>Layer 3 - Vector Store:</b> FAISS embeddings with local persistence<br/>"
        "<b>Layer 4 - RAG:</b> Retrieval and LLM-based question answering<br/>"
        "<b>Layer 5 - APIs:</b> OpenAI embeddings and chat completion<br/>"
        "<b>Layer 6 - Utils:</b> Logging, configuration, and helpers<br/>"
        "<b>Layer 7 - Evaluation:</b> Testing framework with metrics",
        body_style
    ))

    elements.append(Paragraph("<b>Key Modules:</b>", subheading_style))

    # Module table
    module_data = [
        ['Module', 'Purpose', 'Key Classes'],
        ['src/ingestion/', 'PDF processing', 'PDFParser, TextChunker'],
        ['src/vector_store/', 'Vector storage', 'FAISSVectorStore'],
        ['src/rag/', 'RAG pipeline', 'Retriever, QAChain'],
        ['src/utils/', 'Utilities', 'Logger, Helpers'],
        ['eval/', 'Testing', 'RAGEvaluator, TestQuestions']
    ]

    module_table = Table(module_data, colWidths=[1.5*inch, 2*inch, 2*inch])
    module_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 9),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    elements.append(module_table)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 5. Technology Stack
    elements.append(Paragraph("5. Technology Stack", heading_style))

    tech_data = [
        ['Component', 'Technology', 'Version', 'Purpose'],
        ['Frontend', 'Streamlit', '>=1.35.0', 'Web UI'],
        ['PDF Processing', 'pdfplumber', '>=0.10.3', 'Text extraction'],
        ['Embeddings', 'OpenAI', '>=1.10.0', 'text-embedding-3-small'],
        ['Vector DB', 'FAISS', '>=1.13.0', 'Similarity search'],
        ['LLM', 'LangChain', '>=0.1.14', 'RAG orchestration'],
        ['Chat', 'OpenAI', 'gpt-3.5-turbo', 'Answer generation'],
        ['Config', 'Pydantic', '>=2.5.0', 'Settings management'],
        ['Logging', 'Python', 'built-in', 'Rotating file handlers']
    ]

    tech_table = Table(tech_data, colWidths=[1.2*inch, 1.5*inch, 1*inch, 2.3*inch])
    tech_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    elements.append(tech_table)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 6. Installation & Setup
    elements.append(Paragraph("6. Installation & Setup", heading_style))

    elements.append(Paragraph("<b>Prerequisites:</b>", subheading_style))
    elements.append(Paragraph(
        "• Python 3.8 or higher<br/>"
        "• OpenAI API key<br/>"
        "• ~500MB free disk space<br/>"
        "• pip package manager",
        body_style
    ))

    elements.append(Paragraph("<b>Installation Steps:</b>", subheading_style))
    elements.append(Paragraph(
        "1. Create virtual environment: <i>python -m venv myenv</i><br/>"
        "2. Activate: <i>myenv\\Scripts\\Activate.ps1</i> (Windows) or <i>source myenv/bin/activate</i> (Unix)<br/>"
        "3. Install dependencies: <i>pip install -r requirements.txt</i><br/>"
        "4. Copy config: <i>cp .env.example .env</i><br/>"
        "5. Add API key to .env file<br/>"
        "6. Run app: <i>streamlit run app.py</i>",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 7. Usage Guide
    elements.append(Paragraph("7. Usage Guide", heading_style))

    elements.append(Paragraph("<b>Basic Workflow:</b>", subheading_style))
    elements.append(Paragraph(
        "1. <b>Upload PDF:</b> Click file uploader in sidebar, select your PDF<br/>"
        "2. <b>Process:</b> Click 'Process PDF' button, wait for completion<br/>"
        "3. <b>Ask Questions:</b> Type a question in the message box<br/>"
        "4. <b>View Answer:</b> Answer displays with citations<br/>"
        "5. <b>Follow Up:</b> Ask related questions naturally",
        body_style
    ))

    elements.append(Paragraph("<b>Tips & Tricks:</b>", subheading_style))
    elements.append(Paragraph(
        "• Start with general questions about document content<br/>"
        "• Use specific keywords for better retrieval<br/>"
        "• Adjust 'Number of documents to retrieve' for different needs<br/>"
        "• Use search box to find previous conversations<br/>"
        "• Check sources for answer context and accuracy",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 8. Configuration
    elements.append(Paragraph("8. Configuration", heading_style))

    elements.append(Paragraph(
        "Configuration is managed through environment variables in the .env file:",
        body_style
    ))

    config_data = [
        ['Variable', 'Default', 'Purpose'],
        ['OPENAI_API_KEY', 'Required', 'OpenAI API authentication'],
        ['OPENAI_MODEL', 'gpt-3.5-turbo', 'LLM model to use'],
        ['EMBEDDING_MODEL', 'text-embedding-3-small', 'Embedding model'],
        ['CHUNK_SIZE', '500', 'Text chunk size in tokens'],
        ['CHUNK_OVERLAP', '50', 'Overlap between chunks'],
        ['TOP_K_RESULTS', '3', 'Number of documents to retrieve'],
        ['SIMILARITY_THRESHOLD', '0.5', 'Minimum similarity score'],
        ['LOG_LEVEL', 'INFO', 'Logging verbosity level']
    ]

    config_table = Table(config_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
    config_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#667eea')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, 0), 9),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ('FONTSIZE', (0, 1), (-1, -1), 8),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.lightgrey])
    ]))

    elements.append(config_table)
    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 9. API Documentation
    elements.append(Paragraph("9. API Documentation", heading_style))

    elements.append(Paragraph("<b>Retriever Class</b>", subheading_style))
    elements.append(Paragraph(
        "<i>add_documents(chunks)</i> - Add document chunks to vector store<br/>"
        "<i>retrieve(query, k)</i> - Search for relevant documents<br/>"
        "<i>clear()</i> - Clear all documents from store",
        body_style
    ))

    elements.append(Paragraph("<b>QAChain Class</b>", subheading_style))
    elements.append(Paragraph(
        "<i>generate_answer(query, chat_history, k)</i> - Generate answer with citations<br/>"
        "<i>clear_context()</i> - Clear all documents",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 10. Performance & Scalability
    elements.append(Paragraph("10. Performance & Scalability", heading_style))

    elements.append(Paragraph("<b>Performance Metrics:</b>", subheading_style))
    elements.append(Paragraph(
        "• PDF Processing: 2-5 seconds for 100-page document<br/>"
        "• Embedding Generation: 1-2 seconds per batch<br/>"
        "• Similarity Search: <50ms with FAISS<br/>"
        "• LLM Response: 1-2 seconds per query",
        body_style
    ))

    elements.append(Paragraph("<b>Cost Estimates:</b>", subheading_style))
    elements.append(Paragraph(
        "• Embeddings: $0.02 per 1M tokens (~$0.01 per 100-page PDF)<br/>"
        "• LLM: $0.0005 per 1K tokens (~$0.01 per 20 queries)<br/>"
        "• Total: ~$0.02 per PDF + variable per query",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 11. Security & Best Practices
    elements.append(Paragraph("11. Security & Best Practices", heading_style))

    elements.append(Paragraph(
        "• Keep API keys in .env file (never commit to git)<br/>"
        "• Use environment-based configuration<br/>"
        "• PDFs processed locally, not uploaded to cloud<br/>"
        "• Vector embeddings stored locally<br/>"
        "• Comprehensive error logging for debugging<br/>"
        "• Input validation on all user inputs<br/>"
        "• Regular security updates for dependencies",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 12. Troubleshooting
    elements.append(Paragraph("12. Troubleshooting", heading_style))

    elements.append(Paragraph(
        "<b>Streamlit not found:</b> Run <i>pip install -r requirements.txt</i><br/><br/>"
        "<b>OPENAI_API_KEY error:</b> Check .env file contains valid API key<br/><br/>"
        "<b>Pydantic import error:</b> Run <i>pip install pydantic-settings</i><br/><br/>"
        "<b>LangChain import error:</b> Run <i>pip install --upgrade langchain langchain-core</i><br/><br/>"
        "<b>No citations shown:</b> Try increasing TOP_K_RESULTS in .env<br/><br/>"
        "<b>Slow performance:</b> Reduce CHUNK_SIZE or TOP_K_RESULTS<br/><br/>"
        "<b>PDF processing fails:</b> Ensure PDF is not corrupted, try different file",
        body_style
    ))

    elements.append(Spacer(1, 0.2*inch))
    elements.append(PageBreak())

    # 13. Future Enhancements
    elements.append(Paragraph("13. Future Enhancements", heading_style))

    elements.append(Paragraph(
        "• <b>OCR Support:</b> Handle scanned PDFs with Tesseract/EasyOCR<br/>"
        "• <b>Multi-Document:</b> Search across multiple uploaded PDFs<br/>"
        "• <b>Distributed Vector DB:</b> Scale to millions of documents with Qdrant<br/>"
        "• <b>User Authentication:</b> Multi-user support with session management<br/>"
        "• <b>Caching:</b> Cache embeddings to reduce API calls<br/>"
        "• <b>Advanced Chunking:</b> Semantic chunking with sentence-transformers<br/>"
        "• <b>Analytics:</b> Track usage, performance, and cost metrics<br/>"
        "• <b>Custom Models:</b> Support for local LLMs and embeddings",
        body_style
    ))

    elements.append(Spacer(1, 1*inch))
    elements.append(PageBreak())

    # Final page
    elements.append(Spacer(1, 2*inch))
    elements.append(Paragraph(
        "RAG PDF Chat Assistant<br/>Production-Grade Implementation",
        ParagraphStyle('final', parent=styles['Normal'], fontSize=18,
                     alignment=TA_CENTER, textColor=colors.HexColor('#667eea'), fontName='Helvetica-Bold')
    ))
    elements.append(Spacer(1, 0.5*inch))
    elements.append(Paragraph(
        "Built with Streamlit, LangChain, OpenAI, and FAISS<br/>"
        f"Documentation Generated: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}",
        ParagraphStyle('footer', parent=styles['Normal'], fontSize=10,
                     alignment=TA_CENTER, textColor=colors.HexColor('#999999'))
    ))

    # Build PDF
    doc.build(elements)
    print(f"✅ PDF generated successfully: {pdf_path}")
    return pdf_path


if __name__ == "__main__":
    pdf_file = create_project_pdf()
    print(f"📄 Document saved to: {Path(pdf_file).absolute()}")
