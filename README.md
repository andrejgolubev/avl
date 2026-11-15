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

В первой версии интерфейса доступна вставка чисел через пробел.
Остальные операции уже доступны через API на порту 8000.

## Пояснительная записка

[Пояснительная записка](reports/Пояснительная%20записка.docx)
