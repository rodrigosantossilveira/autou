function copyReply(){
  const ta = document.getElementById('reply');
  ta.select();
  document.execCommand('copy');
  const label = document.createElement('div');
  label.textContent = 'Copiada!';
  label.style.position='fixed';label.style.bottom='20px';label.style.right='20px';
  label.style.background='#243056';label.style.padding='8px 12px';label.style.borderRadius='8px';
  document.body.appendChild(label);
  setTimeout(()=>label.remove(),1200);
}

function downloadJSON(){
  const ta = document.getElementById('reply');
  const meta = {
    reply: ta.value
  };
  const data = new Blob([JSON.stringify(meta,null,2)], {type:'application/json'});
  const url = URL.createObjectURL(data);
  const a = document.createElement('a');
  a.href = url; a.download = 'resultado.json';
  document.body.appendChild(a); a.click(); a.remove();
  URL.revokeObjectURL(url);
}
