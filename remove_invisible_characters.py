# Открываем файл app.py и читаем его содержимое
with open("app.py", "r", encoding="utf-8") as f:
    code = f.read()

# Удаляем все невидимые символы
clean_code = ''.join(c for c in code if c.isprintable())

# Записываем очищенный код обратно в файл
with open("app.py", "w", encoding="utf-8") as f:
    f.write(clean_code)

print("Невидимые символы были удалены из файла 'app.py'.")
