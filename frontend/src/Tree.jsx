import styles from './App.module.scss';

export default function Tree({ root, selected }) {
  if (!root) return <div className={styles.empty}>Дерево пусто.</div>;
  const nodes = [], edges = [];
  let index = 0;
  function layout(node, depth) {
    if (!node) return null;
    const left = layout(node.left, depth + 1);
    const point = { ...node, x: 45 + index++ * 64, y: 48 + depth * 90 };
    nodes.push(point);
    const right = layout(node.right, depth + 1);
    for (const child of [left, right]) {
      if (child) edges.push([point, child]);
    }
    return point;
  }
  layout(root, 0);
  const width = Math.max(300, nodes.length * 64 + 26);
  const offset = (width - (nodes.length - 1) * 64) / 2 - 45;
  nodes.forEach(node => { node.x += offset; });
  return <div className={styles.treeScroll}>
    <svg width={width} height={root.height * 90 + 24} role="img" aria-label="Структура AVL-дерева">
      {edges.map(([a, b], i) => <line key={i} x1={a.x} y1={a.y} x2={b.x} y2={b.y} stroke="#bbb" strokeWidth="1.5" />)}
      {nodes.map(node => <g key={node.key} transform={`translate(${node.x},${node.y})`}>
        <circle r="25" className={`${styles.node} ${selected.includes(node.key) ? styles.selected : ''}`} />
        <text textAnchor="middle" dy="5" fontSize="13" className={selected.includes(node.key) ? styles.selectedKey : styles.key}>{node.key}</text>
        <text textAnchor="middle" dy="43" fontSize="10" fill="#666">h={node.height} bf={node.balance}</text>
      </g>)}
    </svg>
  </div>;
}
