// Function to fetch protected 
console.log('auth.js loaded');
async function fetchProtectedResource(url) {
    const token = localStorage.getItem('access_token');

    if (!token) {
        if (window.location.pathname !== '/users/login') {
            window.location.href = '/users/login'; // Redirect to login if no token
        }
        return;
    }

    try {
        const response = await fetch(url, {
            method: 'GET',
            headers: {
                'Authorization': `Bearer ${token}`
            }
        });

        if (!response.ok) {
            if (window.location.pathname !== '/users/login') {
                window.location.href = '/users/login'; // Redirect to login on unauthorized
            }
            throw new Error('Unauthorized access');
        }

        return await response.text(); // Assuming the response is HTML
    } catch (error) {
        console.error('Error accessing protected resource:', error);
        if (window.location.pathname !== '/users/login') {
            window.location.href = '/users/login';
        }
    }
}

// Handle login form submission
async function handleLoginForm() {
    if (window.location.pathname === '/users/login') {
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
                        throw new Error('Login failed');
                    }

                    const data = await response.json();
                    localStorage.setItem('access_token', data.access_token);
                    console.log('Access token stored:', localStorage.getItem('access_token'));

                    // Redirect to a protected page after login
                    window.location.href = '/ad/post-ad';
                } catch (error) {
                    console.error('Login error:', error);
                }
            });
        }
    }
}

// Initialize script
document.addEventListener('DOMContentLoaded', () => {
    handleLoginForm();

    // Example of fetching a protected resource, adjust URL as needed
    if (window.location.pathname === '/ad/post-ad') {
        fetchProtectedResource('/account/dashboard')
            .then((html) => {
                if (html) {
                    document.body.innerHTML = html;
                }
            })
            .catch((error) => {
                console.error('Error loading dashboard:', error);
            });
    }
});
