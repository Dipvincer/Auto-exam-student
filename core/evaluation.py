import re
import time
import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from core.config import Config
from core.llm_integration import LLMIntegration
from core.extensions import exam_prompts
import logging

logger = logging.getLogger("evaluation")

class AnswerEvaluator:
    def __init__(self):
        self.llm = LLMIntegration()
        self.minilm = SentenceTransformer(Config.EVALUATION["models"]["minilm"])
        logger.info("Инициализирован оценщик ответов")


    def evaluate(self, student_answer, reference_answer, question=None):
        """
        Оценивает ответ по 10-балльной шкале
        
        Возвращает:
        {
            "score": int,             # Оценка от 1 до 10
            "detailed_feedback": str, # Развернутый комментарий
            "is_correct": bool,       # Правильный ли ответ
            "evaluation_method": str  # Метод оценки
        }
        """
        answer_type = self._classify_answer(student_answer)
        
        if answer_type == "short":
            return self._evaluate_exact(student_answer, reference_answer)
        elif answer_type == "detailed":
            return self._evaluate_detailed(student_answer, reference_answer, question)
        else:
            return self._evaluate_detailed(student_answer, reference_answer, question)


    def _classify_answer(self, answer):
        answer = answer.strip()
        word_count = len(answer.split())
        
        if word_count == 0:
            return "empty"
        elif word_count <= 2 or re.match(r'^[\d,.]+$', answer) or answer.lower() in ('да', 'нет', 'true', 'false'):
            return "short"
        elif word_count <= 10:
            return "medium"
        else:
            return "detailed"


    def _check_relevance(self, answer, question):
        prompt = exam_prompts.ExamPrompts.RELEVANCE_PROMPT.format(
            question=question,
            answer=answer
        )
        response = self.llm.call_deepseek_v3(prompt, temperature=0, max_tokens=1)
        return response.strip().lower() == 'да'


    def _evaluate_exact(self, student_answer, reference_answer):
        student_norm = student_answer.strip().lower()
        reference_norm = reference_answer.strip().lower()
        
        try:
            student_num = float(student_norm.replace(',', '.'))
            reference_num = float(reference_norm.replace(',', '.'))
            is_correct = abs(student_num - reference_num) < 1e-6
        except ValueError:
            is_correct = student_norm == reference_norm
        
        score = 10 if is_correct else 1
        
        return {
            "score": score,
            "detailed_feedback": "Правильный ответ" if is_correct else "Неправильный ответ",
            "is_correct": is_correct,
            "evaluation_method": "exact"
        }


    def _evaluate_detailed(self, student_answer, reference_answer, question):
        if self._check_relevance(student_answer, question):
            return {
                "score": 0,
                "detailed_feedback": "Ответ некорректен по этическому или смысловому наполнению.",
                "is_correct": False,
                "evaluation_method": "semantic"
            }

        similarity = self._minilm_similarity(student_answer, reference_answer)
        llm_feedback = self._get_llm_feedback(student_answer, reference_answer, question)[0]
        
        similarity_score = int(round(similarity * 9 + 1))
        
        # Корректируем оценку на основе фидбэка LLM
        final_score = self._adjust_score(similarity_score, llm_feedback)
        
        return {
            "score": final_score,
            "detailed_feedback": llm_feedback.get("feedback", ""),
            "is_correct": final_score >= 4,
            "evaluation_method": "semantic"
        }


    def _minilm_similarity(self, text1, text2):
        emb1 = self.minilm.encode(text1, convert_to_tensor=True)
        emb2 = self.minilm.encode(text2, convert_to_tensor=True)
        return np.dot(emb1, emb2.T).item()


    def _get_llm_feedback(self, student_answer, reference_answer, question, models=None):
        time.sleep(1)
        prompt = exam_prompts.ExamPrompts.EVALUATION_PROMPT_LIGHT.format(
            question=question,
            reference_answer=reference_answer,
            student_answer=student_answer
        )

        response_all = []
        if "deepseek_v3" in models:
            response_all.append(self.llm.call_deepseek_v3(prompt, temperature=0.2, max_tokens=1000))
        if "deepseek_r1" in models:
            response_all.append(self.llm.call_deepseek_r1(prompt, temperature=0.2, max_tokens=1000))
        if "llama_3.1_nemotron" in models:
            response_all.append(self.llm.call_llama(prompt, temperature=0.2, max_tokens=1000))
        if "qwen3_325b" in models:
            response_all.append(self.llm.call_qwen(prompt, temperature=0.2, max_tokens=1000))
        if "gemini_2.5_flash" in models:
            response_all.append(self.llm.call_gemini_flash(prompt, temperature=0.2, max_tokens=1000))
        if "grok3_mini" in models:
            response_all.append(self.llm.call_grok_mini(prompt, temperature=0.2, max_tokens=1000))
        if "gpt4o_mini" in models:
            response_all.append(self.llm.call_gpt_mini(prompt, temperature=0.2, max_tokens=1000))

        if not response_all:
            response_all.append(self.llm.call_deepseek_v3(prompt, temperature=0.2, max_tokens=1000))
        
        score = 0
        feedback = "Не удалось автоматически оценить ответ"
        
        results = []
        if response_all:
            for response in response_all:
                try:
                    #score_line = next(line for line in response.split('\n') if line.startswith('Оценка:'))
                    #score = int(score_line.split(':')[1].strip())
                    #score = max(1, min(10, score))
                    
                    #feedback_line = next(line for line in response.split('\n') if line.startswith('Комментарий:'))
                    #feedback = feedback_line.split(':', 1)[1].strip()

                    results.append({"score": int(response), "feedback": ''})
                except (StopIteration, ValueError):
                    logger.warning(f"Не удалось распарсить ответ LLM: {response}")
        
        return results


    def _adjust_score(self, similarity_score, llm_feedback):
        """Комбинируем оценку similarity и LLM"""
        llm_score = llm_feedback.get("score")

        return int(round((similarity_score * 0.4 + llm_score * 0.6)))