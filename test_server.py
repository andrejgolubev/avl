import unittest

from fastapi.testclient import TestClient

from server import app


class APITests(unittest.TestCase):
    def setUp(self):
        self.client = TestClient(app)
        self.send("clear")

    def send(self, operation, values=None):
        return self.client.post("/api/action", json={"operation": operation, "values": values or []})

    def test_insert_rotation_and_duplicates(self):
        response = self.send("insert", [30, 20, 10, 10])
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertEqual(data["root"]["key"], 20)
        self.assertEqual(data["count"], 3)
        self.assertEqual(data["height"], 2)
        self.assertIn("Малый правый поворот вокруг 30", data["events"])
        self.assertEqual(self.client.get("/api/tree").json()["keys"], [10, 20, 30])

    def test_queries_and_highlight(self):
        self.send("insert", [-10, 0, 8, 3, 20])
        self.assertEqual(self.send("search", [8]).json()["selected"], [8])
        self.assertEqual(self.send("search", [9]).json()["selected"], [])
        self.assertEqual(self.send("floor", [7]).json()["selected"], [3])
        self.assertEqual(self.send("floor", [-11]).json()["selected"], [])
        self.assertEqual(self.send("range", [0, 8]).json()["selected"], [0, 3, 8])
        self.assertEqual(self.send("range", [8, 0]).json()["selected"], [])

    def test_delete_validate_clear(self):
        self.send("insert", [20, 10, 30, 25, 40])
        data = self.send("delete", [20]).json()
        self.assertEqual(data["keys"], [10, 25, 30, 40])
        self.assertEqual(data["root"]["key"], 25)
        self.assertEqual(self.send("validate").status_code, 200)
        self.assertEqual(self.send("delete", [99]).json()["count"], 4)
        self.assertEqual(self.send("clear").json()["root"], None)

    def test_invalid_values_do_not_change_tree(self):
        self.send("insert", [5])
        for values in [[10, 10000], [], [True], [1.5], ["3"]]:
            with self.subTest(values=values):
                self.assertIn(self.send("insert", values).status_code, [400, 422])
                self.assertEqual(self.client.get("/api/tree").json()["keys"], [5])

    def test_bad_operation_and_argument_count(self):
        for op, values in [("unknown", []), ("search", []), ("range", [1]),
                           ("delete", [1, 2]), ("clear", [1]), ("validate", [1])]:
            with self.subTest(operation=op):
                self.assertIn(self.send(op, values).status_code, [400, 422])

    def test_limit_checked_before_insertion(self):
        self.send("insert", list(range(126)))
        self.assertEqual(self.send("insert", [126, 127]).status_code, 400)
        self.assertEqual(self.client.get("/api/tree").json()["count"], 126)
        self.assertEqual(self.send("insert", [126]).json()["count"], 127)
        self.assertEqual(self.send("insert", [126]).json()["count"], 127)


if __name__ == "__main__":
    unittest.main(verbosity=2)
