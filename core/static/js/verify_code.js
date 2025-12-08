document.addEventListener('DOMContentLoaded', function() {
  const codeInputs = document.querySelectorAll('.code-input');
  const fullCodeField = document.getElementById('full_code');
  if (!codeInputs.length || !fullCodeField) return;

  codeInputs.forEach((input, idx) => {
    input.addEventListener('input', () => {
      input.value = input.value.replace(/[^0-9]/g, '').slice(0,1);
      if (input.value && codeInputs[idx+1]) codeInputs[idx+1].focus();
      fullCodeField.value = Array.from(codeInputs).map(i => i.value || '').join('');
    });

    input.addEventListener('keydown', (e) => {
      if (e.key === 'Backspace' && !input.value && codeInputs[idx-1]) {
        codeInputs[idx-1].focus();
      }
    });
  });

  const form = fullCodeField && fullCodeField.closest('form');
  if (form) {
    form.addEventListener('submit', () => {
      fullCodeField.value = Array.from(codeInputs).map(i => i.value || '').join('');
    });
  }
});
