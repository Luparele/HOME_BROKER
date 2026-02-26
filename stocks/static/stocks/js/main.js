function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}

const csrftoken = getCookie('csrftoken');

function showToast(message, type = 'success') {
    let toast = document.getElementById('toast');
    let toastMessage = null;

    if (!toast) {
        toast = document.createElement('div');
        toast.id = 'toast';
        toast.className = 'toast';

        toastMessage = document.createElement('span');
        toastMessage.id = 'toastMessage';
        toast.appendChild(toastMessage);

        document.body.appendChild(toast);
    } else {
        toastMessage = document.getElementById('toastMessage');
    }

    toast.className = `toast ${type}`;
    toastMessage.textContent = message;
    toast.style.display = 'flex';
    toast.style.animation = 'slideIn 0.3s forwards';

    setTimeout(() => {
        toast.style.animation = 'fadeOut 0.3s forwards';
        setTimeout(() => { toast.style.display = 'none'; }, 300);
    }, 3000);
}

async function toggleFavorite(button) {
    const ticker = button.getAttribute('data-ticker');
    const name = button.getAttribute('data-name');

    const formData = new FormData();
    formData.append('ticker', ticker);
    formData.append('name', name);

    try {
        const response = await fetch('/favorite/toggle/', {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': csrftoken
            }
        });

        const data = await response.json();

        if (response.ok) {
            if (data.action === 'added') {
                button.classList.add('active');
                button.querySelector('.icon').innerText = '⭐';
                button.querySelector('.text').innerText = 'Favoritado';
                showToast('Adicionado aos favoritos', 'success');
            } else {
                button.classList.remove('active');
                button.querySelector('.icon').innerText = '☆';
                button.querySelector('.text').innerText = 'Favoritar';
                showToast('Removido dos favoritos', 'success');

                // If we are on the dashboard, remove the card
                const card = button.closest('.stock-card');
                if (card) {
                    card.style.opacity = '0';
                    setTimeout(() => card.remove(), 300);
                }
            }
        } else {
            if (response.status === 403) {
                showToast('Você precisa estar logado para favoritar ações.', 'error');
            } else {
                showToast('Erro ao processar solicitação.', 'error');
            }
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('Erro de conexão.', 'error');
    }
}
