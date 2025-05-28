import time
from datetime import datetime
import logging
from typing import Dict, List

class ExamMetrics:
    def __init__(self):
        self.start_time: float = time.time()
        self.questions_metrics: List[Dict] = []
        self.system_metrics: Dict = {
            'total_requests': 0,
            'failed_requests': 0,
            'response_times': []
        }
        self.current_question_start: float = 0

    def start_question_timer(self, question_id: int):
        self.current_question_start = time.time()
        self.questions_metrics.append({
            'question_id': question_id,
            'start_time': datetime.now().isoformat(),
            'response_time_sec': None,
            'score': None,
            'error': None
        })

    def end_question_timer(self, score: float = None, error: str = None):
        if self.current_question_start and self.questions_metrics:
            response_time = time.time() - self.current_question_start
            self.questions_metrics[-1].update({
                'response_time_sec': round(response_time, 2),
                'score': score,
                'error': error
            })
            self.system_metrics['response_times'].append(response_time)
            self.current_question_start = 0

    def log_request(self, success: bool = True):
        self.system_metrics['total_requests'] += 1
        if not success:
            self.system_metrics['failed_requests'] += 1

    def get_summary(self) -> Dict:
        total_time = time.time() - self.start_time
        scores = [q['score'] for q in self.questions_metrics if q['score'] is not None]
        
        return {
            'total_time_min': round(total_time / 60, 2),
            'average_score': round(sum(scores) / len(scores), 2) if scores else 0,
            'average_response_time_sec': round(
                sum(self.system_metrics['response_times']) / 
                len(self.system_metrics['response_times']), 2
            ) if self.system_metrics['response_times'] else 0,
            'total_questions': len(self.questions_metrics),
            'success_rate': round(
                (self.system_metrics['total_requests'] - self.system_metrics['failed_requests']) / 
                self.system_metrics['total_requests'] * 100, 2
            ) if self.system_metrics['total_requests'] else 100,
            'details': self.questions_metrics
        }