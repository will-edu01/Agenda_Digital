function openLoginRequiredModal(){
  const m = document.getElementById("modal-login-required");
  if (!m) return;
  m.setAttribute("aria-hidden","false");
  document.body.classList.add("modal-open");
  m.classList.add("show");
}

function closeLoginRequiredModal(){
  const m = document.getElementById("modal-login-required");
  if (!m) return;
  m.setAttribute("aria-hidden","true");
  m.classList.remove("show");
  document.body.classList.remove("modal-open");
}

document.addEventListener("DOMContentLoaded", function () {

    const dateInput = document.getElementById("modal-date");

    if (dateInput) {
        const today = new Date().toISOString().split("T")[0];
        dateInput.min = today;
    }

    const modals = document.querySelectorAll(".modal-overlay");

    window.openModal = function (modal) {
        if (!modal) return;

        modal.classList.add("show");
        modal.setAttribute("aria-hidden", "false");

        document.body.classList.add("modal-open");
    };

    window.closeModal = function (modal) {
        if (!modal) return;

        modal.classList.remove("show");
        modal.setAttribute("aria-hidden", "true");

        const stillOpen = document.querySelector(".modal-overlay.show");
        if (!stillOpen) {
            document.body.classList.remove("modal-open");
        }
    };

    modals.forEach(modal => {
        modal.addEventListener("click", function (e) {
            if (e.target.classList.contains("modal-overlay")) {
                closeModal(modal);
            }
        });
    });

    document.addEventListener("keydown", function (event) {
        if (event.key === "Escape") {

            const openModalEl = document.querySelector(".modal-overlay.show");
            if (openModalEl) {
                closeModal(openModalEl);
            }
        }
    });

});

function openSuccessModal() {
    document.getElementById("successModal").style.display = "flex";
}

function closeSuccessModal() {
    document.getElementById("successModal").style.display = "none";
}

function showToast(text, type="info") {
      const t = document.getElementById("toast");
      t.className = "toast " + type;
      t.textContent = text;
      t.classList.add("show");
      setTimeout(()=> t.classList.remove("show"), 3500);
}
