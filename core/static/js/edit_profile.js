document.addEventListener("DOMContentLoaded", () => {

  const modal = document.getElementById("modal-edit-profile");
  const openBtn = document.getElementById("openEditProfile");
  const closeBtn = document.getElementById("closeEditProfile");
  const cancelBtn = document.getElementById("cancelEditProfile");
  const form = document.getElementById("editProfileForm");

  if (openBtn) {
    openBtn.addEventListener("click", () => {
      modal.style.display = "flex";
      modal.classList.add("active");
      modal.setAttribute("aria-hidden", "false");
      // foco no primeiro campo
      setTimeout(() => document.getElementById("name").focus(), 120);
    });
  }

  function hideModal() {
    modal.classList.remove("active");
    modal.setAttribute("aria-hidden", "true");
    setTimeout(() => modal.style.display = "none", 220);
  }

  closeBtn && closeBtn.addEventListener("click", hideModal);
  cancelBtn && cancelBtn.addEventListener("click", hideModal);

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

  if (form) {
    form.addEventListener("submit", async (e) => {
      e.preventDefault();
      const submitBtn = form.querySelector(".modal-save");
      submitBtn.disabled = true;
      const formData = new FormData(form);
      try {
        const response = await fetch("/accounts/profile/update/", {
          method: "POST",
          headers: {
            "X-CSRFToken": getCookie("csrftoken")
          },
          body: formData
        });
        const data = await response.json();
        if (data.success) {
          document.getElementById("userName").innerText = data.name;
          document.getElementById("userPhone").innerText = data.phone;
          showToast("Perfil atualizado com sucesso!", "success");
          hideModal();
        } else {
          showToast(data.message || "Erro ao atualizar perfil", "error");
        }
      } catch (err) {
        console.error(err);
        showToast("Erro de conexão", "error");
      } finally {
        submitBtn.disabled = false;
      }
    });
  }

});
