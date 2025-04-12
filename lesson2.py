from lesson_2_data import courts  # импорт данных судов и примеров (если надо)


# Аддон, убирающий дробную часть у целых чисел
def clean_number(n):
    return int(n) if n == int(n) else n


# Функция вычисления факториала числа
def factorial():
    try:
        n = int(input("Введите число для вычисления факториала: "))
        if n < 0:
            raise ValueError("Факториал определён только для неотрицательных чисел")
        result = 1
        for i in range(2, n + 1):
            result *= i
        print("Результат:", result)
    except Exception as e:
        print("Ошибка:", e)


# Поиск наибольшего числа из трёх
def max_of_three():
    try:
        nums = input("Введите три числа через пробел: ").split()
        numbers = list(map(float, nums))
        if len(numbers) != 3:
            raise ValueError("Нужно ввести ровно три числа.")
        print("Максимум:", clean_number(max(numbers)))
    except Exception as e:
        print("Ошибка:", e)


# Расчёт площади прямоугольного треугольника
def triangle_area():
    try:
        base = float(input("Введите основание треугольника: "))
        height = float(input("Введите высоту треугольника: "))
        if base <= 0 or height <= 0:
            raise ValueError("Основание и высота должны быть положительными числами")
        area = 0.5 * base * height
        print("Площадь треугольника:", clean_number(area))
    except Exception as e:
        print("Ошибка:", e)


# Функция генерации шапки процессуального документа с вводом данных вручную
def generate_header_from_input():
    short_name = input("Введите наименование ответчика: ").strip()
    inn = input("Введите ИНН ответчика: ").strip()
    ogrn = input("Введите ОГРН ответчика: ").strip()
    address = input("Введите адрес ответчика: ").strip()
    case_number = input("Введите номер дела (например, А40-123456/2023): ").strip().upper()

    court_code = case_number.split("-")[0]

    # Поиск информации о суде в словаре courts
    court_info = courts.get(court_code)

    if court_info:
        court_name = court_info['court_name']
        court_address = court_info['court_address']
    else:
        court_name = f"Арбитражный суд по коду {court_code} (не найден в базе)"
        court_address = "Адрес суда не указан"

    claimant = {
        "name": "ИП Катаев Михаил Алексеевич",
        "inn": "4345182357",
        "ogrn": "218431927812733",
        "address": "610000, Кировская обл., г. Киров, а/я 43"
    }

    header = (
        f"{court_name}\n"
        f"Адрес: {court_address}\n\n"
        f"Истец: {claimant['name']}\n"
        f"ИНН {claimant['inn']} ОГРНИП {claimant['ogrn']}\n"
        f"Адрес: {claimant['address']}\n\n"
        f"Ответчик: {short_name}\n"
        f"ИНН {inn} ОГРН {ogrn}\n"
        f"Адрес: {address}\n\n"
        f"Номер дела {case_number}"
    )

    print("\n" + "-" * 60)
    print(header)
    print("-" * 60 + "\n")

    return header


# Функция валидации ИНН
def validate_inn(inn: str) -> bool:
    inn = inn.strip()

    # Проверка на длину ИНН
    if len(inn) not in [10, 12]:
        return False

    # Проверка на то, что ИНН состоит только из цифр
    if not inn.isdigit():
        return False

    # Валидация ИНН организации (10 цифр)
    if len(inn) == 10:
        return validate_organization_inn(inn)

    # Валидация ИНН физического лица (12 цифр)
    if len(inn) == 12:
        return validate_individual_inn(inn)

    return False


# Валидация ИНН организации
def validate_organization_inn(inn: str) -> bool:
    # Весовые коэффициенты для ИНН организации
    weights = [2, 4, 10, 3, 5, 9, 4, 6, 8]

    # Вычисление контрольной суммы
    checksum = sum(int(inn[i]) * weights[i] for i in range(9))

    # Вычисление контрольного числа
    control_number = checksum % 11
    if control_number > 9:
        control_number %= 10

    # Проверка контрольного числа с 10-й цифрой
    return control_number == int(inn[9])


# Валидация ИНН физического лица
def validate_individual_inn(inn: str) -> bool:
    # Весовые коэффициенты для ИНН физического лица
    weights_1 = [7, 2, 4, 10, 3, 5, 9, 4, 6, 8]
    weights_2 = [3, 7, 2, 4, 10, 3, 5, 9, 4, 6, 8]

    # Вычисление первого контрольного числа
    checksum_1 = sum(int(inn[i]) * weights_1[i] for i in range(10))
    control_number_1 = checksum_1 % 11
    if control_number_1 > 9:
        control_number_1 %= 10

    # Вычисление второго контрольного числа
    checksum_2 = sum(int(inn[i]) * weights_2[i] for i in range(11))
    control_number_2 = checksum_2 % 11
    if control_number_2 > 9:
        control_number_2 %= 10

    # Проверка контрольных чисел с 11-й и 12-й цифрами
    return control_number_1 == int(inn[10]) and control_number_2 == int(inn[11])


# Главное меню
if __name__ == "__main__":
    while True:
        print("\nВыберите действие:")
        print("1. Функция для вычисления факториала числа")
        print("2. Функция для поиска наибольшего числа из трёх")
        print("3. Функция для расчёта площади прямоугольного треугольника")
        print("4. Функция для генерации текста с адресом суда")
        print("5. Функция для валидации ИНН")
        print("6. Выход")

        choice = input("Ваш выбор: ")

        if choice == '1':
            factorial()
        elif choice == '2':
            max_of_three()
        elif choice == '3':
            triangle_area()
        elif choice == '4':
            generate_header_from_input()
        elif choice == '5':
            inn = input("Введите ИНН для проверки: ").strip()
            if validate_inn(inn):
                print("ИНН валиден.")
            else:
                print("ИНН невалиден.")
        elif choice == '6':
            print("Выход из программы...")
            break
        else:
            print("Некорректный ввод. Пожалуйста, выберите от 1 до 6.")