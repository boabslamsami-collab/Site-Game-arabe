const games = {
  guess: { title: 'الرقم السري', icon: '🔢' }, rps: { title: 'حجر ورقة مقص', icon: '✊' },
  xo: { title: 'إكس أو', icon: '⭕' }, quiz: { title: 'اختبار المعلومات', icon: '🧠' },
  hangman: { title: 'خمن الكلمة', icon: '🔤' }, math: { title: 'تحدي الحساب', icon: '➕' },
  sequence: { title: 'أكمل النمط', icon: '🧩' }, truefalse: { title: 'صح أم خطأ', icon: '✅' },
  scramble: { title: 'الكلمة المبعثرة', icon: '🔀' }, blackjack: { title: '21 المصغرة', icon: '🃏' }
};
const area = document.getElementById('play-area');
const controls = document.getElementById('game-controls');
let activeGame = null;

async function post(url, body) {
  const response = await fetch(url, { method: 'POST', headers: {'Content-Type':'application/json'}, body: JSON.stringify(body) });
  const result = await response.json();
  if (!response.ok) throw new Error(result.error || 'حدث خطأ. حاول مرة أخرى.');
  return result;
}
function showView(view) {
  document.getElementById('game-message').textContent = view.message || '';
  document.getElementById('game-display').textContent = view.display || '';
  controls.innerHTML = '';
  document.getElementById('restart-game').hidden = !view.finished;
  if (view.finished) return;
  if (view.input_type === 'grid') {
    const grid = document.createElement('div'); grid.className = 'xo-grid';
    view.options.forEach(item => {
      const button = document.createElement('button'); button.className = 'answer-button'; button.textContent = item.label;
      button.disabled = item.label !== '·'; button.addEventListener('click', () => play(item.value)); grid.appendChild(button);
    }); controls.appendChild(grid); return;
  }
  if (view.input_type === 'number' || view.input_type === 'text') {
    const input = document.createElement('input'); input.className = 'game-input'; input.type = view.input_type === 'number' ? 'number' : 'text';
    input.placeholder = view.placeholder || ''; input.autocomplete = 'off';
    if (activeGame === 'hangman') { input.maxLength = 1; input.setAttribute('aria-label','اكتب حرفاً'); }
    const submit = document.createElement('button'); submit.className = 'submit-button'; submit.textContent = 'إرسال';
    const submitValue = () => { if (input.value.trim()) { play(input.value.trim()); input.value = ''; input.focus(); } };
    submit.addEventListener('click', submitValue); input.addEventListener('keydown', e => { if (e.key === 'Enter') submitValue(); });
    controls.append(input, submit); input.focus(); return;
  }
  (view.options || []).forEach(item => {
    const button = document.createElement('button'); button.className = 'answer-button'; button.textContent = item.label;
    button.addEventListener('click', () => play(item.value)); controls.appendChild(button);
  });
}
async function play(action) {
  try { showView(await post('/api/action', {game_id: activeGame, action})); }
  catch (error) { document.getElementById('game-message').textContent = error.message; }
}
async function startGame(id) {
  activeGame = id; const game = games[id];
  document.getElementById('play-icon').textContent = game.icon;
  document.getElementById('play-title').textContent = game.title;
  area.hidden = false; document.body.style.overflow = 'hidden';
  controls.textContent = 'جارٍ التحضير…';
  try { showView(await post('/api/start', {game_id: id})); }
  catch (error) { controls.textContent = error.message; }
}
document.querySelectorAll('.play-button').forEach(button => button.addEventListener('click', () => startGame(button.dataset.game)));
document.getElementById('restart-game').addEventListener('click', () => startGame(activeGame));
function closeGame() { area.hidden = true; document.body.style.overflow = ''; }
document.getElementById('close-game').addEventListener('click', closeGame);
area.addEventListener('click', event => { if (event.target === area) closeGame(); });
document.addEventListener('keydown', event => { if (event.key === 'Escape' && !area.hidden) closeGame(); });
