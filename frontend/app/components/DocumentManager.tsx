"use client";

import React, { useState, useEffect } from "react";
import { UploadCloud, FileText, Trash2, CheckCircle2, RefreshCw, FileCode, PlusCircle } from "lucide-react";

export default function DocumentManager() {
  const [documents, setDocuments] = useState<any[]>([]);
  const [totalChunks, setTotalChunks] = useState(0);
  const [loading, setLoading] = useState(false);
  const [uploading, setUploading] = useState(false);
  const [title, setTitle] = useState("");
  const [rawText, setRawText] = useState("");
  const [format, setFormat] = useState("markdown");
  const [file, setFile] = useState<File | null>(null);
  const [statusMsg, setStatusMsg] = useState("");

  const loadDocs = async () => {
    setLoading(true);
    try {
      const res = await fetch("/api/documents");
      const data = await res.json();
      setDocuments(data.documents || []);
      setTotalChunks(data.total_indexed_chunks || 0);
    } catch (err) {
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    loadDocs();
  }, []);

  const handleUpload = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!file && !rawText.trim()) return;

    setUploading(true);
    setStatusMsg("");
    try {
      const formData = new FormData();
      if (title.trim()) formData.append("title", title.trim());
      formData.append("doc_format", format);

      if (file) {
        formData.append("file", file);
      } else {
        formData.append("raw_text", rawText);
      }

      const res = await fetch("/api/documents/upload", {
        method: "POST",
        body: formData,
      });

      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "Upload failed");
      }

      const data = await res.json();
      setStatusMsg(`Successfully indexed ${data.chunk_count} chunks into pgvector HNSW.`);
      setTitle("");
      setRawText("");
      setFile(null);
      loadDocs();
    } catch (err: any) {
      setStatusMsg(`Error: ${err.message}`);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId: string) => {
    try {
      await fetch(`/api/documents/${docId}`, { method: "DELETE" });
      loadDocs();
    } catch (err) {
      console.error(err);
    }
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
      {/* Upload Form */}
      <div className="lg:col-span-1 bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center gap-2 text-white font-semibold text-sm">
          <UploadCloud className="h-4 w-4 text-indigo-400" />
          <span>Ingest Multi-Format Document</span>
        </div>

        <form onSubmit={handleUpload} className="space-y-3 text-xs">
          <div>
            <label className="text-slate-400 block mb-1">Document Title (Optional)</label>
            <input
              type="text"
              placeholder="e.g. PayGuard Architecture SLA"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-indigo-500"
            />
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Document Format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-3 py-2 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-indigo-500"
            >
              <option value="markdown">Markdown (.md)</option>
              <option value="pdf">PDF (.pdf)</option>
              <option value="html">HTML (.html)</option>
              <option value="txt">Plaintext (.txt)</option>
            </select>
          </div>

          <div>
            <label className="text-slate-400 block mb-1">Upload File (PDF / Markdown / TXT)</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full text-slate-400 file:mr-3 file:py-1.5 file:px-3 file:rounded-md file:border-0 file:text-xs file:font-medium file:bg-indigo-600 file:text-white hover:file:bg-indigo-500"
            />
          </div>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-slate-800"></div>
            <span className="flex-shrink mx-2 text-[10px] text-slate-500 uppercase">Or Paste Raw Content</span>
            <div className="flex-grow border-t border-slate-800"></div>
          </div>

          <div>
            <textarea
              rows={4}
              placeholder="# Paste Markdown, architecture specifications, or policies..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-2.5 bg-slate-950 border border-slate-800 rounded-lg text-slate-200 focus:outline-none focus:border-indigo-500 font-mono text-[11px]"
            />
          </div>

          <button
            type="submit"
            disabled={uploading || (!file && !rawText.trim())}
            className="w-full py-2.5 rounded-lg bg-indigo-600 hover:bg-indigo-500 disabled:opacity-50 text-white font-medium flex items-center justify-center gap-2 shadow-lg shadow-indigo-600/20 transition"
          >
            {uploading ? (
              <>
                <RefreshCw className="h-4 w-4 animate-spin" />
                <span>Chunking & Indexing...</span>
              </>
            ) : (
              <>
                <PlusCircle className="h-4 w-4" />
                <span>Recursive Chunk & Index</span>
              </>
            )}
          </button>

          {statusMsg && (
            <p className="text-[11px] text-emerald-400 bg-emerald-500/10 p-2 rounded border border-emerald-500/20">
              {statusMsg}
            </p>
          )}
        </form>
      </div>

      {/* Corpus Overview & Document List */}
      <div className="lg:col-span-2 bg-slate-900/60 p-5 rounded-xl border border-slate-800 space-y-4">
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-2 text-white font-semibold text-sm">
            <FileCode className="h-4 w-4 text-cyan-400" />
            <span>Indexed Document Corpus ({documents.length} Docs &bull; {totalChunks} Chunks)</span>
          </div>

          <button
            onClick={loadDocs}
            disabled={loading}
            className="p-1.5 rounded-lg hover:bg-slate-800 text-slate-400 hover:text-white transition"
          >
            <RefreshCw className={`h-4 w-4 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        <div className="divide-y divide-slate-800 border border-slate-800/80 rounded-lg overflow-hidden bg-slate-950/70">
          {documents.length === 0 ? (
            <div className="p-8 text-center text-xs text-slate-500">
              No custom documents ingested yet. Upload files or specs to populate the HNSW vector store.
            </div>
          ) : (
            documents.map((doc, idx) => (
              <div key={idx} className="p-3.5 flex items-center justify-between text-xs hover:bg-slate-900/40 transition">
                <div className="flex items-center gap-3">
                  <div className="h-8 w-8 rounded bg-slate-900 border border-slate-800 flex items-center justify-center text-indigo-400 shrink-0">
                    <FileText className="h-4 w-4" />
                  </div>
                  <div>
                    <h4 className="font-medium text-slate-200">{doc.title}</h4>
                    <div className="flex items-center gap-2 text-[10px] text-slate-400 font-mono mt-0.5">
                      <span className="uppercase px-1.5 py-0.2 rounded bg-slate-800 text-slate-300">
                        {doc.format}
                      </span>
                      <span>{doc.chunk_count} HNSW chunks</span>
                      <span>&bull;</span>
                      <span>~{doc.total_tokens} tokens</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="p-1.5 rounded text-slate-500 hover:text-red-400 hover:bg-red-500/10 transition"
                  title="Delete Document"
                >
                  <Trash2 className="h-4 w-4" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
