import { useEffect, useState } from "react"
import Tree from "./Tree.jsx"
import styles from "./App.module.scss"

const operations = [
  ["insert", "Добавить"],
  ["delete", "Удалить"],
  ["search", "Найти"],
  ["range", "Диапазон"],
  ["floor", "Наибольший <= x"],
]

export default function App() {
  const [tree, setTree] = useState({
    root: null,
    keys: [],
    count: 0,
    height: 0,
  })
  const [input, setInput] = useState("30 20 10")
  const [operation, setOperation] = useState("insert")
  const [messages, setMessages] = useState([])
  const [events, setEvents] = useState([])
  const [selected, setSelected] = useState([])
  const [error, setError] = useState("")
  const [busy, setBusy] = useState(false)

  async function load() {
    setBusy(true)
    try {
      const response = await fetch("/api/tree")
      if (!response.ok) throw new Error()
      setTree(await response.json())
      setError("")
      setSelected([])
      setEvents([])
      setMessages([])
    } catch {
      setError("Сервер недоступен. Нажмите «Обновить».")
    } finally {
      setBusy(false)
    }
  }
  useEffect(() => {
    load()
  }, [])

  async function perform(op, supplied) {
    setError("")
    const text = input.trim()
    if (
      !supplied &&
      (!text || !text.split(/\s+/).every((v) => /^[+-]?\d+$/.test(v)))
    ) {
      setError("Введите целые числа через пробел.")
      return
    }
    const values = supplied || text.split(/\s+/).map(Number)
    if (values.some((v) => !Number.isSafeInteger(v) || Math.abs(v) > 9999)) {
      setError("Допустимы целые числа от -9999 до 9999.")
      return
    }
    setBusy(true)
    try {
      const response = await fetch("/api/action", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ operation: op, values }),
      })
      const data = await response.json()
      if (!response.ok)
        throw new Error(
          typeof data.detail === "string"
            ? data.detail
            : "Проверьте входные данные."
        )
      setTree(data)
      setMessages(data.messages)
      setEvents(data.events)
      setSelected(data.selected)
    } catch (e) {
      setError(
        e.message === "Failed to fetch" ? "Нет связи с сервером." : e.message
      )
    } finally {
      setBusy(false)
    }
  }

  return (
    <main className={styles.app}>
      <header className={styles.header}>
        <h1>AVL-дерево</h1>
      </header>
      <div className={styles.workspace}>
        <section className={styles.controls} aria-label="Операции с деревом">
          <form
            onSubmit={(e) => {
              e.preventDefault()
              perform(operation)
            }}
          >
            <div className={styles.field}>
              <label htmlFor="operation">Операция</label>
              <select
                id="operation"
                value={operation}
                onChange={(e) => setOperation(e.target.value)}
                disabled={busy}
              >
                {operations.map(([value, label]) => (
                  <option key={value} value={value}>
                    {label}
                  </option>
                ))}
              </select>
            </div>
            <div className={styles.field}>
              <label htmlFor="values">
                {operation === "range"
                  ? "Нижняя и верхняя границы"
                  : operation === "insert"
                  ? "Ключи через пробел"
                  : "Ключ"}
              </label>
              <input
                id="values"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="30 20 10"
                disabled={busy}
              />
            </div>
            <button className={styles.primary} disabled={busy}>
              {busy ? "Выполняется…" : "Выполнить"}
            </button>
          </form>
          <div className={styles.secondary}>
            <button onClick={() => perform("validate", [])} disabled={busy}>
              Проверить баланс
            </button>
            <button onClick={() => perform("clear", [])} disabled={busy}>
              Очистить дерево
            </button>
            <button onClick={load} disabled={busy}>
              Обновить
            </button>
          </div>
          <p className={styles.hint}>
            От −9999 до 9999, до 127 ключей. Повторы не добавляются.
          </p>
        </section>
        <section className={styles.visual}>
          <div className={styles.panelHeader}>
            <h2>Дерево</h2>
            <div className={styles.stats}>
              <span>
                Узлов <b>{tree.count}</b>
              </span>
              <span>
                Высота <b>{tree.height}</b>
              </span>
            </div>
          </div>
          <Tree root={tree.root} selected={selected} />
          <div className={styles.traversal}>
            <span>Обход по возрастанию</span>
            <p>
              {tree.keys.length ? tree.keys.join(", ") : "—"}
            </p>
          </div>
        </section>
      </div>
      {(error || messages.length > 0 || events.length > 0) && (
        <section className={styles.results} aria-live="polite" aria-label="Результат операции">
          {error && (
            <p className={styles.error} role="alert">
              {error}
            </p>
          )}
          {!error && (
            <>
              <p>{messages.join(" · ")}</p>
              {events.length > 0 && (
                <ul>
                  {events.map((event, i) => (
                    <li key={i}>{event}</li>
                  ))}
                </ul>
              )}
            </>
          )}
        </section>
      )}
      <footer>
        h — высота, bf — баланс. Дерево общее для вкладок и хранится до перезапуска сервера.
      </footer>
    </main>
  )
}
