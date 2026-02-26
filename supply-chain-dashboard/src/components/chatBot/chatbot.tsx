import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ragApi } from '../../api/ragbot';
import type { ChatMessage } from '../../types';

import { useStore } from '../../store/useStore';
import { v4 as uuidv4 } from 'uuid';

export const ChatBot = () => {
  const [messages, setMessages] = useState<ChatMessage[]>([{
    id: '0',
    role: 'assistant',
    content: 'Hi! I\'m your supply chain assistant. Ask me anything about your shipments, routes, or logistics data.',
    timestamp: new Date().toISOString(),
  }]);
  const [input, setInput] = useState('');
  const [loading, setLoading] = useState(false);
  const bottomRef = useRef<HTMLDivElement>(null);
  const sessionId = useRef(uuidv4());
  const { selectedShipmentId } = useStore();

  useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim() || loading) return;
    const userMsg: ChatMessage = {
      id: uuidv4(), role: 'user',
      content: input, timestamp: new Date().toISOString(),
    };
    setMessages(prev => [...prev, userMsg]);
    setInput('');
    setLoading(true);

    try {
      const res = await ragApi.chat({
        query: input,
        session_id: sessionId.current,
        context: selectedShipmentId
          ? `Current shipment context: ${selectedShipmentId}`
          : undefined,
      });
      const botMsg: ChatMessage = {
        id: uuidv4(), role: 'assistant',
        content: res.data.answer,
        sources: res.data.sources,
        timestamp: new Date().toISOString(),
      };
      setMessages(prev => [...prev, botMsg]);
    } catch {
      setMessages(prev => [...prev, {
        id: uuidv4(), role: 'assistant',
        content: 'Sorry, I couldn\'t connect to the knowledge base. Check if the RAG server is running.',
        timestamp: new Date().toISOString(),
      }]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', height: '100%' }}>
      {/* Messages */}
      <div style={{ flex: 1, overflowY: 'auto', padding: '16px', display: 'flex', flexDirection: 'column', gap: '12px' }}>
        <AnimatePresence>
          {messages.map((msg) => (
            <motion.div
              key={msg.id}
              initial={{ opacity: 0, y: 12 }}
              animate={{ opacity: 1, y: 0 }}
              style={{
                alignSelf: msg.role === 'user' ? 'flex-end' : 'flex-start',
                maxWidth: '80%',
                background: msg.role === 'user' ? '#00E5FF20' : '#1E1E2E',
                border: `1px solid ${msg.role === 'user' ? '#00E5FF40' : '#2A2A3E'}`,
                borderRadius: 12,
                padding: '10px 14px',
              }}
            >
              <p style={{ margin: 0, fontSize: 14, lineHeight: 1.5 }}>{msg.content}</p>
              {msg.sources && msg.sources.length > 0 && (
                <div style={{ marginTop: 8, fontSize: 11, color: '#888' }}>
                  Sources: {msg.sources.join(', ')}
                </div>
              )}
            </motion.div>
          ))}
        </AnimatePresence>
        {loading && (
          <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}
            style={{ alignSelf: 'flex-start', padding: '10px 14px', background: '#1E1E2E', borderRadius: 12 }}>
            <span>Thinking...</span>
          </motion.div>
        )}
        <div ref={bottomRef} />
      </div>

      {/* Input */}
      <div style={{ padding: '12px 16px', borderTop: '1px solid #2A2A3E', display: 'flex', gap: '8px' }}>
        <input
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyDown={(e) => e.key === 'Enter' && sendMessage()}
          placeholder="Ask about shipments, ETAs, routes..."
          style={{
            flex: 1, background: '#1E1E2E', border: '1px solid #2A2A3E',
            borderRadius: 8, padding: '10px 14px', color: '#fff', outline: 'none', fontSize: 14,
          }}
        />
        <button
          onClick={sendMessage} disabled={loading}
          style={{
            background: '#00E5FF', color: '#0A0A14', border: 'none',
            borderRadius: 8, padding: '10px 16px', cursor: 'pointer', fontWeight: 600,
          }}
        >
          Send
        </button>
      </div>
    </div>
  );
};