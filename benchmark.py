"""Небольшое сравнение AVL и BST без HTTP и вывода дерева."""
import argparse
import csv
import json
import platform
import random
import statistics
import time
from pathlib import Path

from main import AVLTree


class BSTNode:
    def __init__(self, key):
        self.key = key
        self.left = None
        self.right = None


class BST:
    def __init__(self):
        self.root = None

    def insert(self, key):
        if self.root is None:
            self.root = BSTNode(key)
            return
        node = self.root
        while True:
            if key == node.key:
                return
            side = "left" if key < node.key else "right"
            child = getattr(node, side)
            if child is None:
                setattr(node, side, BSTNode(key))
                return
            node = child

    def contains(self, key):
        node = self.root
        while node:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def height(self):
        # Итеративно: у BST на упорядоченном вводе большая глубина.
        stack = [(self.root, 1)] if self.root else []
        result = 0
        while stack:
            node, depth = stack.pop()
            result = max(result, depth)
            for child in [node.left, node.right]:
                if child:
                    stack.append((child, depth + 1))
        return result


def run(output):
    rows = []
    for n in [1000, 3000, 10000]:
        for order in ["random", "sorted"]:
            values = list(range(n))
            if order == "random":
                random.Random(42).shuffle(values)
            rng = random.Random(17)
            queries = [rng.randrange(n) for _ in range(1000)]
            queries += [n + i for i in range(1000)]
            for name, cls in [("AVL", AVLTree), ("BST", BST)]:
                for repeat in range(3):
                    tree = cls()
                    start = time.perf_counter()
                    for key in values:
                        tree.insert(key)
                    build_ms = (time.perf_counter() - start) * 1000
                    start = time.perf_counter()
                    hits = sum(tree.contains(key) for key in queries)
                    search_ms = (time.perf_counter() - start) * 1000
                    assert hits == 1000
                    if name == "AVL":
                        tree.validate()
                        assert tree.inorder() == list(range(n))
                        height = tree.height(tree.root)
                    else:
                        height = tree.height()
                        # Проверяем состав независимо от результатов запросов.
                        stack, keys = [tree.root], []
                        while stack:
                            node = stack.pop()
                            if node:
                                keys.append(node.key)
                                stack.extend([node.left, node.right])
                        assert sorted(keys) == list(range(n))
                    rows.append(dict(n=n, order=order, structure=name, repeat=repeat + 1,
                                     build_ms=build_ms, search_ms=search_ms, height=height))
                batch = rows[-3:]
                print(n, order, name, "build ms:", round(statistics.median(r["build_ms"] for r in batch), 3), flush=True)
    save(output, rows)


def save(output, rows):
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)
    metadata = {"python": platform.python_version(), "platform": platform.platform(),
                "processor": platform.processor(), "repeats": 3, "seed": 42,
                "query_seed": 17, "timer": "perf_counter", "unit": "ms"}
    output.with_suffix(".json").write_text(json.dumps(metadata, ensure_ascii=False, indent=2), encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="reports/assets/comparison.csv")
    args = parser.parse_args()
    run(args.output)
