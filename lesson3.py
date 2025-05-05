import json
import csv
import re
from collections import defaultdict

def info(): # Создание CSV из traders.txt и traders.json

    # Загрузка ИНН из файла
    with open("traders.txt", "r", encoding="utf-8") as txt_file:
        inn_list = [line.strip() for line in txt_file if line.strip()]

    # Загрузка данных из JSON
    with open("traders.json", "r", encoding="utf-8") as json_file:
        traders_data = json.load(json_file)

    # Поиск организаций по ИНН
    filtered_data = []
    for entry in traders_data:
        inn = entry.get("ИНН") or entry.get("inn")  # Учитываем разные возможные ключи
        if inn in inn_list:
            ogrn = entry.get("ОГРН") or entry.get("ogrn", "")
            address = entry.get("Адрес") or entry.get("address", "")
            filtered_data.append({"ИНН": inn, "ОГРН": ogrn, "Адрес": address})

    # Сохранение в CSV
    csv_path = "traders.csv"
    with open(csv_path, "w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=["ИНН", "ОГРН", "Адрес"])
        writer.writeheader()
        writer.writerows(filtered_data)

    print("Информации об организациях успешно извлечены и сохранены в traders.csv.")

def emails():  # Извлечение email из efrsb_messages.json

    EMAIL_PATTERN = r'\b[\w\.-]+@[\w\.-]+\.\w+\b'

    def find_emails(text): # Возвращает список email-адресов, найденных в тексте
        return re.findall(EMAIL_PATTERN, text)

    def extract_emails_from_message(msg): # Ищет email-адреса во всех строковых полях сообщения
        emails = set()
        for value in msg.values():
            if isinstance(value, str):
                emails.update(find_emails(value))
        return emails

    def extract_and_save_emails():
        with open("1000_efrsb_messages.json", "r", encoding="utf-8") as file:
            messages_data = json.load(file)

        emails_by_inn = defaultdict(set)

        for msg in messages_data:
            inn = msg.get("publisher_inn", "")
            if inn:
                emails = extract_emails_from_message(msg)
                if emails:
                    emails_by_inn[inn].update(emails)

        # Сохраняем результат в JSON
        result = {inn: sorted(list(emails)) for inn, emails in emails_by_inn.items()}
        with open("emails.json", "w", encoding="utf-8") as out:
            json.dump(result, out, ensure_ascii=False, indent=2)

    extract_and_save_emails()

    print("Email-адреса успешно извлечены и сохранены в emails.json.")

# Главное меню
if __name__ == "__main__":
    while True:
        print("\nВыберите действие:")
        print("1. Найти информацию об организациях")
        print("2. Найти email-адреса в тексте")
        print("3. Выход")

        choice = input("Ваш выбор: ")

        if choice == '1':
            info()
        elif choice == '2':
            emails()
        elif choice == '3':
            print("Выход из программы...")
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите значение от 1 до 3.")