import ReactFlow, {
  Background,
  Controls,
  MiniMap,
  useEdgesState,
  useNodesState,
} from "reactflow";
import "reactflow/dist/style.css";
import { sampleNodes, sampleEdges } from "../data/sampleGraph";

function GraphCanvas({ onNodeClick }) {
  const [nodes, , onNodesChange] = useNodesState(sampleNodes);
  const [edges, , onEdgesChange] = useEdgesState(sampleEdges);

  return (
    <div className="graph-canvas">
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
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