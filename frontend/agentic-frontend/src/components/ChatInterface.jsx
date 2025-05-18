// Updated frontend component to support inline PRINCE2 quiz
import React, { useState, useRef, useEffect } from 'react';

const ChatInterface = () => {
    const [message, setMessage] = useState('');
    const [history, setHistory] = useState([]);
    const [logs, setLogs] = useState([]);
    const [isLoading, setIsLoading] = useState(false);
    const [inlineQuiz, setInlineQuiz] = useState(null);
    const [answers, setAnswers] = useState([]);
    const [sessionId, setSessionId] = useState(null);
    const bottomRef = useRef(null);

    const handleSubmit = async (e) => {
        e.preventDefault();
        if (!message.trim()) return;

        setHistory(prev => [...prev, { role: 'user', content: message }]);
        setIsLoading(true);

        try {
            const res = await fetch('http://127.0.0.1:8000/agent-run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    message: message,
                    hisotry: history, // typo kept as in original
                    project_id: 'string',
                    document_text: '',
                    strategy: 'recursive',
                    n_results: 3
                })
            });

            const data = await res.json();
            console.log("📦 Données reçues du backend :", data);
            setHistory(prev => [...prev, { role: 'agent', content: data.agent_response }]);
            setLogs(data.history || []);

            if (data.action_taken === 'quiz_inline' && data.questions?.length > 0) {
                setInlineQuiz(data.questions);
                setSessionId(data.session_id);
            }

        } catch (error) {
            setHistory(prev => [...prev, { role: 'agent', content: 'Erreur lors de la requête.' }]);
        } finally {
            setIsLoading(false);
        }

        setMessage('');
    };

    const handleAnswerChange = (index, answer) => {
        const updated = [...answers];
        updated[index] = answer;
        setAnswers(updated);
    };

    const handleQuizSubmit = async () => {
        setIsLoading(true);
        try {
            const res = await fetch('http://127.0.0.1:8000/agent-run', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    answers: answers,
                    session_id: sessionId,
                    user_id: 'default',
                    message: 'résumé'
                })
            });
            const data = await res.json();
            setHistory(prev => [...prev, { role: 'agent', content: data.agent_response }]);
            setInlineQuiz(null);
            setAnswers([]);
        } catch (e) {
            setHistory(prev => [...prev, { role: 'agent', content: 'Erreur lors de la soumission des réponses.' }]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        bottomRef.current?.scrollIntoView({ behavior: 'smooth' });
    }, [history, isLoading]);

    return (
        <div className="flex flex-col h-screen w-screen bg-gray-900 text-white">
            <header className="p-4 bg-gray-800 shadow text-3xl font-bold flex items-center gap-2 w-full">
                <span role="img" aria-label="brain">🧠</span> Consultant Coach
            </header>

            <div className="flex-1 overflow-y-auto p-4 flex flex-col w-full">
                {history.map((entry, idx) => (
                    <div
                        key={idx}
                        className={`my-2 p-3 rounded-lg max-w-[80%] ${
                            entry.role === 'user'
                                ? 'bg-blue-500 text-white self-end text-right'
                                : 'bg-gray-700 text-white self-start text-left'
                        }`}
                    >
                        <span className="block text-sm mb-1 font-semibold">
                            {entry.role === 'user' ? '🗣️ Vous :' : '🤖 Agent :'}
                        </span>
                        {entry.content}
                    </div>
                ))}

                {inlineQuiz && (
                    <div className="bg-gray-800 p-4 rounded-lg mt-4">
                        <h3 className="text-xl font-semibold mb-2">📝 Quiz PRINCE2</h3>
                        {inlineQuiz.map((q, i) => (
                            <div key={i} className="mb-4">
                                <p className="font-medium mb-1">{q.question}</p>
                                {q.answers.map((ans, j) => (
                                    <div key={j} className="flex items-center gap-2">
                                        <input
                                            type="radio"
                                            name={`q${i}`}
                                            value={ans}
                                            onChange={() => handleAnswerChange(i, ans)}
                                            checked={answers[i] === ans}
                                        />
                                        <label>{ans}</label>
                                    </div>
                                ))}
                            </div>
                        ))}
                        <button
                            onClick={handleQuizSubmit}
                            className="bg-green-600 text-white px-4 py-2 rounded hover:bg-green-700"
                        >
                            Soumettre le quiz
                        </button>
                    </div>
                )}

                {isLoading && (
                    <div className="my-2 p-3 rounded-lg max-w-[80%] bg-gray-700 text-white self-start text-left animate-pulse">
                        <span className="block text-sm mb-1 font-semibold">🤖 Agent :</span>
                        L'agent réfléchit...
                    </div>
                )}
                <div ref={bottomRef} />
            </div>

            <form onSubmit={handleSubmit} className="p-4 bg-gray-800 flex gap-2 w-full">
                <input
                    type="text"
                    className="flex-1 border rounded-lg p-3 text-black focus:outline-none focus:ring-2 focus:ring-blue-500"
                    placeholder="Entrez votre message..."
                    value={message}
                    onChange={(e) => setMessage(e.target.value)}
                />
                <button
                    type="submit"
                    className="bg-blue-600 text-white px-5 py-3 rounded-lg hover:bg-blue-700 transition-colors"
                    disabled={isLoading}
                >
                    {isLoading ? 'En cours...' : 'Envoyer'}
                </button>
            </form>
        </div>
    );
};

export default ChatInterface;