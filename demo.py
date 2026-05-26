"""
Demo script showing programmatic usage of the RAG system.
This demonstrates all the core components working together.
"""

import sys
from config import settings
from src.ingestion import PDFParser, TextChunker
from src.rag import Retriever, QAChain
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def demo_rag_pipeline(pdf_path: str, questions: list):
    """
    Demonstrate the complete RAG pipeline.

    Args:
        pdf_path: Path to PDF file
        questions: List of questions to ask
    """
    print("\n" + "="*70)
    print("RAG PIPELINE DEMONSTRATION")
    print("="*70 + "\n")

    # Step 1: PDF Parsing
    print("Step 1: PDF PARSING")
    print("-" * 70)
    try:
        parser = PDFParser(pdf_path)
        pages = parser.extract_text()
        metadata = parser.get_metadata()

        print(f"✅ Parsed PDF: {metadata['title']}")
        print(f"   - Pages: {metadata['pages']}")
        print(f"   - Author: {metadata['author']}\n")

    except Exception as e:
        print(f"❌ Error parsing PDF: {e}\n")
        return

    # Step 2: Text Chunking
    print("Step 2: TEXT CHUNKING")
    print("-" * 70)
    try:
        chunker = TextChunker(
            chunk_size=settings.chunk_size,
            chunk_overlap=settings.chunk_overlap
        )

        all_chunks = []
        for page in pages:
            chunks = chunker.chunk_text(
                text=page['text'],
                page_number=page['page_number'],
                source=metadata['title']
            )
            all_chunks.extend(chunks)

        print(f"✅ Created {len(all_chunks)} chunks")
        print(f"   - Chunk size: {settings.chunk_size} tokens")
        print(f"   - Overlap: {settings.chunk_overlap} tokens")
        print(f"   - Sample chunk length: {len(all_chunks[0]['text']) if all_chunks else 0} chars\n")

    except Exception as e:
        print(f"❌ Error chunking text: {e}\n")
        return

    # Step 3: Embeddings & Vector Store
    print("Step 3: EMBEDDINGS & VECTOR STORE")
    print("-" * 70)
    try:
        retriever = Retriever()
        retriever.add_documents(all_chunks)

        stats = retriever.get_stats()
        print(f"✅ Generated embeddings and stored vectors")
        print(f"   - Embedding model: {stats['embedding_model']}")
        print(f"   - Dimension: {stats['embedding_dimension']}")
        print(f"   - Total vectors: {stats['vector_store_stats']['total_vectors']}\n")

    except Exception as e:
        print(f"❌ Error with embeddings: {e}\n")
        return

    # Step 4: Q&A with RAG
    print("Step 4: Q&A WITH RETRIEVAL-AUGMENTED GENERATION")
    print("-" * 70)

    try:
        qa_chain = QAChain(retriever)

        for i, question in enumerate(questions, 1):
            print(f"\nQuestion {i}: {question}")
            print("-" * 70)

            try:
                response = qa_chain.generate_answer(question)

                # Print answer
                print(f"Answer: {response['answer']}\n")

                # Print citations
                citations = response.get('citations', [])
                if citations:
                    print("Citations:")
                    for j, citation in enumerate(citations, 1):
                        print(f"  [{j}] {citation['document']} - Page {citation['page']}")
                        print(f"      Relevance: {citation['similarity_score']:.2%}")
                        print(f"      Snippet: \"{citation['snippet'][:80]}...\"\n")
                else:
                    print("(No citations found)\n")

            except Exception as e:
                print(f"Error answering question: {e}\n")

    except Exception as e:
        print(f"❌ Error with QA chain: {e}\n")
        return

    print("="*70)
    print("✅ Demo completed successfully!")
    print("="*70 + "\n")


def main():
    """Main demo function."""
    print("\nWelcome to the RAG System Demo!")
    print("This demonstrates all components working together.\n")

    # Get PDF path from user
    pdf_path = input("Enter path to your PDF file: ").strip()

    if not pdf_path or not pdf_path.lower().endswith('.pdf'):
        print("❌ Invalid PDF path")
        return

    # Define demo questions
    demo_questions = [
        "What is the main topic of this document?",
        "What are the key findings or conclusions?",
        "Are there any statistics or data presented?",
    ]

    # Run demo
    try:
        settings.validate_config()
        settings.get_paths()
        demo_rag_pipeline(pdf_path, demo_questions)

    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please set OPENAI_API_KEY environment variable.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal Error: {e}")


if __name__ == "__main__":
    main()
