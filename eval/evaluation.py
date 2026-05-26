"""
Evaluation framework for RAG system testing.
Provides automated and manual evaluation capabilities.
"""

from typing import List, Dict, Any
import json
from datetime import datetime
from src.rag.qa_chain import QAChain
from src.utils.logger import setup_logger

logger = setup_logger(__name__)


class RAGEvaluator:
    """
    Evaluator for testing RAG system performance.
    Tests Q&A quality, citation generation, and retrieval accuracy.
    """

    def __init__(self, qa_chain: QAChain):
        """
        Initialize the evaluator.

        Args:
            qa_chain: QA chain instance to evaluate
        """
        self.qa_chain = qa_chain
        self.results: List[Dict[str, Any]] = []

    def evaluate_questions(
        self,
        questions: List[Dict[str, str]],
        save_results: bool = True
    ) -> Dict[str, Any]:
        """
        Evaluate QA chain on a set of questions.

        Args:
            questions: List of question dictionaries
            save_results: Whether to save results to file

        Returns:
            Evaluation results summary
        """
        logger.info(f"Starting evaluation on {len(questions)} questions")

        results = []
        for q_dict in questions:
            question = q_dict.get('question')
            q_id = q_dict.get('id', 'unknown')

            try:
                # Generate answer
                response = self.qa_chain.generate_answer(question)

                # Create evaluation record
                result = {
                    "question_id": q_id,
                    "question": question,
                    "answer": response.get("answer", ""),
                    "num_citations": len(response.get("citations", [])),
                    "num_sources": len(response.get("sources", [])),
                    "citations": response.get("citations", []),
                    "timestamp": datetime.now().isoformat(),
                    "has_answer": bool(response.get("answer", "").strip()),
                }

                results.append(result)
                logger.info(f"Q{q_id}: Generated answer with {result['num_citations']} citations")

            except Exception as e:
                logger.error(f"Error evaluating question {q_id}: {str(e)}")
                results.append({
                    "question_id": q_id,
                    "question": question,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })

        # Calculate metrics
        summary = self._calculate_metrics(results)

        # Save results if requested
        if save_results:
            self._save_results(results, summary)

        self.results = results
        return summary

    def _calculate_metrics(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Calculate evaluation metrics.

        Args:
            results: List of evaluation results

        Returns:
            Summary metrics dictionary
        """
        total_questions = len(results)
        successful = sum(1 for r in results if r.get('has_answer'))
        failed = sum(1 for r in results if 'error' in r)

        avg_citations = 0
        avg_sources = 0

        successful_results = [r for r in results if r.get('has_answer')]
        if successful_results:
            avg_citations = sum(r['num_citations'] for r in successful_results) / len(successful_results)
            avg_sources = sum(r['num_sources'] for r in successful_results) / len(successful_results)

        return {
            "total_questions": total_questions,
            "successful": successful,
            "failed": failed,
            "success_rate": (successful / total_questions * 100) if total_questions > 0 else 0,
            "avg_citations_per_answer": round(avg_citations, 2),
            "avg_sources_per_answer": round(avg_sources, 2),
            "timestamp": datetime.now().isoformat(),
        }

    def _save_results(
        self,
        results: List[Dict[str, Any]],
        summary: Dict[str, Any]
    ) -> None:
        """
        Save evaluation results to file.

        Args:
            results: Detailed results
            summary: Summary metrics
        """
        try:
            filename = f"evaluation_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"

            output = {
                "summary": summary,
                "details": results,
            }

            with open(filename, 'w') as f:
                json.dump(output, f, indent=2)

            logger.info(f"Saved evaluation results to {filename}")

        except Exception as e:
            logger.warning(f"Could not save evaluation results: {str(e)}")

    def print_results_table(self) -> None:
        """Print a formatted table of evaluation results."""
        if not self.results:
            print("No results to display")
            return

        print("\n" + "="*100)
        print(f"{'Q#':<5} {'Question':<50} {'Cited?':<10} {'Citations':<10} {'Status':<15}")
        print("="*100)

        for result in self.results:
            q_id = result.get('question_id', '?')
            question = result.get('question', '')[:45]
            citations = result.get('num_citations', 0)
            status = "✓ Success" if result.get('has_answer') else "✗ Failed"
            cited = "Yes" if citations > 0 else "No"

            print(f"{q_id:<5} {question:<50} {cited:<10} {citations:<10} {status:<15}")

        print("="*100 + "\n")


def evaluate_qa_chain(
    qa_chain: QAChain,
    questions: List[Dict[str, str]],
    print_table: bool = True
) -> Dict[str, Any]:
    """
    Convenience function to evaluate a QA chain.

    Args:
        qa_chain: QA chain to evaluate
        questions: List of test questions
        print_table: Whether to print results table

    Returns:
        Evaluation summary
    """
    evaluator = RAGEvaluator(qa_chain)
    summary = evaluator.evaluate_questions(questions)

    if print_table:
        evaluator.print_results_table()

    return summary
