import React, { useState } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import { XIcon } from './Icons';

export default function FeedbackModal({ onFeedbackSubmitted }) {
  const { activeLearner, feedbackItem, isFeedbackOpen, closeFeedback, showToast } = useLearner();
  const [rating, setRating] = useState('good');
  const [comment, setComment] = useState('');
  const [isSubmitting, setIsSubmitting] = useState(false);

  if (!isFeedbackOpen || !feedbackItem || !activeLearner) return null;

  const handleSubmit = async (e) => {
    e.preventDefault();
    setIsSubmitting(true);

    try {
      const res = await api.submitFeedback(activeLearner.id, {
        item_type: feedbackItem.type || 'stage',
        item_id: feedbackItem.id,
        item_title: feedbackItem.title || 'Learning Item',
        rating,
        comment,
      });

      showToast(res.action_applied || 'Feedback submitted and roadmap adapted', 'success');
      if (onFeedbackSubmitted) {
        onFeedbackSubmitted(res);
      }
      closeFeedback();
      setComment('');
    } catch (err) {
      showToast('Error submitting feedback: ' + err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const ratings = [
    { value: 'easy', label: 'Easy', desc: 'Already familiar or grasped quickly' },
    { value: 'good', label: 'Well Paced', desc: 'Appropriate challenge level' },
    { value: 'difficult', label: 'Difficult', desc: 'Need more practice or explanation' },
    { value: 'very_difficult', label: 'Very Difficult', desc: 'Struggling to follow the concepts' },
  ];

  return (
    <div className="modal-overlay" onClick={closeFeedback}>
      <div className="modal-dialog" onClick={(e) => e.stopPropagation()}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '16px' }}>
          <div>
            <h3 style={{ fontSize: '17px', fontWeight: 600, color: 'var(--color-text-main)' }}>
              Learning Item Feedback
            </h3>
            <p style={{ fontSize: '13px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
              Item: <strong>{feedbackItem.title}</strong>
            </p>
          </div>
          <button
            onClick={closeFeedback}
            style={{ background: 'none', border: 'none', cursor: 'pointer', color: 'var(--color-text-muted)' }}
          >
            <XIcon size={18} />
          </button>
        </div>

        <form onSubmit={handleSubmit}>
          <div style={{ marginBottom: '14px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '8px' }}>
              Select Pace & Comprehension
            </label>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px' }}>
              {ratings.map((r) => (
                <div
                  key={r.value}
                  onClick={() => setRating(r.value)}
                  style={{
                    border: rating === r.value ? '1.5px solid var(--primary-700)' : '1px solid var(--color-border)',
                    backgroundColor: rating === r.value ? 'var(--primary-50)' : '#ffffff',
                    borderRadius: 'var(--radius-sm)',
                    padding: '8px 10px',
                    cursor: 'pointer',
                  }}
                >
                  <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)' }}>
                    {r.label}
                  </div>
                  <div style={{ fontSize: '11px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                    {r.desc}
                  </div>
                </div>
              ))}
            </div>
          </div>

          <div style={{ marginBottom: '16px' }}>
            <label style={{ display: 'block', fontSize: '12px', fontWeight: 600, color: 'var(--color-text-muted)', marginBottom: '4px' }}>
              Learner Reflection or Notes (Optional)
            </label>
            <textarea
              className="text-input-clean"
              style={{ width: '100%', height: '70px' }}
              placeholder="e.g. 'I understand the theory but need more hands-on labs' or 'I already know this topic, let me skip ahead'"
              value={comment}
              onChange={(e) => setComment(e.target.value)}
            />
            <p style={{ fontSize: '11.5px', color: 'var(--color-text-muted)', marginTop: '4px' }}>
              Your feedback dynamically informs subsequent roadmap scheduling and practice recommendations.
            </p>
          </div>

          <div style={{ display: 'flex', justifyContent: 'flex-end', gap: '8px' }}>
            <button type="button" className="btn btn-secondary btn-sm" onClick={closeFeedback}>
              Cancel
            </button>
            <button type="submit" className="btn btn-primary btn-sm" disabled={isSubmitting}>
              {isSubmitting ? 'Submitting...' : 'Submit & Adapt Roadmap'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
}
