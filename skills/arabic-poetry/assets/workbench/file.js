/* Shared-file transport. The server, not browser storage, owns the poem. */
(function (root) {
  'use strict';
  root.DiwanFileConnection = function (services) {
    const base = root.DiwanFile.base;
    let callback, failed, latest, seen, busy = false, retryKey = '', requestId = '';
    let status, actions;
    function panel(message, recovery) {
      if (!status) {
        const box = document.createElement('div');
        box.className = 'note'; box.dir = 'rtl'; box.id = 'sharedFileStatus';
        status = document.createElement('span'); actions = document.createElement('span');
        box.appendChild(status); box.appendChild(actions);
        (document.querySelector('.app') || document.body).prepend(box);
      }
      status.textContent = message; actions.replaceChildren();
      if (!recovery) return;
      const button = (label, action) => {
        const b = document.createElement('button'); b.type = 'button'; b.className = 'btn mini';
        b.textContent = label; b.onclick = action; actions.appendChild(b);
      };
      button('تنزيل مسودتي', () => {
        const draft = root.DiwanFileDraft && root.DiwanFileDraft();
        if (draft) services.downloads.save({ filename: 'diwan-unsaved-draft.json', data: JSON.stringify(draft, null, 2) });
      });
      if (recovery === 'retry') button('إعادة محاولة الحفظ نفسه', () => root.DiwanFileRetry && root.DiwanFileRetry());
      button('تجاهل مسودتي وتحميل المحفوظ', async () => {
        try {
          const value = await api('/document'); latest = value; seen = value.version; retryKey = ''; requestId = '';
          if (root.DiwanFileAccept) root.DiwanFileAccept(value);
          panel('حُمّلت النسخة المحفوظة، المراجعة ' + value.poem.revision);
        } catch (e) { panel(e.message, 'retry'); }
      });
    }
    async function api(path, body) {
      const response = await fetch(base + path, { cache: 'no-store', ...(body ? {
        method: 'POST', headers: { 'Content-Type': 'application/json' }, body: JSON.stringify(body)
      } : {}) });
      const value = await response.json();
      if (!response.ok) {
        const error = new Error(value.error && value.error.message || 'تعذّر الاتصال بالملف');
        error.code = value.error && value.error.code; error.status = response.status; throw error;
      }
      return value;
    }
    function snapshot(value) {
      const data = { ...value.poem, _file_version: value.version };
      return { docs: [{ id: data.id, data: () => ({ ...data }) }] };
    }
    async function poll() {
      if (busy || !callback) return;
      busy = true;
      try {
        const value = await api('/document'); latest = value;
        if (seen !== value.version) { seen = value.version; callback(snapshot(value)); }
      } catch (error) {
        if (!latest && failed) failed(error);
        panel('تعذّر قراءة الملف. بقيت مسودتك في المحرر؛ يمكنك تنزيلها.', 'retry');
      } finally { busy = false; }
    }
    const db = { collection() { return {
      onSnapshot(fn, error) { callback = fn; failed = error; poll(); const timer = setInterval(poll, 1000); return () => clearInterval(timer); },
      doc(id) { return {
        async set(body) {
          if (!latest || latest.poem.id !== id) throw new Error('افتح ملفًا مستقلًا للقصيدة الجديدة');
          const patch = Object.fromEntries(['title', 'text', 'choices', 'suggestions', 'status', 'mode', 'meter'].map(k => [k, body[k]]));
          const key = JSON.stringify([body._file_version, patch]);
          if (key !== retryKey) { retryKey = key; requestId = crypto.randomUUID().replace(/-/g, ''); }
          panel('جارٍ الحفظ في الملف…');
          try {
            const result = await api('/document', { patch, if_version: body._file_version, request_id: requestId }); latest = result;
            if (result.applied_version && result.applied_version !== result.version) {
              const error = new Error('حُفظ طلبك سابقًا ثم تغيّر الملف؛ حمّل أحدث نسخة قبل متابعة التعديل.');
              error.code = 'CONFLICT'; throw error;
            }
            panel('حُفظ في الملف، المراجعة ' + result.poem.revision);
            return { version: result.applied_version || result.version };
          } catch (error) {
            panel(error.status === 400 ? 'لم يُحفظ التعديل: ' + error.message : error.code === 'CONFLICT'
              ? 'حُفظت نسخة أحدث. لم نستبدلها؛ مسودتك باقية هنا. نزّلها قبل تحميل المحفوظ.'
              : 'لم يتأكد الحفظ. مسودتك باقية هنا؛ أعد المحاولة نفسها أو نزّلها.', error.status === 400 ? 'validation' : error.code === 'CONFLICT' ? 'conflict' : 'retry');
            throw error;
          }
        },
        async delete() { throw new Error('لا يحذف المحرر ملف القصيدة المشتركة'); }
      }; }
    }; } };
    return { ...services, label: 'قصيدة مشتركة مع وكيلك؛ الحفظ في الملف', db };
  };
})(typeof window === 'undefined' ? globalThis : window);
