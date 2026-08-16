(() => {
  const files = Array.isArray(window.SOURCE_FILES) ? window.SOURCE_FILES : [];
  const tree = document.querySelector('#source-tree');
  const search = document.querySelector('#source-search');
  const count = document.querySelector('#file-count');
  const name = document.querySelector('#code-name');
  const path = document.querySelector('#code-path');
  const language = document.querySelector('#code-language');
  const status = document.querySelector('#code-status');
  const view = document.querySelector('#code-view code');
  let selected = null;
  count.textContent = `${files.length} текстовых файлов`;
  function render(filter = '') {
    const value = filter.trim().toLowerCase();
    const shown = files.filter(file => file.path.toLowerCase().includes(value));
    tree.replaceChildren();
    if (!shown.length) { tree.textContent = 'Ничего не найдено.'; return; }
    const groups = new Map();
    shown.forEach(file => {
      const chunks = file.path.split('/'); chunks.shift();
      const folder = chunks.length > 1 ? chunks.slice(0, -1).join('/') : 'Корень';
      if (!groups.has(folder)) groups.set(folder, []);
      groups.get(folder).push(file);
    });
    groups.forEach((items, folder) => {
      const section = document.createElement('section'); section.className = 'tree-folder';
      const heading = document.createElement('p'); heading.textContent = folder === 'Корень' ? 'HS0.7SRC' : folder; section.append(heading);
      items.forEach(file => {
        const button = document.createElement('button'); button.type = 'button'; button.className = 'tree-file' + (selected?.path === file.path ? ' is-active' : '');
        button.textContent = file.name; button.title = file.path; button.addEventListener('click', () => openFile(file)); section.append(button);
      });
      tree.append(section);
    });
  }
  async function openFile(file) {
    selected = file; render(search.value);
    name.textContent = file.name; path.textContent = file.path; language.textContent = file.language;
    status.hidden = false; status.textContent = 'Загрузка…'; view.textContent = '';
    try {
      const response = await fetch(encodeURI(file.path), {cache: 'no-cache'});
      if (!response.ok) throw new Error(String(response.status));
      const text = await response.text();
      view.textContent = text;
      status.hidden = true;
      history.replaceState(null, '', '#'+encodeURIComponent(file.path));
    } catch (error) { status.textContent = 'Не удалось загрузить файл. Откройте сайт через GitHub Pages или локальный веб-сервер.'; }
  }
  search.addEventListener('input', () => render(search.value));
  render();
  const requested = decodeURIComponent(location.hash.slice(1));
  const initial = files.find(file => file.path === requested) || files.find(file => file.name === 'main.py') || files[0];
  if (initial) openFile(initial);
})();