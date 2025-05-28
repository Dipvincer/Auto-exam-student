import pandas as pd
from tqdm import tqdm
from core.evaluation import AnswerEvaluator

evaluator = AnswerEvaluator()

def evaluate_score(question, reference_answer, student_answer, model):
    res = evaluator._get_llm_feedback(student_answer, reference_answer, question, model)
    if res:
        return res[0]['score']
    else:
        return None

tqdm.pandas()
questions = pd.read_csv('questions/all_questions.csv')

questions['deepseek_v3'] = questions.progress_apply(lambda x : 
                                                 evaluate_score(x['Вопрос'], x['Эталонный ответ'], x['Ответ студента'], ['deepseek_v3']), 
                                                 axis=1)
questions.to_csv('questions/questions_model_calc_deepseek_v3.csv')

print(questions.head(5))