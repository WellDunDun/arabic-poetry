/* A compatible server may restart; only a clean, idle page may reload. */
(function (root) {
  'use strict';
  root.DiwanRuntimeUpdates = function (api, ready) {
    const loaded = root.DiwanFile.runtime;
    if (!loaded) return () => {};
    let busy = false, restarting = false, note;
    function message(text) {
      if (!note) {
        note = document.createElement('div'); note.className = 'note'; note.dir = 'rtl';
        note.id = 'runtimeUpdateStatus'; note.setAttribute('role', 'status');
        (document.querySelector('.app') || document.body).prepend(note);
      }
      note.textContent = text;
    }
    async function check() {
      if (busy) return;
      busy = true;
      try {
        const state = await api('/runtime');
        if (state.protocol !== 1 || state.id !== root.DiwanFile.id) return;
        if (state.version !== loaded) {
          message('تحديث ديوان جاهز. سيُطبّق بعد حفظ تعديلاتك وإغلاق أدوات التحرير.');
          if (ready()) root.location.reload();
        } else if (state.available && !restarting) {
          message('يتوفر تحديث لديوان؛ ننتظر حفظ تعديلاتك وانتهاء التحرير قبل تطبيقه.');
          if (ready()) {
            const result = await api('/runtime', {});
            restarting = result.restarting === true;
            if (restarting) message(ready() ? 'جارٍ تحديث ديوان. قصيدتك باقية في ملفها.'
              : 'بدأ التحديث؛ ستبقى مسودتك هنا حتى تؤكّد حفظها وينتهي التحرير.');
          }
        } else if (state.recovered) {
          restarting = false;
          message('تعذّر تشغيل التحديث؛ عاد ديوان إلى النسخة السابقة. قصيدتك ومسودتك باقية.');
        }
      } catch (error) {
        if (restarting) message('جارٍ إعادة الاتصال بعد التحديث؛ مسودتك باقية في المحرر.');
      } finally { busy = false; }
    }
    const timer = setInterval(check, 3000);
    return () => clearInterval(timer);
  };
})(typeof window === 'undefined' ? globalThis : window);
