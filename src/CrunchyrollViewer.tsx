import { useState, useEffect } from 'react';
import { invoke } from '@tauri-apps/api/core';
import './CrunchyrollBrowser.css';

const CrunchyrollBrowser = () => {
    const [currentUrl, setCurrentUrl] = useState('https://www.crunchyroll.com');
    const [isLoading, setIsLoading] = useState(true);
    const [webviewId, setWebviewId] = useState<string | null>(null);
    const [error, setError] = useState<string | null>(null);

    const quickLinks = [
        { name: 'Home', url: 'https://www.crunchyroll.com' },
        { name: 'Browse', url: 'https://www.crunchyroll.com/videos/anime' },
        { name: 'Popular', url: 'https://www.crunchyroll.com/videos/anime/popular' },
        { name: 'Simulcasts', url: 'https://www.crunchyroll.com/simulcasts' },
        { name: 'My List', url: 'https://www.crunchyroll.com/watchlist' },
    ];

    useEffect(() => {
        createCrunchyrollWebview();
        return () => {
            // Cleanup webview when component unmounts
            if (webviewId) {
                invoke('destroy_webview', { webviewId }).catch(console.error);
            }
        };
    }, []);

    const createCrunchyrollWebview = async () => {
        try {
            setIsLoading(true);
            setError(null);

            const id = await invoke<string>('create_crunchyroll_webview', {
                url: currentUrl,
                x: 0,
                y: 80, // Leave space for our controls
                width: window.innerWidth,
                height: window.innerHeight - 80
            });

            setWebviewId(id);
            setIsLoading(false);
        } catch (err) {
            setError(`Failed to create webview: ${err}`);
            setIsLoading(false);
        }
    };

    const navigateTo = async (url: string) => {
        if (!webviewId) return;

        try {
            setIsLoading(true);
            setCurrentUrl(url);
            await invoke('webview_navigate', { webviewId, url });
            setIsLoading(false);
        } catch (err) {
            setError(`Navigation failed: ${err}`);
            setIsLoading(false);
        }
    };

    const refreshWebview = async () => {
        if (!webviewId) return;

        try {
            setIsLoading(true);
            await invoke('webview_reload', { webviewId });
            setIsLoading(false);
        } catch (err) {
            setError(`Refresh failed: ${err}`);
            setIsLoading(false);
        }
    };

    const goBack = async () => {
        if (!webviewId) return;

        try {
            await invoke('webview_go_back', { webviewId });
        } catch (err) {
            console.error('Go back failed:', err);
        }
    };

    const goForward = async () => {
        if (!webviewId) return;

        try {
            await invoke('webview_go_forward', { webviewId });
        } catch (err) {
            console.error('Go forward failed:', err);
        }
    };

    const toggleFullscreen = async () => {
        try {
            await invoke('toggle_webview_fullscreen', { webviewId });
        } catch (err) {
            console.error('Fullscreen toggle failed:', err);
        }
    };

    return (
        <div className="crunchyroll-browser">
            <div className="browser-controls">
                <div className="nav-controls">
                    <button onClick={goBack} className="nav-btn" title="Go Back">
                        ←
                    </button>
                    <button onClick={goForward} className="nav-btn" title="Go Forward">
                        →
                    </button>
                    <button onClick={refreshWebview} className="nav-btn" title="Refresh">
                        ⟳
                    </button>
                </div>

                <div className="url-bar">
                    <span className="current-url">{currentUrl}</span>
                    <button onClick={toggleFullscreen} className="fullscreen-btn" title="Toggle Fullscreen">
                        ⛶
                    </button>
                </div>

                <div className="quick-links">
                    {quickLinks.map((link, index) => (
                        <button
                            key={index}
                            onClick={() => navigateTo(link.url)}
                            className={`quick-link ${currentUrl === link.url ? 'active' : ''}`}
                        >
                            {link.name}
                        </button>
                    ))}
                </div>
            </div>

            {isLoading && (
                <div className="loading-overlay">
                    <div className="loading-spinner"></div>
                    <p>Loading Crunchyroll...</p>
                </div>
            )}

            {error && (
                <div className="error-overlay">
                    <div className="error-message">
                        <h3>Connection Error</h3>
                        <p>{error}</p>
                        <button onClick={createCrunchyrollWebview} className="retry-btn">
                            Retry
                        </button>
                    </div>
                </div>
            )}

            <div className="webview-container" id="crunchyroll-webview">
                {/* The webview will be created here by Tauri */}
            </div>
        </div>
    );
};

export default CrunchyrollBrowser;