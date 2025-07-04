// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

use tauri::{WebviewWindow, Manager, WebviewWindowBuilder, WebviewUrl, Url};
use log::{info, error};
use std::collections::HashMap;
use std::sync::Mutex;

// Global state to track webviews
type WebviewMap = Mutex<HashMap<String, WebviewWindow>>;

/// Greet command handler
#[tauri::command]
fn greet(name: &str) -> Result<String, String> {
    if name.is_empty() {
        return Err("Name cannot be empty".into());
    }

    info!("Received greet request for name: {}", name);
    Ok(format!("Hello, {}! Greetings from Rust", name))
}

/// Command to open URLs in the default browser
#[tauri::command]
async fn open_url(url: String, title: String) -> Result<(), String> {
    info!("Opening URL: {} ({})", url, title);

    match open::that(&url) {
        Ok(_) => {
            info!("Successfully opened URL: {}", url);
            Ok(())
        }
        Err(e) => {
            error!("Failed to open URL {}: {}", url, e);
            Err(format!("Failed to open URL: {}", e))
        }
    }
}

/// Create a dedicated webview for Crunchyroll
#[tauri::command]
async fn create_crunchyroll_webview(
    app: tauri::AppHandle,
    webviews: tauri::State<'_, WebviewMap>,
    url: String,
    x: i32,
    y: i32,
    width: u32,
    height: u32,
) -> Result<String, String> {
    let webview_id = format!("crunchyroll_{}", chrono::Utc::now().timestamp_millis());

    info!("Creating Crunchyroll webview: {} for URL: {}", webview_id, url);

    // Create a new webview window
    let webview = WebviewWindowBuilder::new(
        &app,
        &webview_id,
        WebviewUrl::External(url.parse().map_err(|e| format!("Invalid URL: {}", e))?),
    )
        .title("Crunchyroll")
        .inner_size(width as f64, height as f64)
        .position(x as f64, y as f64)
        .resizable(true)
        .decorations(false) // No window decorations for embedded feel
        .always_on_top(false)
        .visible(true)
        .user_agent("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36")
        .build()
        .map_err(|e| format!("Failed to create webview: {}", e))?;

    // Store the webview reference
    let mut webview_map = webviews.lock().unwrap();
    webview_map.insert(webview_id.clone(), webview);

    Ok(webview_id)
}

/// Navigate webview to a new URL
#[tauri::command]
async fn webview_navigate(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
    url: String,
) -> Result<(), String> {
    info!("Navigating webview {} to: {}", webview_id, url);

    let webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.get(&webview_id) {
        // Parse the URL string into a Url type
        let parsed_url = Url::parse(&url).map_err(|e| format!("Invalid URL: {}", e))?;
        webview.navigate(parsed_url).map_err(|e| format!("Failed to navigate: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Reload the current page in webview
#[tauri::command]
async fn webview_reload(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
) -> Result<(), String> {
    info!("Reloading webview: {}", webview_id);

    let webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.get(&webview_id) {
        // Navigate to current URL to reload
        let current_url = webview.url().map_err(|e| format!("Failed to get current URL: {}", e))?;
        webview.navigate(current_url).map_err(|e| format!("Failed to reload: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Go back in webview history
#[tauri::command]
async fn webview_go_back(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
) -> Result<(), String> {
    let webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.get(&webview_id) {
        // Tauri doesn't have direct back/forward, so we'll use JavaScript
        webview.eval("window.history.back()").map_err(|e| format!("Failed to go back: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Go forward in webview history
#[tauri::command]
async fn webview_go_forward(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
) -> Result<(), String> {
    let webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.get(&webview_id) {
        webview.eval("window.history.forward()").map_err(|e| format!("Failed to go forward: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Toggle fullscreen for webview
#[tauri::command]
async fn toggle_webview_fullscreen(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
) -> Result<(), String> {
    let webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.get(&webview_id) {
        let is_fullscreen = webview.is_fullscreen().map_err(|e| format!("Failed to check fullscreen: {}", e))?;
        webview.set_fullscreen(!is_fullscreen).map_err(|e| format!("Failed to toggle fullscreen: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Destroy a webview
#[tauri::command]
async fn destroy_webview(
    webviews: tauri::State<'_, WebviewMap>,
    webview_id: String,
) -> Result<(), String> {
    info!("Destroying webview: {}", webview_id);

    let mut webview_map = webviews.lock().unwrap();

    if let Some(webview) = webview_map.remove(&webview_id) {
        webview.close().map_err(|e| format!("Failed to close webview: {}", e))?;
        Ok(())
    } else {
        Err(format!("Webview {} not found", webview_id))
    }
}

/// Command to toggle developer tools
#[tauri::command]
async fn toggle_devtools(window: WebviewWindow) {
    #[cfg(debug_assertions)]
    {
        window.open_devtools();
    }
}

fn main() {
    // Initialize webview tracking
    let webview_map: WebviewMap = Mutex::new(HashMap::new());

    tauri::Builder::default()
        .manage(webview_map)
        .setup(|app| {
            // Configure logging only in debug mode
            #[cfg(debug_assertions)]
            {
                app.handle().plugin(
                    tauri_plugin_log::Builder::default()
                        .level(log::LevelFilter::Info)
                        .build()
                )?;
            }

            // Auto-open devtools in debug mode
            #[cfg(debug_assertions)]
            {
                if let Some(window) = app.get_webview_window("main") {
                    window.open_devtools();
                }
            }

            Ok(())
        })
        .invoke_handler(tauri::generate_handler![
            greet,
            toggle_devtools,
            open_url,
            create_crunchyroll_webview,
            webview_navigate,
            webview_reload,
            webview_go_back,
            webview_go_forward,
            toggle_webview_fullscreen,
            destroy_webview
        ])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}