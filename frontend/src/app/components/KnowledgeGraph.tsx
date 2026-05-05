"use client";

import { useEffect, useState } from "react";
import CytoscapeComponent from "react-cytoscapejs";

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
        <div className="w-full border rounded-xl p-4 bg-white">
            <div className="flex justify-between items-center mb-3">
                <div>
                    <h2 className="text-xl font-semibold">Knowledge Graph</h2>
                    {stats && (
                        <p className="text-sm text-gray-500">
                            Showing {stats.shown_nodes}/{stats.total_nodes} nodes and{" "}
                            {stats.shown_edges}/{stats.total_edges} edges
                        </p>
                    )}
                </div>

                <button
                    onClick={loadGraph}
                    className="px-3 py-2 rounded bg-black text-white text-sm"
                >
                    {loading ? "Loading..." : "Refresh"}
                </button>
            </div>

            <div className="h-[600px] border rounded bg-gray-50">
                <CytoscapeComponent
                    elements={elements}
                    style={{ width: "100%", height: "100%" }}
                    layout={{ name: "cose", animate: false }}
                    stylesheet={[
                        {
                            selector: "node",
                            style: {
                                label: "data(label)",
                                "font-size": 9,
                                "text-wrap": "wrap",
                                "text-max-width": 80,
                                width: 24,
                                height: 24,
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
                                width: 1,
                                "font-size": 7,
                                "curve-style": "bezier",
                                "target-arrow-shape": "triangle",
                                "line-color": "#94a3b8",
                                "target-arrow-color": "#94a3b8",
                            },
                        },
                    ]}
                />
            </div>
        </div>
    );
}