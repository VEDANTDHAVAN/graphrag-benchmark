"use client";

import { useEffect, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";
import { Button } from "./ui/Button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "./ui/Card";

type GraphResponse = {
    status: string;
    nodes: any[];
    edges: any[];
    stats?: {
        total_nodes: number;
        total_edges: number;
        shown_nodes: number;
        shown_edges: number;
    };
};

export default function KnowledgeGraph() {
    const [elements, setElements] = useState<any[]>([]);
    const [stats, setStats] = useState<GraphResponse["stats"] | null>(null);
    const [loading, setLoading] = useState(false);

    const loadGraph = async () => {
        setLoading(true);

        try {
            const res = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/api/graph/view?limit=200`);
            const data: GraphResponse = await res.json();

            setElements([...data.nodes, ...data.edges]);
            setStats(data.stats || null);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        loadGraph();
    }, []);

    return (
        <Card className="w-full">
            <CardHeader>
                <div className="flex-1">
                    <CardTitle>Knowledge Graph</CardTitle>
                    <CardDescription>
                        {stats
                            ? `Showing ${stats.shown_nodes}/${stats.total_nodes} nodes and ${stats.shown_edges}/${stats.total_edges} edges`
                            : "NetworkX graph snapshot (sampled)."}{" "}
                    </CardDescription>
                </div>
                <Button onClick={loadGraph} className="h-9 px-3" disabled={loading}>
                    {loading ? "Loading..." : "Refresh"}
                </Button>
            </CardHeader>

            <CardContent>
                <div className="h-[600px] overflow-hidden rounded-lg border border-[var(--border)] bg-[var(--background)]">
                    <CytoscapeComponent
                        elements={elements}
                        style={{ width: "100%", height: "100%" }}
                        layout={{ name: "cose", animate: false }}
                        stylesheet={[
                            {
                                selector: "node",
                                style: {
                                    label: "data(label)",
                                    color: "#e5e7eb",
                                    "text-outline-color": "#0b0f14",
                                    "text-outline-width": 2,
                                    "font-size": "9px",
                                    "text-wrap": "wrap",
                                    "text-max-width": "80px",
                                    width: "24px",
                                    height: "24px",
                                    "background-color": "#64748b",
                                },
                            },
                            {
                                selector: 'node[type = "document"]',
                                style: {
                                    "background-color": "#2563eb",
                                },
                            },
                            {
                                selector: 'node[type = "chunk"]',
                                style: {
                                    "background-color": "#16a34a",
                                },
                            },
                            {
                                selector: 'node[type = "entity"]',
                                style: {
                                    "background-color": "#dc2626",
                                },
                            },
                            {
                                selector: "edge",
                                style: {
                                    label: "data(label)",
                                    width: "1px",
                                    "font-size": "7px",
                                    "curve-style": "bezier",
                                    "target-arrow-shape": "triangle",
                                    "line-color": "#94a3b8",
                                    "target-arrow-color": "#94a3b8",
                                },
                            },
                        ]}
                    />
                </div>
            </CardContent>
        </Card>
    );
}
