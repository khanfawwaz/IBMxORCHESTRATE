import React, { useState, useRef, useEffect } from 'react';
import {
    Send,
    Bot,
    Sparkles,
    TrendingUp,
    Truck,
    AlertTriangle,
    Leaf,
    Lightbulb,
    BarChart3,
    User,
    Package,
    Activity
} from 'lucide-react';
import './App.css';

// API Configuration
const API_CONFIG = {
    BASE_URL: '',
    ENDPOINTS: {
        CHAT: '/api/v1/chat'
    }
};

function App() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            type: 'bot',
            isWelcome: true
        }
    ]);
    const [inputValue, setInputValue] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const messagesEndRef = useRef(null);

    const scrollToBottom = () => {
        messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
    };

    useEffect(() => {
        scrollToBottom();
    }, [messages, isLoading]);

    const handleSendMessage = async (text) => {
        const messageText = text || inputValue.trim();
        if (!messageText) return;

        // Add user message
        const userMsgId = Date.now();
        setMessages(prev => [...prev, {
            id: userMsgId,
            type: 'user',
            content: messageText
        }]);

        setInputValue('');
        setIsLoading(true);

        try {
            const response = await fetch(`${API_CONFIG.BASE_URL}${API_CONFIG.ENDPOINTS.CHAT}`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ message: messageText })
            });

            if (!response.ok) throw new Error('Analysis failed');

            const data = await response.json();

            // Handle Guardrails
            if (!data.is_relevant) {
                setMessages(prev => [...prev, {
                    id: Date.now(),
                    type: 'bot',
                    isGuardrail: true,
                    content: data.response_message
                }]);
                setIsLoading(false);
                return;
            }

            // Handle Success Response
            setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'bot',
                isAnalysis: true,
                data: data
            }]);

        } catch (error) {
            setMessages(prev => [...prev, {
                id: Date.now(),
                type: 'bot',
                isError: true,
                content: "Connection Error: Make sure the backend is running and accessible."
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    const handleKeyPress = (e) => {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            handleSendMessage();
        }
    };

    const WelcomeMessage = () => (
        <div className="welcome-card">
            <div className="welcome-title">
                <Sparkles size={28} />
                <span>Welcome to your AI Warehouse Assistant!</span>
            </div>

            <p style={{ marginBottom: '1.5rem' }}>
                I'm powered by <strong>Gemini AI</strong> and can help you with:
            </p>

            <div className="feature-list">
                <div className="feature-item">
                    <TrendingUp size={20} style={{ color: '#60a5fa' }} />
                    <div>
                        <strong>Demand Forecasting</strong> - ML-powered predictions
                    </div>
                </div>
                <div className="feature-item">
                    <Truck size={20} style={{ color: '#34d399' }} />
                    <div>
                        <strong>Supply Chain Analysis</strong> - Real-time availability
                    </div>
                </div>
                <div className="feature-item">
                    <AlertTriangle size={20} style={{ color: '#fbbf24' }} />
                    <div>
                        <strong>Risk Assessment</strong> - Multi-factor analysis
                    </div>
                </div>
                <div className="feature-item">
                    <Leaf size={20} style={{ color: '#4ade80' }} />
                    <div>
                        <strong>Carbon Footprint</strong> - Sustainability tips
                    </div>
                </div>
                <div className="feature-item">
                    <Sparkles size={20} style={{ color: '#c084fc' }} />
                    <div>
                        <strong>AI Summaries</strong> - Executive insights
                    </div>
                </div>
            </div>

            <div className="example-prompts">
                <div className="example-prompts-title">💡 Try asking:</div>
                <div className="example-prompt" onClick={() => handleSendMessage('Analyze product WH-FP-0001 for New York')}>
                    "Analyze product WH-FP-0001 for New York"
                </div>
                <div className="example-prompt" onClick={() => handleSendMessage('Check supply availability for WH-DE-0075 in Los Angeles')}>
                    "Check supply availability for WH-DE-0075 in Los Angeles"
                </div>
                <div className="example-prompt" onClick={() => handleSendMessage('Assess inventory risk for WH-MS-0125 in Chicago')}>
                    "Assess inventory risk for WH-MS-0125 in Chicago"
                </div>
                <div className="example-prompt" onClick={() => handleSendMessage('Calculate carbon footprint for WH-FF-0230 in Houston')}>
                    "Calculate carbon footprint for WH-FF-0230 in Houston"
                </div>
            </div>

            <p style={{ marginTop: '1.5rem', fontSize: '0.875rem', color: 'var(--color-text-secondary)', fontStyle: 'italic' }}>
                Note: I only respond to warehouse and inventory-related queries.
            </p>
        </div>
    );

    const AnalysisContent = ({ data }) => {
        const { analysis_data, ai_summary, carbon_tips } = data;
        const { forecast, supply, risk, sustainability, recommendation, sku, location } = analysis_data;

        return (
            <div className="analysis-container">
                <div className="analysis-header">
                    <Package size={24} />
                    <span>Analysis Complete: {sku} - {location}</span>
                </div>

                {/* AI Summary */}
                {ai_summary && (
                    <div className="ai-summary-card">
                        <div className="ai-summary-header">
                            <Sparkles size={20} />
                            <span>AI Summary</span>
                        </div>
                        <div style={{ lineHeight: '1.8' }}>{ai_summary}</div>
                    </div>
                )}

                {/* Forecast Section */}
                <div className="section-card">
                    <div className="section-header">
                        <TrendingUp size={20} style={{ color: '#60a5fa' }} />
                        <span>Demand Forecast (30 days)</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-card">
                            <div className="metric-label">Predicted Demand</div>
                            <div className="metric-value">{Math.round(forecast.total_predicted_demand)} units</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Trend</div>
                            <div className="metric-value" style={{ textTransform: 'capitalize' }}>{forecast.trend}</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Confidence</div>
                            <div className="metric-value">{(forecast.confidence * 100).toFixed(0)}%</div>
                        </div>
                    </div>
                </div>

                {/* Supply Chain Section */}
                <div className="section-card">
                    <div className="section-header">
                        <Truck size={20} style={{ color: '#34d399' }} />
                        <span>Supply Chain</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-card">
                            <div className="metric-label">Supplier</div>
                            <div className="metric-value" style={{ fontSize: '1.125rem' }}>{supply.supplier}</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Lead Time</div>
                            <div className="metric-value">{supply.lead_time_days} days</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Current Stock</div>
                            <div className="metric-value">{supply.current_stock} units</div>
                        </div>
                    </div>
                </div>

                {/* Risk Section */}
                <div className="section-card">
                    <div className="section-header">
                        <AlertTriangle size={20} style={{ color: '#fbbf24' }} />
                        <span>Risk Assessment</span>
                    </div>
                    <div style={{
                        padding: 'var(--spacing-md)',
                        background: risk.risk_level === 'low' ? 'rgba(34, 197, 94, 0.1)' : 'rgba(239, 68, 68, 0.1)',
                        border: `1px solid ${risk.risk_level === 'low' ? 'rgba(34, 197, 94, 0.3)' : 'rgba(239, 68, 68, 0.3)'}`,
                        borderRadius: 'var(--radius-md)',
                        fontWeight: 700,
                        color: risk.risk_level === 'low' ? '#4ade80' : '#f87171'
                    }}>
                        {risk.risk_level.toUpperCase()} RISK (Score: {(risk.risk_score * 100).toFixed(0)}%)
                    </div>
                </div>

                {/* Sustainability Section */}
                <div className="section-card">
                    <div className="section-header">
                        <Leaf size={20} style={{ color: '#4ade80' }} />
                        <span>Sustainability Metrics</span>
                    </div>
                    <div className="metrics-grid">
                        <div className="metric-card">
                            <div className="metric-label">Carbon Footprint</div>
                            <div className="metric-value">{sustainability.carbon_footprint_kg} kg CO₂</div>
                        </div>
                        <div className="metric-card">
                            <div className="metric-label">Sustainability Score</div>
                            <div className="metric-value">{sustainability.sustainability_score}/100</div>
                        </div>
                    </div>
                </div>

                {/* Carbon Tips */}
                {carbon_tips && (
                    <div className="section-card" style={{
                        background: 'linear-gradient(135deg, rgba(74, 222, 128, 0.1) 0%, rgba(34, 197, 94, 0.1) 100%)',
                        border: '1px solid rgba(74, 222, 128, 0.2)'
                    }}>
                        <div className="section-header">
                            <Leaf size={20} style={{ color: '#4ade80' }} />
                            <span>Carbon Reduction Tips</span>
                        </div>
                        <div style={{ lineHeight: '1.8' }} dangerouslySetInnerHTML={{
                            __html: carbon_tips.replace(/\n/g, '<br/>').replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                        }} />
                    </div>
                )}

                {/* Recommendation */}
                <div className="recommendation-card">
                    <div className="recommendation-header">
                        <Lightbulb size={20} />
                        <span>Recommendation</span>
                    </div>
                    <div style={{ fontSize: '1.125rem', lineHeight: '1.8' }}>{recommendation}</div>
                </div>
            </div>
        );
    };

    return (
        <div className="app-container">
            {/* Header */}
            <header className="app-header">
                <div className="header-content">
                    <div className="header-left">
                        <div className="logo-container">
                            <Bot size={32} color="white" />
                        </div>
                        <div className="header-text">
                            <h1>Warehouse AI Assistant</h1>
                            <p>Powered by Gemini AI & IBM watsonx</p>
                        </div>
                    </div>
                    <div className="status-badge">
                        <div className="status-dot"></div>
                        <span>Online</span>
                    </div>
                </div>
            </header>

            {/* Chat Container */}
            <div className="chat-container">
                {/* Messages Area */}
                <div className="messages-area">
                    {messages.map((msg) => (
                        <div key={msg.id} className={`message ${msg.type}`}>
                            <div className="message-avatar">
                                {msg.type === 'bot' ? <Bot size={24} /> : <User size={24} />}
                            </div>
                            <div className="message-content">
                                {msg.isWelcome ? (
                                    <WelcomeMessage />
                                ) : msg.isGuardrail ? (
                                    <div className="error-message" style={{ padding: 'var(--spacing-lg)', borderRadius: 'var(--radius-md)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-sm)', fontWeight: 700 }}>
                                            <AlertTriangle size={20} />
                                            <span>Off-Topic Query Detected</span>
                                        </div>
                                        {msg.content}
                                    </div>
                                ) : msg.isAnalysis ? (
                                    <AnalysisContent data={msg.data} />
                                ) : msg.isError ? (
                                    <div className="error-message" style={{ padding: 'var(--spacing-lg)', borderRadius: 'var(--radius-md)' }}>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: 'var(--spacing-sm)', marginBottom: 'var(--spacing-sm)', fontWeight: 700 }}>
                                            <AlertTriangle size={20} />
                                            <span>Error</span>
                                        </div>
                                        {msg.content}
                                    </div>
                                ) : (
                                    msg.content
                                )}
                            </div>
                        </div>
                    ))}

                    {isLoading && (
                        <div className="message bot">
                            <div className="message-avatar">
                                <Bot size={24} />
                            </div>
                            <div className="typing-indicator">
                                <div className="typing-dots">
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                    <div className="typing-dot"></div>
                                </div>
                                <span style={{ color: 'var(--color-text-secondary)', fontSize: '0.875rem' }}>
                                    AI is analyzing...
                                </span>
                            </div>
                        </div>
                    )}
                    <div ref={messagesEndRef} />
                </div>

                {/* Input Section */}
                <div className="input-section">
                    <div className="quick-actions">
                        <button className="quick-action-btn" onClick={() => handleSendMessage('Analyze WH-FP-0001 in New York')}>
                            <BarChart3 size={16} />
                            <span>Analyze Product</span>
                        </button>
                        <button className="quick-action-btn" onClick={() => handleSendMessage('Show forecast for WH-PC-0455')}>
                            <TrendingUp size={16} />
                            <span>Get Forecast</span>
                        </button>
                        <button className="quick-action-btn" onClick={() => handleSendMessage('Check supply chain status')}>
                            <Truck size={16} />
                            <span>Supply Chain</span>
                        </button>
                        <button className="quick-action-btn" onClick={() => handleSendMessage('Carbon footprint analysis')}>
                            <Leaf size={16} />
                            <span>Sustainability</span>
                        </button>
                    </div>

                    <div className="input-wrapper">
                        <input
                            type="text"
                            className="chat-input"
                            placeholder="Ask about inventory, forecasts, supply chain..."
                            value={inputValue}
                            onChange={(e) => setInputValue(e.target.value)}
                            onKeyPress={handleKeyPress}
                            disabled={isLoading}
                        />
                        <button
                            className="send-button"
                            onClick={() => handleSendMessage()}
                            disabled={!inputValue.trim() || isLoading}
                        >
                            <Send size={20} />
                        </button>
                    </div>
                </div>
            </div>
        </div>
    );
}

export default App;
