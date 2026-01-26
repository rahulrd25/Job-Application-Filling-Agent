import { useState, useEffect } from 'react';
import './Questionnaire.css';

interface Question {
    key: string;
    category: string;
    question: string;
    type: string;
    required: boolean;
    options?: string[];
}

interface QuestionnaireProps {
    userId: string;
    onComplete: () => void;
    backendUrl: string;
}

const CATEGORY_NAMES: Record<string, string> = {
    personal: '📋 Personal Information',
    professional_links: '🔗 Professional Links',
    education: '🎓 Education',
    work_history: '💼 Work History',
    logistics: '📅 Logistics & Availability',
    legal: '⚖️ Work Authorization',
    screening: '🔍 Screening Questions',
    self_id: '👤 Voluntary Self-ID',
    accessibility: '♿ Accessibility',
    pitch: '🚀 Experience & Pitch'
};

export default function Questionnaire({ userId, onComplete, backendUrl }: QuestionnaireProps) {
    const [categories, setCategories] = useState<Record<string, Question[]>>({});
    const [currentCategoryIndex, setCurrentCategoryIndex] = useState(0);
    const [answers, setAnswers] = useState<Record<string, string>>({});
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState('');

    const categoryKeys = Object.keys(categories);
    const currentCategoryKey = categoryKeys[currentCategoryIndex];
    const currentQuestions = categories[currentCategoryKey] || [];
    const progress = ((currentCategoryIndex + 1) / categoryKeys.length) * 100;

    useEffect(() => {
        fetchQuestions();
        // Force-expand the extension popup width
        document.body.style.width = '500px';
        return () => {
            document.body.style.width = 'auto';
        };
    }, []);

    const fetchQuestions = async () => {
        try {
            const res = await fetch(`${backendUrl}/questions`);
            const data = await res.json();
            setCategories(data.categories);
            setLoading(false);
        } catch (err) {
            setError('Failed to load questions. Please refresh.');
            setLoading(false);
        }
    };

    const handleInputChange = (questionKey: string, value: string) => {
        setAnswers(prev => ({ ...prev, [questionKey]: value }));
    };

    const handleNext = () => {
        if (currentCategoryIndex < categoryKeys.length - 1) {
            setCurrentCategoryIndex(prev => prev + 1);
        }
    };

    const handleBack = () => {
        if (currentCategoryIndex > 0) {
            setCurrentCategoryIndex(prev => prev - 1);
        }
    };

    const handleSubmit = async () => {
        setSaving(true);
        setError('');

        try {
            // Filter out empty answers and format for backend
            const answersToSave = Object.entries(answers)
                .filter(([_, value]) => value && value.trim())
                .map(([question_key, answer]) => ({ question_key, answer }));

            const res = await fetch(`${backendUrl}/save-answers`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'x-user-id': userId
                },
                body: JSON.stringify({ answers: answersToSave })
            });

            if (!res.ok) throw new Error('Failed to save answers');

            onComplete();
        } catch (err: any) {
            setError(err.message || 'Failed to save. Please try again.');
            setSaving(false);
        }
    };

    const isCurrentCategoryComplete = () => {
        return currentQuestions
            .filter(q => q.required)
            .every(q => answers[q.key] && answers[q.key].trim());
    };

    const isLastCategory = currentCategoryIndex === categoryKeys.length - 1;

    if (loading) {
        return (
            <div className="questionnaire-container">
                <div className="loading">Loading questions...</div>
            </div>
        );
    }

    if (error && categoryKeys.length === 0) {
        return (
            <div className="questionnaire-container">
                <div className="error">{error}</div>
            </div>
        );
    }

    return (
        <div className="questionnaire-container">
            <div className="questionnaire-header">
                <h1>Complete Your Profile</h1>
                <div className="progress-bar">
                    <div className="progress-fill" style={{ width: `${progress}%` }} />
                </div>
                <p className="progress-text">
                    Step {currentCategoryIndex + 1} of {categoryKeys.length}
                </p>
            </div>

            <div className="category-section">
                <h2>{CATEGORY_NAMES[currentCategoryKey] || currentCategoryKey}</h2>

                <div className="questions-list">
                    {currentQuestions.map(question => (
                        <div key={question.key} className="question-item">
                            <label htmlFor={question.key}>
                                {question.question}
                                {question.required && <span className="required">*</span>}
                            </label>

                            {question.type === 'select' && question.options ? (
                                <select
                                    id={question.key}
                                    value={answers[question.key] || ''}
                                    onChange={(e) => handleInputChange(question.key, e.target.value)}
                                    required={question.required}
                                >
                                    <option value="">Select...</option>
                                    {question.options.map(opt => (
                                        <option key={opt} value={opt}>{opt}</option>
                                    ))}
                                </select>
                            ) : question.type === 'textarea' ? (
                                <textarea
                                    id={question.key}
                                    value={answers[question.key] || ''}
                                    onChange={(e) => handleInputChange(question.key, e.target.value)}
                                    required={question.required}
                                    rows={3}
                                />
                            ) : (
                                <input
                                    id={question.key}
                                    type={question.type}
                                    value={answers[question.key] || ''}
                                    onChange={(e) => handleInputChange(question.key, e.target.value)}
                                    required={question.required}
                                />
                            )}
                        </div>
                    ))}
                </div>
            </div>

            {error && <div className="error-message">{error}</div>}

            <div className="navigation-buttons">
                <button
                    onClick={handleBack}
                    disabled={currentCategoryIndex === 0}
                    className="btn-secondary"
                >
                    ← Back
                </button>

                {isLastCategory ? (
                    <button
                        onClick={handleSubmit}
                        disabled={saving || !isCurrentCategoryComplete()}
                        className="btn-primary"
                    >
                        {saving ? 'Saving...' : 'Complete Setup ✓'}
                    </button>
                ) : (
                    <button
                        onClick={handleNext}
                        disabled={!isCurrentCategoryComplete()}
                        className="btn-primary"
                    >
                        Next →
                    </button>
                )}
            </div>

            <div className="help-text">
                <p>
                    <small>
                        Required fields are marked with *. You can skip optional fields and fill them later.
                    </small>
                </p>
            </div>
        </div>
    );
}
