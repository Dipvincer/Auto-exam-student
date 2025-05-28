document.addEventListener('DOMContentLoaded', function() {
    const chatMessages = document.getElementById('chat-messages');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');
    const readyButton = document.getElementById('ready-button');
    const themeToggle = document.getElementById('theme-toggle');
    const themeStyle = document.getElementById('theme-style');
    
    let currentQuestionIndex = 0;
    let totalQuestions = 0;

    let currentState = 'welcome';
    let isDarkTheme = false;

    function initTheme() {
        const savedTheme = localStorage.getItem('theme');
        if (savedTheme === 'dark') {
            enableDarkTheme();
        }
    }

    function enableDarkTheme() {
        themeStyle.disabled = false;
        themeToggle.textContent = 'Светлая тема';
        localStorage.setItem('theme', 'dark');
        isDarkTheme = true;
    }
    
    function disableDarkTheme() {
        themeStyle.disabled = true;
        themeToggle.textContent = 'Темная тема';
        localStorage.setItem('theme', 'light');
        isDarkTheme = false;
    }
    
    themeToggle.addEventListener('click', function() {
        if (isDarkTheme) {
            disableDarkTheme();
        } else {
            enableDarkTheme();
        }
    });
    
    function addMessage(text, isUser = false) {
        const messageDiv = document.createElement('div');
        messageDiv.classList.add('message');
        messageDiv.classList.add(isUser ? 'user-message' : 'bot-message');
        messageDiv.textContent = text;
        chatMessages.appendChild(messageDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addEvaluation(score, comment, correctAnswer) {
        const evalDiv = document.createElement('div');
        evalDiv.classList.add('evaluation');
        evalDiv.innerHTML = `
            <p><strong>Оценка: ${score}/10</strong></p>
            <p>${comment}</p>
            ${correctAnswer ? `<p><em>Правильный ответ: ${correctAnswer}</em></p>` : ''}
        `;
        chatMessages.appendChild(evalDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    function addFinalResult(message, averageScore) {
        const resultDiv = document.createElement('div');
        resultDiv.classList.add('final-result');
        resultDiv.innerHTML = `
            <p>${message}</p>
            <p>Средний балл: ${averageScore.toFixed(1)}/10</p>
        `;
        chatMessages.appendChild(resultDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function addQuestion(questionText, difficulty) {
        if (!questionText) {
            console.error('Получен пустой вопрос');
            questionText = "Не удалось загрузить вопрос";
        }
        
        if (!difficulty) {
            difficulty = 'medium';
        }
    
        const questionDiv = document.createElement('div');
        questionDiv.classList.add('message', 'bot-message');
        
        const difficultyBadge = `
            <span class="difficulty-badge difficulty-${difficulty}">
                ${getDifficultyLabel(difficulty)}
            </span>
        `;
        
        questionDiv.innerHTML = `${difficultyBadge}${questionText}`;
        chatMessages.appendChild(questionDiv);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function getDifficultyLabel(difficulty) {
        const labels = {
            'easy': 'Легкий',
            'medium': 'Средний',
            'hard': 'Сложный'
        };
        return labels[difficulty] || difficulty;
    }
    
    async function handleAnswer() {
        const answer = userInput.value.trim();
        if (!answer) return;
        
        addMessage(answer, true);
        userInput.value = '';
        sendButton.disabled = true;
        
        try {
            const response = await fetch('/submit-answer', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ answer: answer })
            });
            
            const data = await response.json();
            updateMetrics(data.metrics);
            
            if (data.error) {
                addMessage(`Ошибка: ${data.error}`);
                return;
            }
            
            addEvaluation(
                data.evaluation.score,
                data.evaluation.comment,
                data.evaluation.correct_answer
            );
            
            if (data.question_text) {
                addQuestion(data.question_text, data.difficulty);
                currentQuestionIndex++;
                updateProgress();
                sendButton.disabled = false;
            } else if (data.final_result) {
                addFinalResult(
                    data.final_result.message,
                    data.final_result.average_score
                );
                sendButton.style.display = 'none';
                userInput.disabled = true;
                currentState = 'completed';
            }
        } catch (error) {
            addMessage("Произошла ошибка при отправке ответа");
            console.error('Error:', error);
            sendButton.disabled = false;
        }
    }
    

    async function loadWelcomeMessage() {
        try {
            const response = await fetch('/get-welcome-message');
            const data = await response.json();
            
            addMessage(data.message);
            readyButton.style.display = 'block';
            currentState = 'waiting_confirmation';
            
            document.querySelector('.exam-subject').textContent = 'Экзамен';
            totalQuestions = data.question_count || 0;
            updateProgress();
        } catch (error) {
            addMessage("Не удалось загрузить приветственное сообщение");
            console.error('Error:', error);
        }
    }
    
    async function confirmReadiness() {
        readyButton.style.display = 'none';
        sendButton.style.display = 'block';
        addMessage("Я готов начать экзамен", true);
        
        try {
            const response = await fetch('/confirm-ready', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                }
            });
            
            const data = await response.json();
            addQuestion(data.question_text, data.difficulty);
            currentState = 'in_progress';
        } catch (error) {
            addMessage("Ошибка при начале экзамена");
            console.error('Error:', error);
        }
    }

    function updateProgress() {
        const progressElement = document.querySelector('.exam-progress');
        progressElement.textContent = `Вопрос ${currentQuestionIndex + 1} из ${totalQuestions}`;
    }

    function updateMetrics(metricsData) {
        const metricsContent = document.getElementById('metrics-content');
        
        if (!metricsData) {
            metricsContent.innerHTML = '<p>Метрики загружаются...</p>';
            return;
        }
        
        metricsContent.innerHTML = `
            <div class="metrics-item">
                <span class="metrics-title">Средний балл:</span>
                <span class="metrics-value">${metricsData.average_score.toFixed(1)}/10</span>
            </div>
            <div class="metrics-item">
                <span class="metrics-title">Время ответа:</span>
                <span class="metrics-value">${metricsData.current_question_time} сек</span>
            </div>
            <div class="metrics-item">
                <span class="metrics-title">Прогресс:</span>
                <span class="metrics-value">${currentQuestionIndex + 1}/${totalQuestions}</span>
            </div>
            <div class="metrics-item">
                <span class="metrics-title">Успешность:</span>
                <span class="metrics-value">${metricsData.success_rate}%</span>
            </div>
        `;
    }


    async function loadSystemMetrics() {
        try {
            const response = await fetch('/metrics');
            const data = await response.json();
            console.log("System metrics:", data);
        } catch (error) {
            console.error("Error loading metrics:", error);
        }
    }   
    

    sendButton.addEventListener('click', handleAnswer);
    readyButton.addEventListener('click', confirmReadiness);
    
    userInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter' && currentState === 'in_progress') {
            handleAnswer();
        }
    });
    
    // Инициализация приложения
    loadSystemMetrics();
    initTheme();
    loadWelcomeMessage();
});