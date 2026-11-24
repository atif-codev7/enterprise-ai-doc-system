import type { Metadata } from "next";
import "./globals.css";
import Header from "./components/Header";

export const metadata: Metadata = {
  title: "Enterprise AI Document Intelligence System",
  description: "pgvector HNSW Semantic Search, LangGraph Workflows & Ragas Quantitative Evaluation",
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className="dark">
      <body className="bg-slate-950 text-slate-100 min-h-screen flex flex-col antialiased">
        <Header />
        <main className="flex-1 max-w-7xl w-full mx-auto p-6">{children}</main>
      </body>
    </html>
  );
}
