from core.extensions import exam_prompts, questions
from core.config import Config

class ExamFlow:
    def __init__(self, llm, evaluator, exam_name='basic_programming'):
        self.llm = llm
        self.evaluator = evaluator
        exam_data = questions.get_exam_questions(exam_name)
        self.subject = exam_data['subject']
        self.questions = exam_data['questions']
        self.total_questions = len(self.questions)

    def get_welcome_message(self):
        return exam_prompts.ExamPrompts.WELCOME_MESSAGE.format(
            subject=self.subject,
            question_count=self.total_questions
        ), self.total_questions

    def get_next_question(self, index):
        if index < self.total_questions:
            return self.questions[index]["question"]
        return None

    def evaluate_answer(self, question_idx, user_answer):
        question = self.questions[question_idx]
        
        evaluation = self.evaluator.evaluate(
            student_answer=user_answer,
            reference_answer=question["reference_answer"],
            question=question["question"]
        )
        
        comment = exam_prompts.ExamPrompts.EVALUATION_COMMENTS.get(
            round(evaluation['score']),
            "Ответ оценен."
        )
        
        return {
            'score': evaluation['score'],
            'comment': comment,
            'correct_answer': question["reference_answer"],
            'difficulty': question["difficulty"]
        }

    def get_final_result(self, scores):
        average_score = sum(scores) / len(scores) if scores else 0
        result_key = 'passed' if average_score >= 4 else 'failed'

        return {
            'message': exam_prompts.ExamPrompts.FINAL_RESULTS[result_key].format(grade=Config.EVALUATION["pass_border"][round(average_score)],
                                                                                 score=average_score),
            'average_score': average_score,
            'scores': scores,
            'passed': result_key == 'passed'
        }