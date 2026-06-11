export const sampleNodes = [
  {
    id: "backend/app.py",
    position: { x: 100, y: 120 },
    data: {
      label: "app.py",
      path: "backend/app.py",
      type: "python",
      dependencyCount: 2,
    },
  },
  {
    id: "backend/scanner/traverse.py",
    position: { x: 430, y: 60 },
    data: {
      label: "traverse.py",
      path: "backend/scanner/traverse.py",
      type: "python",
      dependencyCount: 1,
    },
  },
  {
    id: "backend/scanner/parser.py",
    position: { x: 430, y: 220 },
    data: {
      label: "parser.py",
      path: "backend/scanner/parser.py",
      type: "python",
      dependencyCount: 3,
    },
  },
];

export const sampleEdges = [
  {
    id: "app-to-traverse",
    source: "backend/app.py",
    target: "backend/scanner/traverse.py",
  },
  {
    id: "traverse-to-parser",
    source: "backend/scanner/traverse.py",
    target: "backend/scanner/parser.py",
  },
];