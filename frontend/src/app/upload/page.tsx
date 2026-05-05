"use client";

import { useState } from "react";
import { Button } from "../components/ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/Card";

export default function UploadPage() {
    const [file, setFile] = useState<File | null>(null);
    const [loading, setLoading] = useState(false);
    const [response, setResponse] = useState<any>(null);
    const [error, setError] = useState<string | null>(null);

    const handleUpload = async () => {
        if (!file) return;

        setLoading(true);
        setError(null);
        setResponse(null);

        try {
            const formData = new FormData();
            formData.append("file", file);

            const res = await fetch(
                `${process.env.NEXT_PUBLIC_API_URL}/api/upload`,
                {
                    method: "POST",
                    body: formData,
                }
            );

            if (!res.ok) {
                throw new Error(`Upload failed: ${res.status}`);
            }

            const data = await res.json();
            setResponse(data);
        } catch (err: any) {
            setError(err.message);
        } finally {
            setLoading(false);
        }
    };

    return (
        <main className="mx-auto w-full max-w-[1200px] px-6 py-8">
            <header className="mb-6">
                <h1 className="text-2xl font-semibold text-[var(--text-primary)]">Upload</h1>
                <p className="mt-2 text-sm text-[var(--text-secondary)]">
                    Upload a research file to ingest into ChromaDB and the local NetworkX graph.
                    Supported: PDF, TXT, CSV.
                </p>
            </header>

            <Card>
                <CardHeader>
                    <div>
                        <CardTitle>File</CardTitle>
                        <CardDescription>Choose a single file and ingest it.</CardDescription>
                    </div>
                </CardHeader>
                <CardContent className="flex flex-col gap-4">
                    <input
                        type="file"
                        accept=".pdf,.txt,.csv"
                        onChange={(e) => setFile(e.target.files?.[0] || null)}
                        className="block w-full rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2 text-sm text-[var(--text-primary)] file:mr-3 file:rounded-md file:border-0 file:bg-[var(--surface)] file:px-3 file:py-2 file:text-sm file:font-semibold file:text-[var(--text-primary)]"
                    />

                    <div className="flex items-center gap-3">
                        <Button
                            onClick={handleUpload}
                            disabled={loading || !file}
                            variant="primary"
                            className="h-10"
                        >
                            {loading ? "Uploading..." : "Upload"}
                        </Button>
                        <div className="text-xs text-[var(--text-secondary)]">
                            {file ? file.name : "No file selected"}
                        </div>
                    </div>

                    {error && <div className="text-sm text-red-600">Error: {error}</div>}
                </CardContent>
            </Card>

            <div className="mt-6 grid gap-6 lg:grid-cols-2">
                <Card>
                    <CardHeader>
                        <div>
                            <CardTitle>Ingestion Pipeline</CardTitle>
                            <CardDescription>Transparency into what happens after upload.</CardDescription>
                        </div>
                    </CardHeader>
                    <CardContent>
                        <ol className="grid gap-2 text-sm">
                            {[
                                { id: "upload", label: "File received" },
                                { id: "extract", label: "Text extracted" },
                                { id: "chunk", label: "Chunked" },
                                { id: "vector", label: "Stored in ChromaDB" },
                                { id: "graph", label: "Graph updated (NetworkX)" },
                            ].map((step) => {
                                const done = Boolean(response) && !error;
                                const state = loading ? "running" : done ? "done" : "pending";
                                return (
                                    <li
                                        key={step.id}
                                        className="flex items-center justify-between rounded-lg border border-[var(--border)] bg-[var(--background)] px-3 py-2"
                                    >
                                        <span className="text-[var(--text-primary)]">{step.label}</span>
                                        <span className="text-xs font-semibold uppercase tracking-wide text-[var(--text-secondary)]">
                                            {state}
                                        </span>
                                    </li>
                                );
                            })}
                        </ol>
                    </CardContent>
                </Card>

                <Card>
                    <CardHeader>
                        <div>
                            <CardTitle>Ingestion Result</CardTitle>
                            <CardDescription>Raw backend response for debugging.</CardDescription>
                        </div>
                    </CardHeader>
                    <CardContent>
                        {!response ? (
                            <div className="text-sm text-[var(--text-secondary)]">
                                Upload a file to see ingestion stats.
                            </div>
                        ) : (
                            <pre className="max-h-[420px] overflow-auto rounded-lg border border-[var(--border)] bg-[var(--background)] p-3 text-xs leading-5 text-[var(--text-primary)]">
                                {JSON.stringify(response, null, 2)}
                            </pre>
                        )}
                    </CardContent>
                </Card>
            </div>
        </main>
    );
}
