import React, { useState, useEffect } from 'react';
import { useLearner } from '../context/LearnerContext';
import { api } from '../api/client';
import { CheckCircleIcon, RefreshIcon, CheckIcon, ArrowRightIcon } from '../components/Icons';

export default function AssessmentPage({ setActivePage }) {
  const { activeLearner, showToast, refreshDashboard, openMentorWithContext } = useLearner();

  const [assessments, setAssessments] = useState([]);
  const [selectedAssessment, setSelectedAssessment] = useState(null);
  const [userAnswers, setUserAnswers] = useState({});
  const [submissionResult, setSubmissionResult] = useState(null);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [isLoading, setIsLoading] = useState(true);

  if (!activeLearner) {
    return (
      <div className="fresh-empty-state-panel">
        <h2 className="fresh-empty-title">YOUR ASSESSMENTS</h2>
        <p className="fresh-empty-desc">
          Your skill assessments will appear here once we understand what you're working toward.
        </p>
        <button className="btn btn-primary" onClick={() => setActivePage('onboarding')}>
          <span>Start Your Journey</span>
          <ArrowRightIcon size={14} />
        </button>
      </div>
    );
  }

  const fetchAssessments = async () => {
    setIsLoading(true);
    try {
      const params = {};
      if (activeLearner) {
        params.domain = activeLearner.direction;
      }
      const list = await api.getAssessments(params);
      setAssessments(list);
      if (list.length > 0 && !selectedAssessment) {
        setSelectedAssessment(list[0]);
      }
    } catch (err) {
      console.error('Failed to load assessments:', err);
    } finally {
      setIsLoading(false);
    }
  };

  useEffect(() => {
    fetchAssessments();
  }, [activeLearner]);

  const handleSelectOption = (questionIndex, optionIndex) => {
    if (submissionResult) return;
    setUserAnswers({ ...userAnswers, [questionIndex]: optionIndex });
  };

  const handleSubmitQuiz = async () => {
    if (!selectedAssessment || !activeLearner) return;

    const totalQ = selectedAssessment.questions.length;
    const answeredCount = Object.keys(userAnswers).length;
    if (answeredCount < totalQ) {
      showToast(`Please answer all ${totalQ} questions before submitting`, 'error');
      return;
    }

    const answersList = [];
    for (let i = 0; i < totalQ; i++) {
      answersList.push(userAnswers[i]);
    }

    setIsSubmitting(true);
    try {
      const res = await api.submitAssessment(selectedAssessment.id, activeLearner.id, answersList);
      setSubmissionResult(res);
      await refreshDashboard();
      if (res.passed) {
        showToast(`Passed with ${res.percentage}%`, 'success');
      } else {
        showToast(`Score: ${res.percentage}%. Refresher module added to roadmap.`, 'warning');
      }
    } catch (err) {
      showToast('Submission error: ' + err.message, 'error');
    } finally {
      setIsSubmitting(false);
    }
  };

  const handleRetake = () => {
    setUserAnswers({});
    setSubmissionResult(null);
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
      <div>
        <h2 style={{ fontSize: '20px', fontWeight: 700, color: 'var(--color-text-main)' }}>
          Topic Skill Assessments
        </h2>
        <p style={{ color: 'var(--color-text-muted)', fontSize: '13.5px', marginTop: '2px' }}>
          Evaluate conceptual proficiency and verify readiness for subsequent stages.
        </p>
      </div>

      {isLoading ? (
        <div style={{ textAlign: 'center', padding: '40px', color: 'var(--color-text-muted)' }}>
          Loading assessment catalog...
        </div>
      ) : assessments.length === 0 ? (
        <div className="card" style={{ textAlign: 'center', padding: '40px' }}>
          <p style={{ color: 'var(--color-text-muted)' }}>No assessments available for current domain.</p>
        </div>
      ) : (
        <div className="grid-2" style={{ alignItems: 'start' }}>
          {/* Active Quiz Card */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            {selectedAssessment && (
              <div className="card">
                <div className="card-header-clean">
                  <div>
                    <span className="badge badge-upcoming">{selectedAssessment.topic}</span>
                    <h3 className="card-title-clean" style={{ marginTop: '4px' }}>
                      {selectedAssessment.title}
                    </h3>
                    <p className="card-subtitle-clean">
                      Passing Threshold: {selectedAssessment.passing_percentage}% • {selectedAssessment.questions.length} questions
                    </p>
                  </div>
                  {submissionResult && (
                    <button className="btn btn-secondary btn-sm" onClick={handleRetake}>
                      <RefreshIcon size={13} />
                      <span>Retake</span>
                    </button>
                  )}
                </div>

                {/* Submission Result Notice */}
                {submissionResult && (
                  <div
                    style={{
                      padding: '12px 14px',
                      borderRadius: 'var(--radius-md)',
                      marginBottom: '16px',
                      backgroundColor: submissionResult.passed ? 'var(--success-bg)' : 'var(--warning-bg)',
                      border: `1px solid ${submissionResult.passed ? 'var(--success-border)' : 'var(--warning-border)'}`,
                    }}
                  >
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                      <span style={{ fontWeight: 600, fontSize: '13.5px', color: submissionResult.passed ? 'var(--success-text)' : 'var(--warning-text)' }}>
                        {submissionResult.passed ? 'Assessment Passed' : 'Needs Reinforcement'}
                      </span>
                      <span
                        className={`badge ${submissionResult.passed ? 'badge-completed' : 'badge-remedial'}`}
                      >
                        {submissionResult.score} / {submissionResult.total_questions} ({submissionResult.percentage}%)
                      </span>
                    </div>

                    <div style={{ fontSize: '12.5px', marginTop: '4px', color: 'var(--color-text-secondary)' }}>
                      Roadmap Adaptation: {submissionResult.adaptive_action}
                    </div>
                  </div>
                )}

                {/* Questions List */}
                <div style={{ display: 'flex', flexDirection: 'column', gap: '18px' }}>
                  {selectedAssessment.questions.map((q, qIdx) => {
                    const selectedOpt = userAnswers[qIdx];
                    const qResult = submissionResult?.question_results?.[qIdx];

                    return (
                      <div
                        key={q.id}
                        style={{
                          padding: '14px',
                          borderRadius: 'var(--radius-md)',
                          border: '1px solid var(--color-border)',
                          backgroundColor: '#fafbfc',
                        }}
                      >
                        <div style={{ fontSize: '13.5px', fontWeight: 600, marginBottom: '10px' }}>
                          {qIdx + 1}. {q.question_text}
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                          {q.options.map((opt, optIdx) => {
                            const isChosen = selectedOpt === optIdx;
                            let optBg = '#ffffff';
                            let optBorder = 'var(--color-border)';

                            if (submissionResult) {
                              if (optIdx === qResult?.correct_index) {
                                optBg = 'var(--success-bg)';
                                optBorder = 'var(--success-border)';
                              } else if (isChosen && !qResult?.is_correct) {
                                optBg = '#fef2f2';
                                optBorder = '#fca5a5';
                              }
                            } else if (isChosen) {
                              optBg = 'var(--primary-50)';
                              optBorder = 'var(--primary-600)';
                            }

                            return (
                              <div
                                key={optIdx}
                                onClick={() => handleSelectOption(qIdx, optIdx)}
                                style={{
                                  padding: '8px 12px',
                                  borderRadius: 'var(--radius-sm)',
                                  border: `1px solid ${optBorder}`,
                                  backgroundColor: optBg,
                                  cursor: submissionResult ? 'default' : 'pointer',
                                  fontSize: '13px',
                                  display: 'flex',
                                  alignItems: 'center',
                                  gap: '8px',
                                }}
                              >
                                <span
                                  style={{
                                    width: '18px',
                                    height: '18px',
                                    borderRadius: 'var(--radius-full)',
                                    border: `1px solid ${isChosen ? 'var(--primary-700)' : '#9ca3af'}`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                    fontSize: '10px',
                                    fontWeight: 600,
                                    background: isChosen ? 'var(--primary-700)' : 'transparent',
                                    color: isChosen ? 'white' : 'var(--color-text-muted)',
                                  }}
                                >
                                  {String.fromCharCode(65 + optIdx)}
                                </span>
                                <span style={{ flex: 1 }}>{opt}</span>
                              </div>
                            );
                          })}
                        </div>

                        {qResult && (
                          <div
                            style={{
                              marginTop: '10px',
                              padding: '8px 10px',
                              borderRadius: 'var(--radius-sm)',
                              backgroundColor: 'var(--color-surface-subtle)',
                              fontSize: '12px',
                              lineHeight: 1.45,
                              color: 'var(--color-text-secondary)',
                            }}
                          >
                            <strong>Explanation:</strong> {qResult.explanation}
                          </div>
                        )}
                      </div>
                    );
                  })}
                </div>

                {!submissionResult && (
                  <div style={{ marginTop: '18px', display: 'flex', justifyContent: 'flex-end' }}>
                    <button
                      className="btn btn-primary"
                      onClick={handleSubmitQuiz}
                      disabled={isSubmitting}
                    >
                      {isSubmitting ? 'Submitting...' : 'Submit Assessment'}
                    </button>
                  </div>
                )}
              </div>
            )}
          </div>

          {/* Assessment Catalog Picker */}
          <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
            <div className="card">
              <div className="card-header-clean">
                <h3 className="card-title-clean">Available Quizzes</h3>
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: '6px' }}>
                {assessments.map((a) => (
                  <div
                    key={a.id}
                    onClick={() => {
                      setSelectedAssessment(a);
                      setUserAnswers({});
                      setSubmissionResult(null);
                    }}
                    style={{
                      padding: '10px 12px',
                      borderRadius: 'var(--radius-sm)',
                      border: selectedAssessment?.id === a.id ? '1.5px solid var(--primary-700)' : '1px solid var(--color-border)',
                      backgroundColor: selectedAssessment?.id === a.id ? 'var(--primary-50)' : '#ffffff',
                      cursor: 'pointer',
                    }}
                  >
                    <div style={{ fontSize: '13.5px', fontWeight: 600 }}>{a.title}</div>
                    <div style={{ fontSize: '12px', color: 'var(--color-text-muted)', marginTop: '2px' }}>
                      {a.topic} · Pass {a.passing_percentage}%
                    </div>
                  </div>
                ))}
              </div>
            </div>

            <div className="card" style={{ backgroundColor: 'var(--color-surface-subtle)' }}>
              <div style={{ fontSize: '13px', fontWeight: 600, color: 'var(--color-text-main)', marginBottom: '4px' }}>
                Adaptive Assessment Logic
              </div>
              <p style={{ fontSize: '12.5px', color: 'var(--color-text-secondary)', lineHeight: 1.5 }}>
                Passing an assessment validates conceptual retention and unlocks subsequent locked stages. Scoring below 70% automatically injects a targeted refresher practice stage into your active roadmap.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
