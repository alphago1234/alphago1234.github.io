'use strict';
// Progressive enhancement: all publications remain available without JavaScript.
const tools = document.querySelector('.tools');
if (tools) {
  tools.classList.add('ready');
  const buttons = Array.from(document.querySelectorAll('[data-filter]'));
  const search = document.querySelector('#publication-search');
  const entries = Array.from(document.querySelectorAll('[data-publication]'));
  const count = document.querySelector('#result-count');
  const empty = document.querySelector('#empty-results');
  let category = 'all';
  function apply() {
    const query = search.value.trim().toLocaleLowerCase();
    let visible = 0;
    for (const entry of entries) {
      const matches = (category === 'all' || entry.dataset.category === category) && entry.textContent.toLocaleLowerCase().includes(query);
      entry.hidden = !matches;
      if (matches) visible++;
    }
    for (const group of document.querySelectorAll('[data-year-group]')) {
      group.hidden = !Array.from(group.querySelectorAll('[data-publication]')).some(entry => !entry.hidden);
    }
    count.textContent = `${visible} ${visible === 1 ? 'record' : 'records'}`;
    empty.hidden = visible !== 0;
  }
  for (const button of buttons) {
    button.addEventListener('click', () => {
      category = button.dataset.filter;
      for (const other of buttons) other.setAttribute('aria-pressed', String(other === button));
      apply();
    });
  }
  search.addEventListener('input', apply);
  apply();
}
