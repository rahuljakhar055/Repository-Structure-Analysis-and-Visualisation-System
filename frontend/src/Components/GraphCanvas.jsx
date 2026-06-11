import React from "react";
import ReactFlow, {
  Background,
  Controls,
  MiniMap,
} from "reactflow";

import "reactflow/dist/style.css";

const initialNodes = [
  {
    id: "backend/app.py",
    position: { x: 100, y: 100 },
    data: { label: "app.py" },
  },
  {
    id: "backend/scanner/traverse.py",
    position: { x: 400, y: 200 },
    data: { label: "traverse.py" },
  },
];

const initialEdges = [
  {
    id: "edge-1",
    source: "backend/app.py",
    target: "backend/scanner/traverse.py",
  },
];

function GraphCanvas({ onNodeClick }) {
  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={initialNodes}
        edges={initialEdges}
        onNodeClick={(_, node) => onNodeClick(node)}
        fitView
      >
        <Background />
        <Controls />
        <MiniMap />
      </ReactFlow>
    </div>
  );
}

export default GraphCanvas;