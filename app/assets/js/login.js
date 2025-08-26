document.addEventListener('DOMContentLoaded', (event) => {
    const loginForm = document.getElementById('login-form');

    if (loginForm) {
        loginForm.addEventListener('submit', async (event) => {
            event.preventDefault();

            const formData = new FormData(loginForm);
            const email = formData.get('username');
            const password = formData.get('password');
            try {
                const response = await fetch('/users/login', {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/x-www-form-urlencoded',
                    },
                    body: new URLSearchParams({
                        username: email,
                        password: password
                    })
                });
                if (!response.ok) {
                    throw new Error('Error al iniciar sesión');
                }

                const data = await response.json();
                localStorage.setItem('access_token', data.access_token);


            } catch (error) {
                console.error('Error al iniciar sesión:', error);
            }
        });

    }
});
