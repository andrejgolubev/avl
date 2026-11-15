"""
AVL-дерево целых ключей.

Требуется: Python 3.10+
Запуск встроенных модульных тестов: python main.py --test

Дерево реализует множество: повторная вставка не меняет его.
Соглашение: высота пустого дерева 0, листа 1;
balance = height(left) - height(right).
"""
from __future__ import annotations

from dataclasses import dataclass
import random
import sys
import unittest


@dataclass
class Node:
    key: int
    left: Node | None = None
    right: Node | None = None
    height: int = 1


class AVLTree:
    def __init__(self) :
        self.root = None
        # Журнал только последней вставки/удаления, включая составные повороты.
        self.events = []

    @staticmethod
    def height(node):
        return node.height if node else 0

    def balance(self, node):
        return self.height(node.left) - self.height(node.right) if node else 0

    def _update(self, node) :
        node.height = 1 + max(self.height(node.left), self.height(node.right))

    def _rotate_right(self, node):
        pivot = node.left
        assert pivot is not None
        node.left = pivot.right
        pivot.right = node
        # Сначала обновляется нижний узел, затем новый корень поддерева.
        self._update(node)
        self._update(pivot)
        self.events.append(f"Малый правый поворот вокруг {node.key}")
        return pivot

    def _rotate_left(self, node):
        pivot = node.right
        assert pivot is not None
        node.right = pivot.left
        pivot.left = node
        self._update(node)
        self._update(pivot)
        self.events.append(f"Малый левый поворот вокруг {node.key}")
        return pivot

    def _rebalance(self, node):
        self._update(node)
        if self.balance(node) > 1:
            if self.balance(node.left) < 0:
                self.events.append(f"Большой правый поворот (LR) вокруг {node.key}")
                node.left = self._rotate_left(node.left)
            return self._rotate_right(node)
        if self.balance(node) < -1:
            if self.balance(node.right) > 0:
                self.events.append(f"Большой левый поворот (RL) вокруг {node.key}")
                node.right = self._rotate_right(node.right)
            return self._rotate_left(node)
        return node

    def insert(self, key):
        """Добавить ключ. True - добавлен, False - уже присутствовал."""
        self.events.clear()
        self.root, added = self._insert(self.root, key)
        return added

    def _insert(self, node, key):
        if node is None:
            return Node(key), True
        if key < node.key:
            node.left, added = self._insert(node.left, key)
        elif key > node.key:
            node.right, added = self._insert(node.right, key)
        else:
            return node, False
        return self._rebalance(node), added

    def delete(self, key):
        """Удалить ключ. True - удалён, False - отсутствовал."""
        self.events.clear()
        self.root, removed = self._delete(self.root, key)
        return removed

    def _delete(self, node, key):
        if node is None:
            return None, False
        if key < node.key:
            node.left, removed = self._delete(node.left, key)
        elif key > node.key:
            node.right, removed = self._delete(node.right, key)
        else:
            if node.left is None:
                return node.right, True
            if node.right is None:
                return node.left, True
            # Два сына: заменяем ключ минимальным в правом поддереве.
            successor = node.right
            while successor.left is not None:
                successor = successor.left
            node.key = successor.key
            node.right, _ = self._delete(node.right, successor.key)
            removed = True
        # После удаления баланс может нарушиться у нескольких предков.
        return self._rebalance(node), removed

    def contains(self, key):
        node = self.root
        while node is not None:
            if key == node.key:
                return True
            node = node.left if key < node.key else node.right
        return False

    def floor(self, key):
        """Наибольший ключ, не превосходящий key, либо None."""
        node, result = self.root, None
        while node is not None:
            if node.key == key:
                return key
            if node.key < key:
                result, node = node.key, node.right
            else:
                node = node.left
        return result

    def inorder(self):
        result = []

        def visit(node) :
            if node is not None:
                visit(node.left)
                result.append(node.key)
                visit(node.right)

        visit(self.root)
        return result
    
    # ДАЛЕЕ МЕТОДЫ ДЛЯ ТЕСТИРОВАНИЯ И ВЫВОДА ДЕРЕВА
    def range_keys(self, low, high):
        """Ключи из [low, high] по возрастанию с отсечением лишних ветвей."""
        result = []

        def visit(node) :
            if node is None:
                return
            if low < node.key:
                visit(node.left)
            if low <= node.key <= high:
                result.append(node.key)
            if node.key < high:
                visit(node.right)

        if low <= high:
            visit(self.root)
        return result

    def validate(self) :
        """Проверить порядок BST, высоты и баланс; ошибка - AssertionError."""
        def check(node, low, high):
            if node is None:
                return 0
            assert low is None or low < node.key, "Нарушен нижний предел BST"
            assert high is None or node.key < high, "Нарушен верхний предел BST"
            left = check(node.left, low, node.key)
            right = check(node.right, node.key, high)
            assert node.height == 1 + max(left, right), "Неверная высота"
            assert abs(left - right) <= 1, "Нарушен AVL-баланс"
            return node.height

        check(self.root, None, None)

    def show(self) :
        """Корень сверху, дети ниже с отступами и подписями Л/П."""
        def visit(node, depth, side) :
            if node is None:
                return
            print("    " * depth + f"{side}: {node.key} "
                  f"(h={node.height}, bf={self.balance(node)})")
            visit(node.left, depth + 1, "Л")
            visit(node.right, depth + 1, "П")

        if self.root is None:
            print("Дерево пусто.")
        else:
            visit(self.root, 0, "Корень")

    

