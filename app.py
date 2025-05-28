from flask import Flask, render_template, request, jsonify, session
from core.llm_integration import LLMIntegration
from core.exam_flow import ExamFlow
from core.evaluation import AnswerEvaluator
from core.config import Config
from core.metrics import ExamMetrics
import logging

app = Flask(__name__)
app.secret_key = 'test_exam_sistem'
Config.setup_logging()

# Инициализация компонентов
llm = LLMIntegration()
evaluator = AnswerEvaluator()
exam_flow = ExamFlow(llm, evaluator)
metrics = ExamMetrics()

@app.route('/')
def home():
    session['exam_state'] = 'welcome'
    session['current_question'] = 0
    session['scores'] = []
    return render_template('exam_chat.html')

@app.route('/get-welcome-message')
def get_welcome():
    welcome_msg, question_count = exam_flow.get_welcome_message()
    session['exam_state'] = 'waiting_confirmation'
    return jsonify({'message': welcome_msg, 'question_count': question_count})

@app.route('/confirm-ready', methods=['POST'])
def confirm_ready():
    metrics.start_question_timer(0)
    session['exam_state'] = 'in_progress'
    first_question = exam_flow.get_next_question(0)
    question_data = exam_flow.questions[0]
    return jsonify({
        'question_text': first_question,
        'difficulty': question_data.get('difficulty', 'medium'),
    })

@app.route('/submit-answer', methods=['POST'])
def submit_answer():
    if session['exam_state'] != 'in_progress':
        return jsonify({'error': 'Экзамен не начат'}), 400

    metrics.log_request()

    user_answer = request.json.get('answer', '')
    question_idx = session['current_question']
    
    evaluation = exam_flow.evaluate_answer(question_idx, user_answer)
    session['scores'].append(evaluation['score'])
    

    next_question_idx = question_idx + 1
    if next_question_idx < exam_flow.total_questions:
        session['current_question'] = next_question_idx
        next_question_data = exam_flow.questions[next_question_idx]
        metrics.end_question_timer(score=evaluation['score'])
        return jsonify({
            'evaluation': evaluation,
            'question_text': next_question_data["question"],
            'difficulty': next_question_data.get("difficulty", "medium"),
            'metrics': {
                'current_question_time': metrics.questions_metrics[-1]['response_time_sec'],
                'average_score': metrics.get_summary()['average_score']
            }
        })
    else:
        session['exam_state'] = 'completed'
        final_result = exam_flow.get_final_result(session['scores'])
        return jsonify({
            'evaluation': evaluation,
            'final_result': final_result
        })
    
@app.route('/metrics')
def get_metrics():
    return jsonify(metrics.get_summary())

if __name__ == '__main__':
    app.run(debug=True, port=5000)