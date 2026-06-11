import { useState } from "react";
import GraphCanvas from "./components/GraphCanvas";
import SidePanel from "./components/SidePanel";
import "./App.css";

function App() {
  const [selectedNode, setSelectedNode] = useState(null);

  return (
    <main className="app-layout">
      <GraphCanvas onNodeClick={setSelectedNode} />
      <SidePanel selectedNode={selectedNode} />
    </main>
  );
}

export default App;