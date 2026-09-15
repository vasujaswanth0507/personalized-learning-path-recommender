import React, { useState, useEffect, useRef } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import { BotIcon, XIcon, ArrowRightIcon } from './Icons';
import MarkdownRenderer from './MarkdownRenderer';

export default function AIMentorDrawer() {
  const {
    activeLearner,
    isMentorOpen,
    setIsMentorOpen,
    mentorContextTopic,
  } = useLearner();

  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const [suggestedFollowups, setSuggestedFollowups] = useState([
    'Why is this topic recommended now?',
    'I only have 1 hour today',
    'Explain this concept simply',
    'What should I build after completing this?',
  ]);

  const messagesEndRef = useRef(null);

  useEffect(() => {
    if (isMentorOpen && activeLearner) {
      api.getMentorHistory(activeLearner.id)
        .then((history) => {
          if (history && history.length > 0) {
            setMessages(history);
          } else {
            setMessages([
              {
                id: 'init',
                sender: 'mentor',
                content: `Hello ${activeLearner.name}. I'm your mentor. I track your progress toward ${activeLearner.target_goal}. How can I help you with your learning path today?`,
                context_tag: mentorContextTopic || activeLearner.direction,
              },
            ]);
          }
        })
        .catch((err) => console.error('Failed to load mentor history:', err));
    }
  }, [isMentorOpen, activeLearner]);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, isLoading]);

  if (!isMentorOpen || !activeLearner) return null;

  const handleSend = async (textToSend) => {
    const query = textToSend || inputMessage;
    if (!query.trim() || isLoading) return;

    setInputMessage('');
    const userMsg = {
      id: Date.now(),
      sender: 'user',
      content: query,
      context_tag: mentorContextTopic || '',
    };
    setMessages((prev) => [...prev, userMsg]);
    setIsLoading(true);

    try {
      const res = await api.askMentor(
        activeLearner.id,
        query,
        mentorContextTopic || '',
        activeLearner.direction || ''
      );

      const mentorMsg = {
        id: Date.now() + 1,
        sender: 'mentor',
        content: res.reply,
        context_tag: mentorContextTopic || '',
      };
      setMessages((prev) => [...prev, mentorMsg]);
      if (res.suggested_followups && res.suggested_followups.length > 0) {
        setSuggestedFollowups(res.suggested_followups);
      }
    } catch (err) {
      setMessages((prev) => [
        ...prev,
        {
          id: Date.now() + 1,
          sender: 'mentor',
          content: 'Unable to reach the assistant right now. Please review your roadmap stages or try again shortly.',
          context_tag: '',
        },
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="drawer-overlay" onClick={() => setIsMentorOpen(false)}>
      <div className="drawer-container" onClick={(e) => e.stopPropagation()}>
        {/* Header */}
        <div style={{ padding: '16px 20px', borderBottom: '1px solid var(--color-border)', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: '10px' }}>
            <div
              style={{
                width: '32px',
                height: '32px',
                borderRadius: 'var(--radius-sm)',
                backgroundColor: 'var(--primary-50)',
                color: 'var(--primary-700)',
                display: 'flex',
                alignItems: 'center',
                justifyContent: 'center',
              }}
            >
              <BotIcon size={18} />
            </div>
            <div>
              <div style={{ fontSize: '14px', fontWeight: 600, color: 'var(--color-text-main)' }}>
                Your Mentor
              </div>
              <div style={{ fontSize: '12px', color: 'var(--color-text-muted)' }}>
                Guidance for {mentorContextTopic || activeLearner.direction}
              </div>
            </div>
          </div>

          <button
            onClick={() => setIsMentorOpen(false)}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
          >
            <XIcon size={18} />
          </button>
        </div>

        {/* Message Stream */}
        <div className="chat-stream">
          {messages.map((m, idx) => (
            <div
              key={idx}
              className={`chat-bubble-clean ${
                m.sender === 'user' ? 'chat-bubble-learner' : 'chat-bubble-mentor'
              }`}
            >
              <MarkdownRenderer content={m.content} />
            </div>
          ))}
          {isLoading && (
            <div className="chat-bubble-clean chat-bubble-mentor" style={{ color: 'var(--color-text-muted)', fontStyle: 'italic' }}>
              Referencing roadmap and progress...
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>

        {/* Suggested Followups */}
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px', padding: '8px 16px', background: 'var(--color-surface-subtle)' }}>
          {suggestedFollowups.map((chip, idx) => (
            <button
              key={idx}
              onClick={() => handleSend(chip)}
              disabled={isLoading}
              style={{
                background: '#ffffff',
                border: '1px solid var(--color-border)',
                padding: '4px 10px',
                borderRadius: 'var(--radius-full)',
                fontSize: '11.5px',
                color: 'var(--color-text-secondary)',
                cursor: 'pointer',
              }}
            >
              {chip}
            </button>
          ))}
        </div>

        {/* Input Row */}
        <div className="chat-input-row">
          <input
            type="text"
            className="text-input-clean"
            placeholder="Ask about your learning path, concepts, or pacing..."
            value={inputMessage}
            onChange={(e) => setInputMessage(e.target.value)}
            onKeyDown={(e) => e.key === 'Enter' && handleSend()}
            disabled={isLoading}
          />
          <button
            className="btn btn-primary btn-sm"
            onClick={() => handleSend()}
            disabled={!inputMessage.trim() || isLoading}
          >
            Send
          </button>
        </div>
      </div>
    </div>
  );
}
