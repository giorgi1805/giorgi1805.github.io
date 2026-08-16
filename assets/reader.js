(() => {
  const params = new URLSearchParams(window.location.search);
  const source = params.get('file');
  const title = params.get('title');
  const category = params.get('category');
  const content = document.getElementById('reading-content');
  const titleNode = document.getElementById('reading-title');
  const categoryNode = document.getElementById('reading-category');
  const metaNode = document.getElementById('reading-meta');

  const allowed = /^(notes\/[A-Za-zА-Яа-яЁё0-9_./ -]+\.(txt|md))$/u;
  if (!source || !allowed.test(source) || source.includes('..')) {
    titleNode.textContent = 'Заметка не найдена';
    content.innerHTML = '<p>Выберите материал в разделе <a href="index.html#notes">«Заметки»</a>.</p>';
    return;
  }

  const fallbackTitle = source.split('/').pop().replace(/\.(txt|md)$/i, '');
  titleNode.textContent = title || fallbackTitle;
  categoryNode.textContent = category || 'ЗАМЕТКА';
  document.title = `${titleNode.textContent} — giorgi1805`;

  fetch(source)
    .then(response => {
      if (!response.ok) throw new Error('Файл не найден');
      return response.text();
    })
    .then(text => {
      const lines = text.replace(/\r\n/g, '\n').split('\n');
      const words = text.trim() ? text.trim().split(/\s+/u).length : 0;
      metaNode.textContent = `${words.toLocaleString('ru-RU')} слов · ${source.endsWith('.md') ? 'Markdown' : 'Текстовая заметка'}`;
      content.replaceChildren();

      let paragraph = [];
      const flush = () => {
        if (!paragraph.length) return;
        const p = document.createElement('p');
        p.textContent = paragraph.join(' ');
        content.appendChild(p);
        paragraph = [];
      };

      lines.forEach(line => {
        const value = line.trim();
        if (!value) { flush(); return; }
        const heading = value.match(/^(#{1,3})\s+(.+)$/);
        if (heading) {
          flush();
          const h = document.createElement(`h${heading[1].length + 1}`);
          h.textContent = heading[2];
          content.appendChild(h);
          return;
        }
        if (/^[-*•]\s+/.test(value)) {
          flush();
          let list = content.lastElementChild;
          if (!list || list.tagName !== 'UL') {
            list = document.createElement('ul');
            content.appendChild(list);
          }
          const li = document.createElement('li');
          li.textContent = value.replace(/^[-*•]\s+/, '');
          list.appendChild(li);
          return;
        }
        paragraph.push(value);
      });
      flush();

      if (!content.children.length) content.innerHTML = '<p>В этой заметке пока нет текста.</p>';
    })
    .catch(() => {
      titleNode.textContent = 'Не удалось открыть заметку';
      content.innerHTML = '<p>Файл недоступен. Вернитесь к <a href="index.html#notes">списку заметок</a> и попробуйте снова.</p>';
    });
})();
