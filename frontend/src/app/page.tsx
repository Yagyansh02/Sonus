"use client";

import { useState } from "react";

export default function Home() {
  const [activeTab, setActiveTab] = useState("health");
  const [loading, setLoading] = useState(false);
  const [response, setResponse] = useState<any>(null);
  const [error, setError] = useState<string | null>(null);

  // Form states
  const [songId, setSongId] = useState("");
  const [youtubeUrl, setYoutubeUrl] = useState("");
  const [question, setQuestion] = useState("");
  const [targetLanguage, setTargetLanguage] = useState("");

  const baseUrl = "http://localhost:8000/api";

  const handleRequest = async (endpoint: string, method: string = "GET", body?: any) => {
    setLoading(true);
    setError(null);
    setResponse(null);

    try {
      const res = await fetch(`${baseUrl}${endpoint}`, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      const data = await res.json();
      setResponse({ status: res.status, data });
    } catch (err: any) {
      setError(err.message || "Failed to make request. Check if backend is running.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50 text-gray-900 font-sans">
      <div className="max-w-4xl mx-auto bg-white p-6 rounded-xl shadow-sm">
        <h1 className="text-3xl font-bold mb-6 text-center">Sonus API Tester</h1>

        <div className="flex flex-wrap gap-2 mb-8 border-b pb-4">
          <button onClick={() => setActiveTab("health")} className={`px-4 py-2 rounded-md ${activeTab === "health" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Health</button>
          <button onClick={() => setActiveTab("ingest")} className={`px-4 py-2 rounded-md ${activeTab === "ingest" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Ingest Song</button>
          <button onClick={() => setActiveTab("rag")} className={`px-4 py-2 rounded-md ${activeTab === "rag" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>RAG Ask</button>
          <button onClick={() => setActiveTab("transcript")} className={`px-4 py-2 rounded-md ${activeTab === "transcript" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Transcript</button>
          <button onClick={() => setActiveTab("translate")} className={`px-4 py-2 rounded-md ${activeTab === "translate" ? "bg-blue-600 text-white" : "bg-gray-200"}`}>Translate</button>
        </div>

        <div className="mb-8 p-4 border rounded-lg bg-gray-50">
          {activeTab === "health" && (
            <div>
              <h2 className="text-xl font-semibold mb-4">GET /health</h2>
              <button 
                onClick={() => handleRequest("/health")}
                className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
              >
                Check Health
              </button>
            </div>
          )}

          {activeTab === "ingest" && (
            <div>
              <h2 className="text-xl font-semibold mb-4">POST /api/song/ingest</h2>
              <div className="flex flex-col gap-4 max-w-md">
                <input 
                  type="text" 
                  placeholder="YouTube URL" 
                  className="border p-2 rounded text-black"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                />
                <button 
                  onClick={() => handleRequest("/song/ingest", "POST", { youtube_url: youtubeUrl })}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Ingest Song
                </button>
              </div>
            </div>
          )}

          {activeTab === "rag" && (
            <div>
              <h2 className="text-xl font-semibold mb-4">POST /api/rag/ask</h2>
              <div className="flex flex-col gap-4 max-w-md">
                <input 
                  type="text" 
                  placeholder="Song ID" 
                  className="border p-2 rounded text-black"
                  value={songId}
                  onChange={(e) => setSongId(e.target.value)}
                />
                <input 
                  type="text" 
                  placeholder="Question" 
                  className="border p-2 rounded text-black"
                  value={question}
                  onChange={(e) => setQuestion(e.target.value)}
                />
                <button 
                  onClick={() => handleRequest("/rag/ask", "POST", { song_id: songId, question, session_id: "test-session" })}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Ask Question
                </button>
              </div>
            </div>
          )}

          {activeTab === "transcript" && (
            <div>
              <h2 className="text-xl font-semibold mb-4">GET /api/song/{"{song_id}"}/transcript</h2>
              <div className="flex flex-col gap-4 max-w-md">
                <input 
                  type="text" 
                  placeholder="Song ID" 
                  className="border p-2 rounded text-black"
                  value={songId}
                  onChange={(e) => setSongId(e.target.value)}
                />
                <button 
                  onClick={() => handleRequest(`/song/${songId}/transcript`)}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Get Transcript
                </button>
              </div>
            </div>
          )}

          {activeTab === "translate" && (
            <div>
              <h2 className="text-xl font-semibold mb-4">POST /api/translate</h2>
              <div className="flex flex-col gap-4 max-w-md">
                <input 
                  type="text" 
                  placeholder="Song ID (optional if URL provided)" 
                  className="border p-2 rounded text-black"
                  value={songId}
                  onChange={(e) => setSongId(e.target.value)}
                />
                <input 
                  type="text" 
                  placeholder="YouTube URL (optional if ID provided)" 
                  className="border p-2 rounded text-black"
                  value={youtubeUrl}
                  onChange={(e) => setYoutubeUrl(e.target.value)}
                />
                <input 
                  type="text" 
                  placeholder="Target Language (e.g., 'es', 'fr', 'es-MX')" 
                  className="border p-2 rounded text-black"
                  value={targetLanguage}
                  onChange={(e) => setTargetLanguage(e.target.value)}
                />
                <button 
                  onClick={() => handleRequest("/translate", "POST", { song_id: songId || undefined, youtube_url: youtubeUrl || undefined, target_language: targetLanguage })}
                  className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700"
                >
                  Translate
                </button>

                <hr className="my-4" />
                <h3 className="text-lg font-semibold">GET /api/song/{"{song_id}"}/translations</h3>
                <button 
                  onClick={() => handleRequest(`/song/${songId}/translations`)}
                  className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700"
                >
                  List Translations
                </button>
              </div>
            </div>
          )}
        </div>

        <div className="bg-gray-800 text-green-400 p-4 rounded-lg overflow-auto max-h-96 min-h-[200px] shadow-inner font-mono text-sm relative">
          {loading && <div className="animate-pulse text-yellow-400">Loading...</div>}
          {error && <div className="text-red-400">Error: {error}</div>}
          {response && (
            <div>
              <div className="text-gray-400 mb-2">Status: {response.status}</div>
              <pre className="whitespace-pre-wrap">{JSON.stringify(response.data, null, 2)}</pre>
            </div>
          )}
          {!loading && !error && !response && (
            <div className="text-gray-500">Responses will appear here...</div>
          )}
        </div>
      </div>
    </div>
  );
}
