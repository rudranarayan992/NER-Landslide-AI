import React, { useState, useRef, useEffect } from 'react';
import { Send, X, MessageCircle } from 'lucide-react';

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: string;
}

interface DisasterAIAssistantProps {
  onClose: () => void;
  selectedLocation?: string;
}

export function DisasterAIAssistant({ onClose, selectedLocation }: DisasterAIAssistantProps) {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '0',
      role: 'assistant',
      content: 'Welcome to Disaster AI Assistant. I can help you understand landslide risks, explain available data, summarize historical events, and generate reports. What would you like to know?',
      timestamp: new Date().toISOString(),
    },
  ]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  const suggestedQuestions = [
    'Why is this location important?',
    'Show historical landslides nearby',
    'What roads are nearby?',
    'Explain this dataset',
    'Why is current risk unavailable?',
    'Generate a risk report',
  ];

  const handleSendMessage = async () => {
    if (!input.trim()) return;

    const userMessage: Message = {
      id: Date.now().toString(),
      role: 'user',
      content: input,
      timestamp: new Date().toISOString(),
    };

    setMessages((prev) => [...prev, userMessage]);
    setInput('');
    setLoading(true);

    try {
      // Call backend LLM endpoint
      const response = await fetch('/api/assistant/query', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          question: input,
          context: selectedLocation ? { selectedLocation } : undefined,
        }),
      });

      const data = await response.json();
      const assistantMessage: Message = {
        id: (Date.now() + 1).toString(),
        role: 'assistant',
        content: data.response || data.answer || 'I encountered an error processing your request.',
        timestamp: new Date().toISOString(),
      };

      setMessages((prev) => [...prev, assistantMessage]);
    } catch (error) {
      console.error('LLM request failed:', error);
      setMessages((prev) => [
        ...prev,
        {
          id: (Date.now() + 1).toString(),
          role: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          timestamp: new Date().toISOString(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestedQuestion = (question: string) => {
    setInput(question);
  };

  return (
    <div className="fixed bottom-4 right-4 w-96 rounded-lg border border-slate-700/70 bg-slate-950/95 shadow-2xl backdrop-blur-sm z-40 flex flex-col max-h-[600px]">
      {/* HEADER */}
      <div className="flex items-center justify-between p-3 border-b border-slate-700/50">
        <div className="flex items-center gap-2">
          <MessageCircle size={16} className="text-cyan-400" />
          <h2 className="text-sm font-bold text-cyan-300 uppercase tracking-[0.14em]">Ask Disaster AI</h2>
        </div>
        <button
          onClick={onClose}
          className="p-1 hover:bg-slate-700/60 rounded transition-colors"
        >
          <X size={16} className="text-slate-400" />
        </button>
      </div>

      {/* MESSAGES */}
      <div className="flex-1 overflow-y-auto p-3 space-y-3">
        {messages.length === 1 && (
          <div className="space-y-2">
            <p className="text-[10px] text-slate-400 uppercase tracking-[0.12em] font-semibold">Suggested Questions:</p>
            <div className="space-y-1">
              {suggestedQuestions.map((question, idx) => (
                <button
                  key={idx}
                  onClick={() => handleSuggestedQuestion(question)}
                  className="w-full text-left px-2 py-1.5 rounded bg-slate-900/60 border border-slate-700/50 hover:border-cyan-500/60 text-[10px] text-slate-300 hover:text-cyan-300 transition-colors"
                >
                  {question}
                </button>
              ))}
            </div>
          </div>
        )}

        {messages.map((message) => (
          <div
            key={message.id}
            className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
          >
            <div
              className={`max-w-xs px-3 py-2 rounded-lg ${
                message.role === 'user'
                  ? 'bg-cyan-600/80 text-white text-[11px]'
                  : 'bg-slate-900/60 border border-slate-700/50 text-slate-200 text-[11px]'
              }`}
            >
              {message.content}
            </div>
          </div>
        ))}

        {loading && (
          <div className="flex justify-start">
            <div className="bg-slate-900/60 border border-slate-700/50 px-3 py-2 rounded-lg text-[11px] text-slate-400">
              Thinking...
            </div>
          </div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* INPUT */}
      <div className="border-t border-slate-700/50 p-3 flex gap-2">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === 'Enter' && handleSendMessage()}
          placeholder="Ask about this location..."
          disabled={loading}
          className="flex-1 px-2 py-1.5 bg-slate-900/60 border border-slate-700/50 rounded text-[11px] text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500/60 disabled:opacity-50"
        />
        <button
          onClick={handleSendMessage}
          disabled={loading || !input.trim()}
          className="p-1.5 bg-cyan-600/80 hover:bg-cyan-500/80 disabled:opacity-50 disabled:cursor-not-allowed text-white rounded transition-colors"
        >
          <Send size={14} />
        </button>
      </div>

      {/* STATUS */}
      <div className="border-t border-slate-700/50 px-3 py-2 bg-slate-900/60 text-[9px] text-slate-400">
        <span className="text-cyan-300">ℹ</span> LLM provides historical context and explanations. Not a real-time warning system.
      </div>
    </div>
  );
}
