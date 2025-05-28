BASIC_PROGRAMMING_EXAM = {
    'subject': 'Основам Программирования',
    'questions': [
        {
            "question": "Что такое ООП?",
            "reference_answer": "Объектно-ориентированное программирование - это парадигма программирования, основанная на объектах, содержащих данные и методы.",
            "difficulty": "medium"
        },
        {
            "question": "Назовите основные принципы SOLID",
            "reference_answer": "Single Responsibility (единственная ответственность), Open-Closed (открытость/закрытость), Liskov Substitution (подстановка Лисков), Interface Segregation (разделение интерфейсов), Dependency Inversion (инверсия зависимостей).",
            "difficulty": "hard"
        },
        {
            "question": "Что такое инкапсуляция?",
            "reference_answer": "Это механизм языка, который объединяет данные и методы, работающие с этими данными, и защищает их от внешнего вмешательства.",
            "difficulty": "easy"
        },
        {
            "question": "В чем разница между классом и объектом?",
            "reference_answer": "Класс - это шаблон для создания объектов, определяющий их структуру и поведение. Объект - это экземпляр класса, конкретная реализация.",
            "difficulty": "medium"
        }
    ]
}

def get_exam_questions(exam_name):
    exams = {
        'basic_programming': BASIC_PROGRAMMING_EXAM
    }
    return exams.get(exam_name)