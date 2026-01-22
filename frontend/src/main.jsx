import React from 'react'
import ReactDOM from 'react-dom/client'
import App from './App'
import './styles/index.css'

// #region agent log
const __agentLog = (payload) => {
  try {
    window.__debugBuffer = window.__debugBuffer || [];
    window.__debugBuffer.push(payload);
    // eslint-disable-next-line no-console
    console.log('[debug]', payload);
  } catch {}
  fetch('http://127.0.0.1:7243/ingest/a090e97f-e35b-4efd-9272-c010d2bb89a9',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(payload)}).catch(()=>{});
};
// #endregion

// #region agent log
window.addEventListener('error', (event) => {
  __agentLog({location:'frontend/src/main.jsx:global_error',message:'window_error',data:{message:String(event?.message||''),filename:String(event?.filename||''),lineno:event?.lineno,colno:event?.colno},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'});
});
// #endregion

// #region agent log
window.addEventListener('unhandledrejection', (event) => {
  const reason = event?.reason;
  __agentLog({location:'frontend/src/main.jsx:unhandledrejection',message:'unhandled_promise_rejection',data:{reasonType:typeof reason,reasonMessage:String(reason?.message||reason||'')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'});
});
// #endregion

// #region agent log
__agentLog({location:'frontend/src/main.jsx:render',message:'react_root_render',data:{hasRoot:!!document.getElementById('root')},timestamp:Date.now(),sessionId:'debug-session',runId:'run1',hypothesisId:'A'});
// #endregion

ReactDOM.createRoot(document.getElementById('root')).render(
  <React.StrictMode>
    <App />
  </React.StrictMode>,
)
