"""HTTP-интерфейс учебной демонстрации. Один процесс — одно общее дерево."""
from pathlib import Path
from threading import Lock
from typing import Literal

from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, ConfigDict, Field

from main import AVLTree


app = FastAPI(title="AVL-дерево")
tree = AVLTree()
lock = Lock()
LIMIT = 127


class Action(BaseModel):
    # Аннотации нужны Pydantic для проверки тела запроса.
    model_config = ConfigDict(strict=True, extra="forbid")
    operation: Literal["insert", "delete", "search", "range", "floor", "validate", "clear"]
    values: list[int] = Field(default_factory=list, max_length=127)


def snapshot():
    def pack(node):
        if node is None:
            return None
        return {"key": node.key, "height": node.height, "balance": tree.balance(node),
                "left": pack(node.left), "right": pack(node.right)}

    keys = tree.inorder()
    return {"root": pack(tree.root), "keys": keys, "count": len(keys),
            "height": tree.height(tree.root)}


@app.get("/api/tree")
def get_tree():
    with lock:
        return snapshot()


@app.post("/api/action")
def action(data: Action):
    with lock:
        op, values = data.operation, data.values
        required = {"delete": 1, "search": 1, "floor": 1, "range": 2,
                    "validate": 0, "clear": 0}
        if (op == "insert" and not values) or (op in required and len(values) != required[op]):
            raise HTTPException(400, "Неверное количество чисел для операции.")
        if any(abs(key) > 9999 for key in values):
            raise HTTPException(400, "Введите целые числа от -9999 до 9999.")
        messages, events, selected = [], [], []
        if op == "insert":
            # Проверяем весь пакет до изменения дерева.
            if len(set(tree.inorder()) | set(values)) > LIMIT:
                raise HTTPException(400, f"В веб-демонстрации допускается до {LIMIT} узлов.")
            for key in values:
                added = tree.insert(key)
                messages.append(f"{key}: " + ("добавлен" if added else "уже есть"))
                events.extend(tree.events)
        elif op == "delete":
            messages.append("Ключ удалён." if tree.delete(values[0]) else "Ключ не найден.")
            events = list(tree.events)
        elif op == "search":
            found = tree.contains(values[0])
            messages.append("Ключ найден." if found else "Ключ не найден.")
            selected = values if found else []
        elif op == "floor":
            result = tree.floor(values[0])
            messages.append("Подходящего ключа нет." if result is None else f"Результат: {result}")
            selected = [] if result is None else [result]
        elif op == "range":
            selected = tree.range_keys(*values)
            messages.append(f"Ключи в диапазоне: {selected}")
        elif op == "validate":
            tree.validate()
            messages.append("Порядок BST, высоты и AVL-баланс соблюдены.")
        elif op == "clear":
            tree.root = None
            tree.events.clear()
            messages.append("Дерево очищено.")
        return {**snapshot(), "messages": messages, "events": events, "selected": selected}


# После npm run build интерфейс и API доступны с одного адреса.
dist = Path(__file__).parent / "frontend" / "dist"
if dist.is_dir():
    app.mount("/", StaticFiles(directory=dist, html=True), name="frontend")
