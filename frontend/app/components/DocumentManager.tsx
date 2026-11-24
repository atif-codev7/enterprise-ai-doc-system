"use client";

import React, { useState, useEffect } from "react";
import { UploadCloud, FileText, Trash2, RefreshCw, Plus } from "lucide-react";

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
      setStatusMsg(`Indexed ${data.chunk_count} chunks into pgvector HNSW`);
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
      <div className="lg:col-span-1 bg-[#10121a] p-5 rounded-lg border border-white/[0.08] space-y-4">
        <div className="flex items-center gap-2 text-[#eef1f6] font-medium text-xs">
          <UploadCloud className="h-4 w-4 text-[#646c80]" />
          <span>Ingest document</span>
        </div>

        <form onSubmit={handleUpload} className="space-y-3 text-xs">
          <div>
            <label className="text-[#646c80] block mb-1">Document title</label>
            <input
              type="text"
              placeholder="e.g. PayGuard Architecture SLA"
              value={title}
              onChange={(e) => setTitle(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d0f14] border border-white/[0.08] rounded-md text-[#eef1f6] placeholder-[#646c80] focus:outline-none focus:border-white/[0.2] transition-colors"
            />
          </div>

          <div>
            <label className="text-[#646c80] block mb-1">Document format</label>
            <select
              value={format}
              onChange={(e) => setFormat(e.target.value)}
              className="w-full px-3 py-2 bg-[#0d0f14] border border-white/[0.08] rounded-md text-[#eef1f6] focus:outline-none focus:border-white/[0.2] transition-colors"
            >
              <option value="markdown">Markdown (.md)</option>
              <option value="pdf">PDF (.pdf)</option>
              <option value="html">HTML (.html)</option>
              <option value="txt">Plaintext (.txt)</option>
            </select>
          </div>

          <div>
            <label className="text-[#646c80] block mb-1">Source file</label>
            <input
              type="file"
              onChange={(e) => setFile(e.target.files?.[0] || null)}
              className="w-full text-[#9aa2b4] text-xs file:mr-2.5 file:py-1 file:px-2.5 file:rounded file:border-0 file:text-xs file:font-medium file:bg-[#1a1e2a] file:text-[#eef1f6] hover:file:bg-white/[0.1] transition-colors"
            />
          </div>

          <div className="relative flex py-1 items-center">
            <div className="flex-grow border-t border-white/[0.06]"></div>
            <span className="flex-shrink mx-2 text-[10px] text-[#646c80] uppercase tracking-wide">Or paste content</span>
            <div className="flex-grow border-t border-white/[0.06]"></div>
          </div>

          <div>
            <textarea
              rows={4}
              placeholder="# Paste Markdown, architecture specifications, or policies..."
              value={rawText}
              onChange={(e) => setRawText(e.target.value)}
              className="w-full p-2.5 bg-[#0d0f14] border border-white/[0.08] rounded-md text-[#eef1f6] placeholder-[#646c80] focus:outline-none focus:border-white/[0.2] font-mono text-[11px] transition-colors"
            />
          </div>

          <button
            type="submit"
            disabled={uploading || (!file && !rawText.trim())}
            className="w-full py-2 rounded-md bg-[#eef1f6] hover:bg-white disabled:opacity-40 text-[#0d0f14] font-medium text-xs flex items-center justify-center gap-1.5 transition-colors"
          >
            {uploading ? (
              <>
                <RefreshCw className="h-3.5 w-3.5 animate-spin" />
                <span>Chunking & indexing...</span>
              </>
            ) : (
              <>
                <Plus className="h-3.5 w-3.5" />
                <span>Recursive chunk & index</span>
              </>
            )}
          </button>

          {statusMsg && (
            <p className="text-[11px] text-[#9aa2b4] bg-white/[0.04] p-2 rounded border border-white/[0.06] font-mono">
              {statusMsg}
            </p>
          )}
        </form>
      </div>

      {/* Corpus Overview & Document List */}
      <div className="lg:col-span-2 bg-[#10121a] p-5 rounded-lg border border-white/[0.08] space-y-4">
        <div className="flex items-center justify-between">
          <div className="text-[#eef1f6] font-medium text-xs flex items-center gap-2">
            <FileText className="h-4 w-4 text-[#646c80]" />
            <span>Document corpus &middot; {documents.length} files ({totalChunks} chunks)</span>
          </div>

          <button
            onClick={loadDocs}
            disabled={loading}
            className="p-1 rounded text-[#646c80] hover:text-[#eef1f6] hover:bg-white/[0.05] transition-colors"
            title="Refresh document list"
          >
            <RefreshCw className={`h-3.5 w-3.5 ${loading ? "animate-spin" : ""}`} />
          </button>
        </div>

        <div className="divide-y divide-white/[0.06] border border-white/[0.06] rounded-md overflow-hidden bg-[#0d0f14]">
          {documents.length === 0 ? (
            <div className="p-8 text-center text-xs text-[#646c80]">
              No documents indexed. Ingest specifications or text above.
            </div>
          ) : (
            documents.map((doc, idx) => (
              <div key={idx} className="p-3.5 flex items-center justify-between text-xs hover:bg-white/[0.02] transition-colors">
                <div className="flex items-center gap-3 truncate">
                  <div className="h-7 w-7 rounded bg-[#161922] border border-white/[0.08] flex items-center justify-center text-[#646c80] shrink-0">
                    <FileText className="h-3.5 w-3.5" />
                  </div>
                  <div className="truncate">
                    <h4 className="font-medium text-[#eef1f6] truncate">{doc.title}</h4>
                    <div className="flex items-center gap-2 text-[11px] text-[#646c80] font-mono mt-0.5 tabular-nums">
                      <span className="uppercase text-[10px] px-1 py-0.2 rounded bg-white/[0.05] text-[#9aa2b4]">
                        {doc.format}
                      </span>
                      <span>{doc.chunk_count} chunks</span>
                      <span>&bull;</span>
                      <span>~{doc.total_tokens} tokens</span>
                    </div>
                  </div>
                </div>

                <button
                  onClick={() => handleDelete(doc.document_id)}
                  className="p-1 rounded text-[#646c80] hover:text-red-400 hover:bg-white/[0.05] transition-colors ml-2 shrink-0"
                  title="Delete document"
                >
                  <Trash2 className="h-3.5 w-3.5" />
                </button>
              </div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
