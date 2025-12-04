document.addEventListener("DOMContentLoaded", function() {
  const $ = id => document.getElementById(id);
  const q = sel => document.querySelector(sel);
  const qa = sel => Array.from(document.querySelectorAll(sel));

  const trigger = document.getElementById("user-trigger");
  const dropdown = document.getElementById("user-dropdown");
  if (trigger && dropdown) {
      trigger.addEventListener("click", function(e){
        e.stopPropagation();
        dropdown.classList.toggle("show");
      });
      document.addEventListener("click", function(e){
        if (!trigger.contains(e.target) && !dropdown.contains(e.target)){
          dropdown.classList.remove("show");
        }
      });
  }

  function getCookie(name){
    const m = document.cookie.match('(^|;)\\s*' + name + '\\s*=\\s*([^;]+)');
    return m ? m.pop() : '';
  }
  const csrftoken = getCookie('csrftoken');

  const checkboxes = qa('.service-checkbox');
  const totalDurationEl = $('total-duration');
  const totalPriceEl = $('total-price');
  const continueBtn = $('continue-btn');

  const modalSelect = $('modal-select-datetime');
  const modalTimes = $('modal-times');
  const modalDate = $('modal-date');
  const modalSelectNext = $('modal-select-next');

  const modalSummary = $('modal-summary');
  const summaryServices = $('summary-services');
  const summaryTime = $('summary-time');
  const summaryPrice = $('summary-price');
  const summaryDate = $('summary-date');
  const summaryHour = $('summary-hour');
  const summaryBack = $('summary-back');
  const summaryConfirm = $('summary-confirm');

  const modalSuccess = $('modal-success');
  const successClose = $('success-close');

  function parsePrice(txt){
    if (!txt) return 0;
    return parseFloat(txt.replace('R$','').replace(/\s/g,'').replace(',','.')) || 0;
  }
  function parseMinutes(txt){
    if (!txt) return 0;
    const n = txt.replace(/[^0-9]/g,'');
    return parseInt(n) || 0;
  }

  function updateSummary(){
    let minutes = 0, price = 0;
    qa('.service-checkbox').forEach(cb=>{
      if (cb.checked){
        const card = cb.closest('.service-card');
        const meta = (card && card.querySelector('.service-meta')) ? card.querySelector('.service-meta').textContent : '';
        const pricePart = (meta.split('|')[0] || meta).trim();
        const minsPart = (meta.split('|')[1] || '').trim();
        price += parsePrice(pricePart);
        minutes += parseMinutes(minsPart);
      }
    });
    if (totalDurationEl) totalDurationEl.textContent = minutes;
    if (totalPriceEl) totalPriceEl.textContent = price.toFixed(2);
    if (continueBtn) continueBtn.disabled = (minutes === 0);
  }

  qa('.service-checkbox').forEach(cb => cb.addEventListener('change', updateSummary));
  updateSummary();

  if (continueBtn) {
    continueBtn.addEventListener('click', function(){
      if (continueBtn.disabled) return;

      if (!window.userIsAuthenticated) {
        openLoginRequiredModal();
        return;
      }

      if (modalDate) modalDate.value = '';
      if (modalTimes) modalTimes.innerHTML = '<p style="grid-column:1/-1;color:#666;text-align:center">Selecione uma data</p>';
      if (modalSelectNext) modalSelectNext.disabled = true;
      openModal(modalSelect);
    });
  }

  if (modalDate && modalTimes && modalSelectNext) {
    modalDate.addEventListener('change', async function(){
      const date = this.value;
      modalTimes.innerHTML = '';
      modalSelectNext.disabled = true;

      if (!date) {
        modalTimes.innerHTML = '<p style="grid-column:1/-1;color:#666;text-align:center">Selecione uma data</p>';
        return;
      }

      const duration = parseInt((totalDurationEl && totalDurationEl.textContent) || '0', 10) || 0;

      const url = "/horarios/?date=" + encodeURIComponent(date) + "&duration=" + encodeURIComponent(duration);

      try {
        const res = await fetch(url, { credentials: 'same-origin' });
        if (!res.ok) throw new Error('Erro ao buscar horários');
        const data = await res.json();
        const slots = data.slots || [];
        if (!slots.length) {
          modalTimes.innerHTML = "<p style='grid-column:1/-1;color:#666;text-align:center'>Nenhum horário disponível.</p>";
          return;
        }

        modalTimes.innerHTML = '';
        slots.forEach(t => {
          const b = document.createElement('button');
          b.type = 'button';
          b.className = 'time-btn';
          b.textContent = t;
          b.addEventListener('click', function(){
            modalTimes.querySelectorAll('.time-btn').forEach(x => x.classList.remove('selected'));
            b.classList.add('selected');
            modalSelectNext.dataset.date = date;
            modalSelectNext.dataset.time = t;
            modalSelectNext.disabled = false;
          });
          modalTimes.appendChild(b);
        });
      } catch(err) {
        console.error(err);
        modalTimes.innerHTML = "<p style='grid-column:1/-1;color:#c33;text-align:center'>Erro ao carregar horários.</p>";
      }
    });
  }

  if (modalSelectNext) {
    modalSelectNext.addEventListener('click', async function(){
      const date = modalSelectNext.dataset.date;
      const time = modalSelectNext.dataset.time;
      const selected = qa('input[name="services"]:checked');
      if (!selected.length) { showToast('Selecione pelo menos um serviço', 'error'); return; }
      const ids = selected.map(cb => cb.value);

      const fd = new FormData();
      ids.forEach(id => fd.append('services[]', id));
      fd.append('selected_date', date);
      fd.append('selected_time', time);

      try {
        const res = await fetch("/api/confirm/", {
          method: 'POST',
          body: fd,
          headers: { 'X-CSRFToken': csrftoken },
          credentials: 'same-origin'
        });
        const data = await res.json();
        if (!data.ok) {
          showToast(data.error || 'Erro ao validar seleção', 'error');
          return;
        }

        summaryServices.innerHTML = '';
        (data.services || []).forEach(s => {
          const li = document.createElement('li');
          li.textContent = `${s.name} — ${s.duration} min — R$ ${parseFloat(s.price).toFixed(2)}`;
          summaryServices.appendChild(li);
        });
        summaryTime.textContent = data.total_minutes;
        summaryPrice.textContent = parseFloat(data.total_price).toFixed(2);
        summaryDate.textContent = data.selected_date;
        summaryHour.textContent = data.selected_time;

        closeModal(modalSelect);
        openModal(modalSummary);

      } catch(err) {
        console.error(err);
        showToast('Erro ao validar dados', 'error');
      }
    });
  }

  if (summaryBack) {
    summaryBack.addEventListener('click', function(){
      closeModal(modalSummary);
      openModal(modalSelect);
    });
  }

  if (summaryConfirm) {
    summaryConfirm.addEventListener('click', async function(){
      const selected = qa('input[name="services"]:checked');
      if (!selected.length) { showToast('Selecione serviços', 'error'); return; }
      const ids = selected.map(cb => cb.value);

      const fd = new FormData();
      ids.forEach(id => fd.append('services[]', id));
      fd.append('selected_date', summaryDate.textContent);
      fd.append('selected_time', summaryHour.textContent);

      try {
        const res = await fetch("/api/save/", {
          method: 'POST',
          body: fd,
          headers: { 'X-CSRFToken': csrftoken },
          credentials: 'same-origin'
        });
        const data = await res.json();
        if (!data.ok) {
          showToast(data.error || 'Erro ao salvar agendamento', 'error');
          return;
        }
        closeModal(modalSummary);
        openModal(modalSuccess);
      } catch(err) {
        console.error(err);
        showToast('Erro ao salvar agendamento', 'error');
      }
    });
  }

  if (successClose) {
    successClose.addEventListener('click', function(){
      closeModal(modalSuccess);
    });
  }

});
