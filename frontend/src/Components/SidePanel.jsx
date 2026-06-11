function SidePanel({ selectedNode }) {
  return (
    <aside className="side-panel">
      <h2>File Details</h2>

      {selectedNode ? (
        <>
          <p><strong>Name:</strong> {selectedNode.data.label}</p>
          <p><strong>Path:</strong> {selectedNode.data.path}</p>
          <p><strong>Type:</strong> {selectedNode.data.type}</p>
          <p><strong>Dependencies:</strong> {selectedNode.data.dependencyCount}</p>
        </>
      ) : (
        <p>Select a file node to view details.</p>
      )}
    </aside>
  );
}

export default SidePanel;