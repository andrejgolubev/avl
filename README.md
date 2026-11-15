# Курсовая работа на тему: AVL-деревья

## Запуск в Windows PowerShell

Требования:
- Python 3.10+ 
- Node.js 22.12+

Команды выполняются из корня проекта. 

1. запуск backend: 
```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe -m uvicorn server:app  
```

2. запуск frontend (в другом терминале):
```powershell
cd frontend 
npm install
npm run dev
```

Далее приложение будет доступно на http://127.0.0.1:5173. Как для взаимодействия, так и для разработки.

## Работа с деревом

Выберите операцию, введите числа через пробел и нажмите «Выполнить».

Разрешено до 127 уникальных ключей от −9999 до 9999. Повторы
игнорируются. При обратном диапазоне возвращается пустой список.
Кнопка «Проверить баланс» проверяет порядок BST, высоты и AVL-баланс.
Кнопка «Очистить дерево» удаляет все ключи.

## Тесты и эксперименты
```powershell
.\.venv\Scripts\python.exe -m pip install -r requirements-dev.txt
.\.venv\Scripts\python.exe main.py --test
.\.venv\Scripts\python.exe -m unittest test_server -v
```
Семь тестов проверяют AVL-дерево, ещё шесть — API.

## Пояснительная записка

[Пояснительная записка](reports/Пояснительная%20записка.docx)

Скриншоты и результаты проверок находятся в `reports/assets`.
