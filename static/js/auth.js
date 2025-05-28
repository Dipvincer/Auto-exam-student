document.addEventListener('DOMContentLoaded', function() {
    // Переключение между вкладками
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            const tabId = this.getAttribute('data-tab');
            
            // Убираем активные классы
            tabBtns.forEach(b => b.classList.remove('active'));
            tabContents.forEach(c => c.classList.remove('active'));
            
            // Добавляем активные классы
            this.classList.add('active');
            document.getElementById(`${tabId}-form`).classList.add('active');
        });
    });

    // Обработка формы входа
    const loginForm = document.getElementById('loginForm');
    loginForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const email = document.getElementById('login-email').value;
        const password = document.getElementById('login-password').value;
        
        try {
            const response = await fetch('/token', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    username: email,
                    password: password,
                    grant_type: 'password'
                })
            });
            
            if (!response.ok) {
                throw new Error('Ошибка авторизации');
            }
            
            const data = await response.json();
            localStorage.setItem('access_token', data.access_token);
            window.location.href = '/exam';
        } catch (error) {
            showError(loginForm, 'Неверный email или пароль');
            console.error('Login error:', error);
        }
    });

    // Обработка формы регистрации
    const registerForm = document.getElementById('registerForm');
    registerForm.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const userData = {
            email: document.getElementById('reg-email').value,
            password: document.getElementById('reg-password').value,
            full_name: document.getElementById('reg-fullname').value,
            faculty: document.getElementById('reg-faculty').value
        };
        
        try {
            const response = await fetch('/register', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(userData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Ошибка регистрации');
            }
            
            alert('Регистрация успешна! Теперь вы можете войти.');
            document.querySelector('.tab-btn[data-tab="login"]').click();
            registerForm.reset();
        } catch (error) {
            showError(registerForm, error.message);
            console.error('Registration error:', error);
        }
    });

    function showError(form, message) {
        let errorDiv = form.querySelector('.error-message');
        if (!errorDiv) {
            errorDiv = document.createElement('div');
            errorDiv.className = 'error-message';
            form.appendChild(errorDiv);
        }
        errorDiv.textContent = message;
        errorDiv.style.display = 'block';
    }
});