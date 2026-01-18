import React, { useState, useEffect, useRef } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api';

// --- Icons (Polished & Rounded) ---
const SendIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>
);
const AttachIcon = () => (
  <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21.44 11.05l-9.19 9.19a6 6 0 0 1-8.49-8.49l9.19-9.19a4 4 0 0 1 5.66 5.66l-9.2 9.19a2 2 0 0 1-2.83-2.83l8.49-8.48"></path></svg>
);
const FileIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M13 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V9z"></path><polyline points="13 2 13 9 20 9"></polyline></svg>
);
const ChatIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z"></path></svg>
);
const TrashIcon = () => (
  <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
);
const LogoutIcon = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M9 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h4"></path><polyline points="16 17 21 12 16 7"></polyline><line x1="21" y1="12" x2="9" y2="12"></line></svg>
);

export default function MainPage() {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [selectedFile, setSelectedFile] = useState(null); 
  const [loading, setLoading] = useState(false);
  const [loadingText, setLoadingText] = useState("");
  const [history, setHistory] = useState([]);
  
  const navigate = useNavigate();
  const fileInputRef = useRef(null);
  const chatEndRef = useRef(null);

  // User Data
  const userName = localStorage.getItem('user_name') || 'User';
  const userId = localStorage.getItem('user_id') || '1'; 

  // --- 1. Load History ---
  useEffect(() => {
    fetchHistory();
  }, [userId]);

  const fetchHistory = async () => {
    try {
      const safeId = userId;
      const response = await api.get(`/chat/history/${safeId}`);
      if (Array.isArray(response.data)) {
        setHistory(response.data.reverse()); // Show newest first
      }
    } catch (error) {
      console.error("Failed to load history", error);
    }
  };

  // --- 2. Load Chat Logic ---
  const loadChatFromHistory = (item) => {
    setMessages([
        { role: "user", content: item.query },
        { role: "assistant", content: item.response || item.answer || "No response saved." }
    ]);
  };

  const startNewChat = () => {
    setMessages([]);
    setInput("");
    setSelectedFile(null);
  };

  // --- 3. File Handling ---
  const handleFileSelect = (e) => {
    const file = e.target.files[0];
    if (file) {
      setSelectedFile(file);
      setInput(""); 
    }
  };

  const clearFile = () => {
    setSelectedFile(null);
    if (fileInputRef.current) fileInputRef.current.value = "";
  };

  // --- 4. Send Message / Upload ---
  const handleSend = async (e) => {
    e.preventDefault();

    // A. File Upload Flow
    if (selectedFile) {
      await uploadFile(selectedFile);
      return;
    }

    // B. Text Chat Flow
    if (!input.trim()) return;
    
    const userMsg = { role: "user", content: input };
    setMessages((prev) => [...prev, userMsg]);
    setInput("");
    setLoading(true);
    setLoadingText("");

    try {
      const token = localStorage.getItem('token');
      const data = await fetch('http://superb-exploration.railway.internal:8000/chat/', {
        method: 'POST', 
        headers: { 'Content-Type': 'application/json' }, 
        body: JSON.stringify({ query: userMsg.content, 
        user_id: parseInt(userId) || 1, token: token })
      }); 
      
      const response = await data.json()
      
      const botMsg = { 
        role: "assistant", 
        content: response.data|| response.answer || "No response received." 
      };
      
      setMessages((prev) => [...prev, botMsg]);
      fetchHistory(); // Update sidebar

    } catch (error) {
      console.error("Chat Error:", error);
      let errorMsg = "An unexpected error occurred.";
      
      // Safe Error Handling to prevent crashes
      if (error.response && error.response.data) {
          errorMsg = `Server Error: ${JSON.stringify(error.response.data.detail || error.response.data)}`;
      } else if (error.message) {
          errorMsg = `Network Error: ${error.message}`;
      }

      setMessages((prev) => [...prev, { role: "assistant", content: errorMsg }]);
    } finally {
      setLoading(false);
    }
  };

  const uploadFile = async (file) => {
    setLoading(true);
    setLoadingText("File is being ingested..."); // Requirement met

    setMessages((prev) => [...prev, { role: "user", content: `📎 Uploading: ${file.name}` }]);

    const formData = new FormData();
    formData.append('file', file);

    try {
       // Critical Fix for FormData
       await api.post('/documents/upload', formData, {
         headers: { 'Content-Type': undefined }
       });
       
       setMessages((prev) => [...prev, { role: "assistant", content: `✅ **${file.name}** ingested successfully. Ready for questions.` }]);
       clearFile();
       
    } catch (error) {
       console.error("Upload failed", error);
       let errorMsg = "Ingestion failed.";
       
       if (error.response?.data?.detail) {
         errorMsg = `Upload Failed: ${JSON.stringify(error.response.data.detail)}`;
       }
       setMessages((prev) => [...prev, { role: "assistant", content: `❌ ${errorMsg}` }]);
       clearFile();
    } finally {
       setLoading(false);
       setLoadingText("");
    }
  };

  useEffect(() => {
    chatEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages, loading]);

  const handleLogout = () => {
    localStorage.clear();
    navigate('/login');
  };

  return (
    <div className="flex h-screen bg-gray-50 overflow-hidden font-sans text-gray-800">
      
      {/* --- SIDEBAR (Rounder, cleaner aesthetic) --- */}
      <div className="w-[280px] bg-[#1e2329] flex-shrink-0 flex flex-col shadow-2xl z-20">
        {/* Header */}
        <div className="p-5 flex items-center justify-between">
           <div className="flex items-center gap-3 text-white">
              <div className="w-8 h-8 bg-indigo-500 rounded-xl flex items-center justify-center shadow-lg shadow-indigo-500/30">
                 <span className="font-bold text-sm">AI</span>
              </div>
              <h2 className="font-semibold tracking-tight">Workspace</h2>
           </div>
           <button onClick={startNewChat} className="p-2 bg-[#2d333b] hover:bg-[#373e48] rounded-lg text-gray-300 transition-colors" title="New Chat">
             <ChatIcon />
           </button>
        </div>

        {/* Scrollable History */}
        <div className="flex-1 overflow-y-auto px-3 py-2 space-y-1 custom-scrollbar">
          <div className="px-3 pb-2 text-xs font-semibold text-gray-500 uppercase tracking-wider">History</div>
          {history.length === 0 && (
             <div className="px-4 py-4 text-center text-gray-500 text-sm italic">No recent chats</div>
          )}
          {history.map((item, idx) => (
            <button 
               key={idx} 
               onClick={() => loadChatFromHistory(item)}
               className="w-full text-left px-4 py-3 rounded-xl hover:bg-[#2d333b] group transition-all duration-200"
            >
              <p className="text-gray-300 text-sm font-medium truncate group-hover:text-white">
                {item.query ? item.query.substring(0, 25) : "New Conversation"}
              </p>
              <p className="text-gray-500 text-xs truncate mt-0.5 group-hover:text-gray-400">
                {item.response ? item.response.substring(0, 30) : "..."}
              </p>
            </button>
          ))}
        </div>

        {/* User Profile Footer */}
        <div className="p-4 bg-[#181b20] mt-auto">
          <div className="flex items-center justify-between bg-[#23272d] p-3 rounded-xl border border-[#2d333b]">
             <div className="flex items-center gap-3">
                <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-indigo-500 to-purple-500 flex items-center justify-center text-white text-xs font-bold">
                   {userName.charAt(0).toUpperCase()}
                </div>
                <div className="overflow-hidden">
                   <p className="text-sm font-medium text-white truncate w-20">{userName}</p>
                   <p className="text-[10px] text-green-400">● Online</p>
                </div>
             </div>
             <button onClick={handleLogout} className="text-gray-400 hover:text-white transition-colors">
               <LogoutIcon />
             </button>
          </div>
        </div>
      </div>

      {/* --- MAIN CHAT AREA --- */}
      <div className="flex-1 flex flex-col min-w-0 bg-white rounded-l-[2rem] shadow-[-10px_0_30px_-10px_rgba(0,0,0,0.1)] overflow-hidden my-2 mr-2 border border-gray-100 relative">
        
        {/* Chat Header */}
        <header className="px-8 py-5 border-b border-gray-100 flex items-center justify-between bg-white z-10">
           <div>
              <h1 className="text-xl font-bold text-gray-900 tracking-tight">Compliance Assistant</h1>
              <p className="text-xs text-gray-500 mt-1">Powered by RAG • Secure Context</p>
           </div>
        </header>

        {/* Messages List */}
        <div className="flex-1 overflow-y-auto p-6 space-y-8 bg-white">
          {messages.length === 0 && (
            <div className="h-full flex flex-col items-center justify-center text-center opacity-60 animate-in fade-in zoom-in duration-500">
               <div className="w-24 h-24 bg-indigo-50 rounded-3xl flex items-center justify-center mb-6 text-indigo-500 shadow-sm">
                  <ChatIcon />
               </div>
               <h3 className="text-2xl font-bold text-gray-800">Good day, {userName}</h3>
               <p className="text-gray-500 mt-2 max-w-sm">Upload a document to analyze or simply start typing to ask a question.</p>
            </div>
          )}

          {messages.map((msg, index) => (
            <div key={index} className={`flex w-full ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}>
              <div 
                className={`max-w-[80%] px-6 py-4 rounded-2xl text-[15px] leading-7 shadow-sm whitespace-pre-wrap ${
                  msg.role === 'user' 
                    ? 'bg-indigo-600 text-white rounded-br-none shadow-indigo-200' 
                    : 'bg-gray-100 text-gray-800 rounded-bl-none border border-gray-200'
                }`}
              >
                {msg.content}
              </div>
            </div>
          ))}
          
          {loading && (
             <div className="flex justify-start">
               <div className="bg-gray-50 border border-gray-200 px-6 py-4 rounded-2xl rounded-bl-none flex items-center gap-3">
                 <div className="flex gap-1">
                   <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce"></span>
                   <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-75"></span>
                   <span className="w-2 h-2 bg-indigo-400 rounded-full animate-bounce delay-150"></span>
                 </div>
                 <span className="text-sm text-gray-500 font-medium">{loadingText || "Thinking..."}</span>
               </div>
             </div>
          )}
          <div ref={chatEndRef} />
        </div>

        {/* --- INPUT AREA (Floating & Rounded) --- */}
        <div className="p-6 bg-white">
          <div className="max-w-4xl mx-auto relative">
             
             {/* Staged File Pill */}
             {selectedFile && (
               <div className="absolute -top-14 left-0 bg-white border border-indigo-100 shadow-lg shadow-indigo-500/10 text-indigo-700 px-4 py-2.5 rounded-xl flex items-center gap-3 animate-in slide-in-from-bottom-2">
                  <FileIcon />
                  <span className="font-semibold text-sm">{selectedFile.name}</span>
                  <span className="text-xs text-gray-400 px-2 border-l border-gray-200">Pending Upload</span>
                  <button onClick={clearFile} className="ml-2 text-gray-400 hover:text-red-500 transition-colors">
                     <TrashIcon />
                  </button>
               </div>
             )}

             <form 
               onSubmit={handleSend}
               className={`
                  flex items-center gap-2 p-2 rounded-2xl border transition-all duration-300 shadow-sm
                  ${selectedFile 
                     ? 'bg-gray-50 border-gray-200' 
                     : 'bg-white border-gray-200 hover:border-gray-300 focus-within:ring-4 focus-within:ring-indigo-50 focus-within:border-indigo-200'}
               `}
             >
               {/* File Input */}
               <input type="file" ref={fileInputRef} className="hidden" onChange={handleFileSelect} accept=".pdf,.txt,.docx" />
               
               <button
                  type="button"
                  onClick={() => fileInputRef.current.click()}
                  disabled={loading || selectedFile}
                  className="p-3 text-gray-400 hover:text-indigo-600 hover:bg-indigo-50 rounded-xl transition-all"
               >
                  <AttachIcon />
               </button>

               {/* Text Input */}
               <input
                  type="text"
                  value={input}
                  onChange={(e) => setInput(e.target.value)}
                  placeholder={selectedFile ? "⚠️ Click send to ingest file (typing disabled)..." : "Ask a question..."}
                  disabled={loading || selectedFile !== null}
                  className={`flex-1 bg-transparent px-2 py-2 focus:outline-none text-gray-800 placeholder-gray-400
                    ${selectedFile ? 'cursor-not-allowed italic text-gray-500' : ''}`}
               />

               {/* Send Button */}
               <button
                  type="submit"
                  disabled={loading || (!input.trim() && !selectedFile)}
                  className={`p-3 rounded-xl transition-all duration-200
                     ${(input.trim() || selectedFile) && !loading
                        ? 'bg-indigo-600 text-white shadow-md shadow-indigo-200 hover:bg-indigo-700 hover:scale-105 active:scale-95' 
                        : 'bg-gray-100 text-gray-300 cursor-not-allowed'}
                  `}
               >
                 <SendIcon />
               </button>
             </form>
             
             <div className="text-center mt-3">
               <p className="text-[11px] text-gray-400">
                 {selectedFile 
                    ? "File must be uploaded before asking questions." 
                    : "AI can make mistakes. Please verify important information."}
               </p>
             </div>
          </div>
        </div>

      </div>
    </div>
  );
}