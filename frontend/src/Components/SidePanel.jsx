function SidePanel({ selectedNode }) {
  return (
    <aside className="side-panel">
      <h2>File Details</h2>

      {selectedNode ? (
        <>
          <p><strong>ID:</strong> {selectedNode.id}</p>
          <p><strong>Name:</strong> {selectedNode.data.label}</p>
        </>
      ) : (
        <p>Select a file node to view details.</p>
      )}
    </aside>
  );
}

export default SidePanel;