import { useEffect, useState } from "react"
import Tree from "./Tree.jsx"
import styles from "./App.module.scss"

export default function App() {
  const [tree, setTree] = useState({root: null, keys: [], count: 0, height: 0})
  const [input, setInput] = useState("30 20 10")
  const [message, setMessage] = useState("")
  useEffect(() => {
    fetch("/api/tree").then(r => r.json()).then(setTree)
      .catch(() => setMessage("Сервер недоступен."))
  }, [])
  async function insert(e) {
    e.preventDefault()
    const values = input.trim().split(/\s+/)
    if (!input.trim() || !values.every(v => /^[+-]?\d+$/.test(v))) {
      setMessage("Введите целые числа через пробел.")
      return
    }
    try {
      const response = await fetch("/api/action", {
        method: "POST", headers: {"Content-Type": "application/json"},
        body: JSON.stringify({operation: "insert", values: values.map(Number)}),
      })
      const data = await response.json()
      if (!response.ok) throw new Error(data.detail || "Ошибка запроса.")
      setTree(data)
      setMessage([...data.messages, ...data.events].join(" · "))
    } catch (error) { setMessage(error.message) }
  }
  return <main className={styles.app}>
    <header className={styles.header}><h1>AVL-дерево</h1></header>
    <section className={styles.controls}>
      <form onSubmit={insert}>
        <div className={styles.field}>
          <label htmlFor="values">Ключи через пробел</label>
          <input id="values" value={input} onChange={e => setInput(e.target.value)} />
        </div>
        <button className={styles.primary}>Добавить</button>
      </form>
    </section>
    <section className={styles.visual}>
      <div className={styles.panelHeader}><h2>Дерево</h2>
        <span>Узлов {tree.count} · Высота {tree.height}</span></div>
      <Tree root={tree.root} selected={[]} />
      <div className={styles.traversal}>{tree.keys.join(", ")}</div>
    </section>
    <p>{message}</p>
  </main>
}
