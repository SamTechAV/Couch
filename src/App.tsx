import { useState } from 'react';
import { invoke } from '@tauri-apps/api/core';
import CrunchyrollViewer from './CrunchyrollViewer';
import CrunchyrollBrowser from './CrunchyrollBrowser';
import './App.css';

function App() {
    const [currentView, setCurrentView] = useState<'home' | 'crunchyroll' | 'browser'>('home');
    const [name, setName] = useState('');
    const [greeting, setGreeting] = useState('');
    const [isLoading, setIsLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    async function handleGreet() {
        if (!name.trim()) {
            setError('Please enter a name');
            return;
        }

        setIsLoading(true);
        setError(null);

        try {
            const response = await invoke<string>('greet', { name });
            setGreeting(response);
        } catch (err) {
            setError(`Failed to greet: ${err instanceof Error ? err.message : String(err)}`);
        } finally {
            setIsLoading(false);
        }
    }

    // Embedded Crunchyroll Browser View
    if (currentView === 'browser') {
        return (
            <div className="app-container">
                <nav className="app-nav">
                    <button onClick={() => setCurrentView('home')} className="nav-btn">
                        ← Back to Home
                    </button>
                    <h2 style={{ margin: 0, color: 'white' }}>Crunchyroll Browser</h2>
                </nav>
                <CrunchyrollBrowser />
            </div>
        );
    }

    // Crunchyroll Viewer (External Links)
    if (currentView === 'crunchyroll') {
        return (
            <div className="app-container">
                <nav className="app-nav">
                    <button onClick={() => setCurrentView('home')} className="nav-btn">
                        ← Back to Home
                    </button>
                    <h2 style={{ margin: 0, color: 'white' }}>Crunchyroll Viewer</h2>
                </nav>
                <CrunchyrollViewer />
            </div>
        );
    }

    // Home Screen
    return (
        <div className="container">
            <header className="app-header">
                <h1>🛋️ Welcome to Couch</h1>
                <p className="app-subtitle">Your Ultimate Entertainment Hub</p>
                <div className="app-description">
                    <p>Stream anime, browse content, and enjoy your favorite shows with a dedicated desktop experience.</p>
                </div>
            </header>

            <main className="feature-grid">
                {/* Embedded Browser Card */}
                <div className="feature-card featured">
                    <div className="feature-icon">🌐</div>
                    <h3>Crunchyroll Browser</h3>
                    <p>Full Crunchyroll website embedded directly in the app. Login, stream, and browse without leaving Couch.</p>
                    <ul className="feature-list">
                        <li>✅ Full website functionality</li>
                        <li>✅ Login & streaming</li>
                        <li>✅ Browser controls</li>
                        <li>✅ Fullscreen viewing</li>
                    </ul>
                    <button
                        className="feature-btn primary"
                        onClick={() => setCurrentView('browser')}
                    >
                        🚀 Launch Browser
                    </button>
                </div>

                {/* Anime Viewer Card */}
                <div className="feature-card">
                    <div className="feature-icon">🍊</div>
                    <h3>Anime Gallery</h3>
                    <p>Browse popular anime and quickly open them on Crunchyroll. Perfect for discovering new shows.</p>
                    <ul className="feature-list">
                        <li>✅ Popular anime showcase</li>
                        <li>✅ Category filtering</li>
                        <li>✅ Quick search</li>
                        <li>✅ External link opening</li>
                    </ul>
                    <button
                        className="feature-btn secondary"
                        onClick={() => setCurrentView('crunchyroll')}
                    >
                        📺 Browse Anime
                    </button>
                </div>

                {/* Demo Card */}
                <div className="feature-card demo">
                    <div className="feature-icon">👋</div>
                    <h3>System Demo</h3>
                    <p>Test the Rust ↔ React communication system that powers this application.</p>

                    <div className="greet-section">
                        <div className="input-group">
                            <input
                                type="text"
                                value={name}
                                onChange={(e) => {
                                    setName(e.target.value);
                                    setError(null);
                                }}
                                placeholder="Enter your name..."
                                disabled={isLoading}
                                onKeyDown={(e) => e.key === 'Enter' && handleGreet()}
                                className="demo-input"
                            />
                            <button
                                onClick={handleGreet}
                                disabled={isLoading || !name.trim()}
                                className="demo-btn"
                            >
                                {isLoading ? '⏳ Processing...' : '🤝 Greet'}
                            </button>
                        </div>

                        {greeting && (
                            <div className="greeting-message">
                                <div className="message-icon">✨</div>
                                <p>{greeting}</p>
                            </div>
                        )}

                        {error && (
                            <div className="error-message">
                                <div className="message-icon">⚠️</div>
                                <p>{error}</p>
                            </div>
                        )}
                    </div>
                </div>
            </main>

            <footer className="app-footer">
                <div className="tech-stack">
                    <h4>🚀 Powered by Modern Technology</h4>
                    <div className="tech-badges">
                        <span className="tech-badge rust">🦀 Rust</span>
                        <span className="tech-badge react">⚛️ React 18</span>
                        <span className="tech-badge tauri">🔧 Tauri v2</span>
                        <span className="tech-badge typescript">📘 TypeScript</span>
                    </div>
                </div>

                <div className="app-info">
                    <p>✨ Desktop app with web technologies and native performance</p>
                    <p>🌐 Embedded web browsing capabilities with full site support</p>
                    <p>🔒 Secure, fast, and lightweight compared to traditional solutions</p>
                </div>
            </footer>
        </div>
    );
}

export default App;