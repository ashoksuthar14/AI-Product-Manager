// Simple loader that injects the full VoiceAgent implementation only once
if (!window.__voiceAgentLoaded) {
  window.__voiceAgentLoaded = true;

  /* Load the script contents from analyze page dynamically */
  // For brevity we will import by creating a script tag pointing to the same Vapi CDN when needed.
  // If you already copied the full VoiceAgent class elsewhere, you can paste it here.

  // --- MINIMAL FALLBACK USING Gemini-only echo (text) while you wire audio ----
  async function fakeReply(text){
    const div=document.createElement('div');
    div.textContent='🤖 (fake) '+text.split('').reverse().join('');
    document.getElementById('messages').appendChild(div);
  }

  document.addEventListener('DOMContentLoaded',()=>{
      const statusEl=document.getElementById('status');
      const startBtn=document.getElementById('start-btn');
      const stopBtn=document.getElementById('stop-btn');
      const messagesDiv=document.getElementById('messages');
      const statusSpan=document.getElementById('status');
      let mediaRecorder; let chunks=[]; let recordingTimeout;

      function setStatus(t){ statusSpan.textContent=t; }
      function addMsg(role,text){ const div=document.createElement('div'); div.innerHTML=`<strong>${role}:</strong> ${text}`; messagesDiv.appendChild(div); messagesDiv.scrollTop=messagesDiv.scrollHeight; }

      async function initMic(){
        const stream=await navigator.mediaDevices.getUserMedia({audio:true});
        mediaRecorder=new MediaRecorder(stream);
        mediaRecorder.ondataavailable=e=>{ if(e.data.size>0) chunks.push(e.data);}  
        mediaRecorder.onstop=sendToServer;
      }

      async function sendToServer(){
        setStatus('Processing…');
        const blob=new Blob(chunks,{type:'audio/webm'}); chunks=[];
        const fd=new FormData(); fd.append('audio',blob,'recording.webm');
        fd.append('workflow','Sample workflow');
        const res=await fetch('/voice/process',{method:'POST',body:fd});
        const json=await res.json();
        addMsg('You',json.transcript);
        addMsg('Assistant',json.reply_text);
        if(json.audio_b64){
           const audio=new Audio('data:audio/wav;base64,'+json.audio_b64); audio.play();
        }
        setStatus('Idle');
        startBtn.classList.remove('hidden'); stopBtn.classList.add('hidden');
      }

      startBtn.addEventListener('click',async()=>{
          if(!mediaRecorder) await initMic();
          chunks=[]; mediaRecorder.start(250); // emit data every 250ms
          setStatus('Recording…');
          console.log('🎤 recording started');
          recordingTimeout=setTimeout(()=>{ if(mediaRecorder.state==='recording'){ console.log('⏲️ auto stop'); mediaRecorder.stop(); }},5000);
          startBtn.classList.add('hidden'); stopBtn.classList.remove('hidden');
      });

      stopBtn.addEventListener('click',()=>{
          console.log('🛑 stop button pressed');
          clearTimeout(recordingTimeout);
          if(mediaRecorder && mediaRecorder.state==='recording'){
              mediaRecorder.stop();
              setStatus('Sending…');
          }
      });
  });
} 