class AVLTests(unittest.TestCase):
    def make_tree(self, values):
        tree = AVLTree()
        for key in values:
            tree.insert(key)
            tree.validate()
        return tree

    def test_four_rotation_cases(self) :
        cases = {
            "LL": [30, 20, 10], "RR": [10, 20, 30],
            "LR": [30, 10, 20], "RL": [10, 30, 20],
        }
        for name, values in cases.items():
            with self.subTest(case=name):
                tree = self.make_tree(values)
                self.assertEqual(tree.root.key, 20)
                self.assertEqual(tree.inorder(), [10, 20, 30])
                self.assertTrue(tree.events)

    def test_duplicate_and_missing_key(self) :
        tree = self.make_tree([5])
        self.assertFalse(tree.insert(5))
        self.assertFalse(tree.delete(8))
        self.assertEqual(tree.inorder(), [5])
        tree.validate()

    def test_delete_leaf_one_child_and_two_children(self) :
        for values, key in [([20, 10, 30], 10),
                            ([20, 10, 30, 25], 30),
                            ([20, 10, 30, 25, 40], 20)]:
            with self.subTest(values=values, key=key):
                tree = self.make_tree(values)
                self.assertTrue(tree.delete(key))
                tree.validate()
                self.assertEqual(tree.inorder(), sorted(set(values) - {key}))

    def test_delete_with_zero_child_balance(self) :
        tree = self.make_tree([4, 2, 5, 1, 3])
        tree.delete(5)
        tree.validate()
        self.assertEqual(tree.root.key, 2)
        self.assertTrue(tree.events)

    def test_search_floor_and_range(self) :
        tree = self.make_tree([-10, 0, 8, 3, 20])
        self.assertTrue(tree.contains(8))
        self.assertFalse(tree.contains(9))
        self.assertEqual(tree.floor(7), 3)
        self.assertEqual(tree.floor(8), 8)
        self.assertIsNone(tree.floor(-11))
        self.assertEqual(tree.range_keys(0, 8), [0, 3, 8])
        self.assertEqual(tree.range_keys(8, 0), [])

    def test_delete_all_and_empty_tree(self) :
        tree = self.make_tree(list(range(100)))
        for key in range(100):
            self.assertTrue(tree.delete(key))
            tree.validate()
        self.assertIsNone(tree.root)
        self.assertFalse(tree.delete(0))
        self.assertFalse(tree.contains(0))
        self.assertEqual(tree.range_keys(-10, 10), [])

    def test_random_operations_against_set(self) :
        rng = random.Random(42)
        tree, expected = AVLTree(), set()
        for _ in range(3000):
            key = rng.randrange(-200, 201)
            if rng.randrange(2):
                self.assertEqual(tree.insert(key), key not in expected)
                expected.add(key)
            else:
                self.assertEqual(tree.delete(key), key in expected)
                expected.discard(key)
            tree.validate()
            self.assertEqual(tree.inorder(), sorted(expected))


def main() :
    tree = AVLTree()
    while True:
        print("\n1 - вставить числа   2 - удалить   3 - найти"
              "\n4 - показать дерево  5 - обход по возрастанию"
              "\n6 - ключи в диапазоне  7 - наибольший ключ <= x"
              "\n8 - проверить инварианты  0 - выход")
        try:
            choice = input("Выбор: ").strip()
            if choice == "0":
                return
            if choice == "1":
                values = [int(x) for x in input("Целые числа через пробел: ").split()]
                for key in values:
                    print(f"{key}: " + ("добавлен" if tree.insert(key) else "уже есть"))
                    for event in tree.events:
                        print("  " + event)
            elif choice == "2":
                key = int(input("Удалить ключ: "))
                print("Удалён." if tree.delete(key) else "Ключ не найден.")
                for event in tree.events:
                    print("  " + event)
            elif choice == "3":
                print("Найден." if tree.contains(int(input("Ключ: "))) else "Не найден.")
            elif choice == "4":
                tree.show()
            elif choice == "5":
                print(tree.inorder())
            elif choice == "6":
                low, high = map(int, input("Границы low high: ").split())
                print(tree.range_keys(low, high))
            elif choice == "7":
                value = tree.floor(int(input("x: ")))
                print("Подходящего ключа нет." if value is None else value)
            elif choice == "8":
                tree.validate()
                print("Порядок BST, высоты и AVL-баланс соблюдены.")
            else:
                print("Выберите пункт от 0 до 8.")
        except ValueError:
            print("Ошибка: нужны целые числа в указанном количестве.")
        except (EOFError, KeyboardInterrupt):
            print("\nРабота завершена.")
            return


if __name__ == "__main__":
    if sys.argv[1:] == ["--test"]:
        unittest.main(argv=[sys.argv[0]], verbosity=2)
    elif sys.argv[1:]:
        print("Использование: python main.py [--test]", file=sys.stderr)
        sys.exit(2)
    else:
        main()
