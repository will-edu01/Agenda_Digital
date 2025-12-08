document.addEventListener("DOMContentLoaded", function () {
    const btn = document.getElementById("resendButton");
    const msg = document.getElementById("resendMessage");

    if (!btn) return;

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let cookie of cookies) {
                cookie = cookie.trim();
                if (cookie.startsWith(name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }

    btn.addEventListener("click", function () {
        btn.disabled = true;
        msg.style.display = "block";
        msg.textContent = "Reenviando código...";

        fetch("/accounts/resend-code/", {
            method: "POST",
            headers: {
                "Content-Type": "application/json",
                "X-CSRFToken": getCookie("csrftoken")
            }
        })
        .then(res => res.json())
        .then(data => {
            if (data.ok) {
                startTimer();
            } else {
                msg.textContent = "Erro ao reenviar. Tente novamente.";
                btn.disabled = false;
            }
        })
        .catch(() => {
            msg.textContent = "Erro ao reenviar.";
            btn.disabled = false;
        });
    });

    function startTimer() {
        let time = 60; // segundos
        const interval = setInterval(() => {
            msg.textContent = `Código reenviado! Aguarde ${time}s para reenviar novamente.`;
            time--;

            if (time < 0) {
                clearInterval(interval);
                msg.style.display = "none";
                btn.disabled = false;
            }
        }, 1000);
    }
});
