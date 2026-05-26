"""
Standalone evaluation script for RAG system.
Run after uploading a PDF through the Streamlit app.
"""

import sys
from pathlib import Path

from config import settings
from src.rag import QAChain, Retriever
from eval import TEST_QUESTIONS, evaluate_qa_chain
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


def main():
    """Run evaluation on the RAG system."""
    print("\n" + "="*60)
    print("RAG System Evaluation")
    print("="*60 + "\n")

    # Check if vector store has data
    try:
        retriever = Retriever()
        stats = retriever.get_stats()
        total_vectors = stats['vector_store_stats']['total_vectors']

        if total_vectors == 0:
            print("⚠️  Vector store is empty!")
            print("Please upload and process a PDF in the Streamlit app first.")
            print(f"Vector store path: {settings.vector_store_path}")
            return

        print(f"✅ Found {total_vectors} vectors in store\n")

    except Exception as e:
        logger.error(f"Error checking vector store: {e}")
        print(f"❌ Error: {e}")
        return

    # Initialize QA chain
    try:
        print("Initializing QA chain...\n")
        qa_chain = QAChain(retriever)

        # Run evaluation
        print("Running evaluation on 8 test questions...\n")
        results = evaluate_qa_chain(
            qa_chain,
            TEST_QUESTIONS,
            print_table=True
        )

        # Print summary
        print("\n" + "="*60)
        print("EVALUATION SUMMARY")
        print("="*60)
        print(f"Total Questions: {results['total_questions']}")
        print(f"Successful: {results['successful']}")
        print(f"Failed: {results['failed']}")
        print(f"Success Rate: {results['success_rate']:.1f}%")
        print(f"Avg Citations per Answer: {results['avg_citations_per_answer']}")
        print(f"Avg Sources per Answer: {results['avg_sources_per_answer']}")
        print("="*60 + "\n")

        if results['success_rate'] == 100.0:
            print("🎉 All tests passed!\n")
        else:
            print(f"⚠️  {results['failed']} test(s) failed. Check logs for details.\n")

    except Exception as e:
        logger.error(f"Evaluation error: {e}")
        print(f"❌ Error during evaluation: {e}")
        print("\nCheck logs at: ./logs/rag_app.log")


if __name__ == "__main__":
    try:
        settings.validate_config()
        settings.get_paths()
        main()
    except ValueError as e:
        print(f"❌ Configuration Error: {e}")
        print("Please set OPENAI_API_KEY environment variable before running.")
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        print(f"❌ Fatal Error: {e}")
        sys.exit(1)
