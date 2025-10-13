# Задача 1
# Напишите функцию fib(), которая генерирует числа Фибоначчи и принимает n — сколько чисел сгенерировать.

def fib(n: int):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n должно быть целым неотрицательным числом")
    a, b = 0, 1
    result = []
    for _ in range(n):
        result.append(a)
        a, b = b, a + b
    return result

# Задача 1*
# Сделайте функцию-генератор, используя yield.

def fib_gen(n: int):
    if not isinstance(n, int) or n < 0:
        raise ValueError("n должно быть целым неотрицательным числом")
    a, b = 0, 1
    for _ in range(n):
        yield a
        a, b = b, a + b

# Задача 2
# Конвертер римских чисел в десятичные с валидацией.

def roman_to_int(s: str) -> int:
    if not isinstance(s, str) or not s:
        raise ValueError("Ввод должен быть непустой строкой")

    s = s.upper()
    values = {'I': 1, 'V': 5, 'X': 10, 'L': 50,
              'C': 100, 'D': 500, 'M': 1000}
    allowed_subtractive = {('I', 'V'), ('I', 'X'),
                           ('X', 'L'), ('X', 'C'),
                           ('C', 'D'), ('C', 'M')}
    repeatable = {'I', 'X', 'C', 'M'}
    non_repeatable = {'V', 'L', 'D'}

    # Базовая проверка символов
    for ch in s:
        if ch not in values:
            raise ValueError(f"Введён неверный символ: {ch}")

    # Проверка повторов (консекутивно)
    run_char = None
    run_len = 0
    for ch in s:
        if ch == run_char:
            run_len += 1
        else:
            run_char, run_len = ch, 1
        if run_char in non_repeatable and run_len > 1:
            raise ValueError(f"Недопустимо повторять {run_char}")
        if run_char in repeatable and run_len > 3:
            raise ValueError(f"Слишком много повторений {run_char}")

    # Доп. запрет: нельзя ставить ДВА одинаковых меньших перед большим (IIX, XXL, CCD и т.п.)
    # Проверяем шаблон s[i] == s[i+1] и s[i] < s[i+2]
    for i in range(len(s) - 2):
        a, b, c = s[i], s[i + 1], s[i + 2]
        if a == b and values[a] < values[c]:
            raise ValueError(f"Недопустимая вычитательная конструкция: {a}{b}{c}")

    total = 0
    prev_val = 0
    prev_char = None

    for ch in reversed(s):
        cur_val = values[ch]
        if cur_val < prev_val:
            # Проверим допустимость пары вычитания
            if (ch, prev_char) not in allowed_subtractive:
                raise ValueError(f"Неверная вычитательная пара: {ch} перед {prev_char}")
            total -= cur_val
        else:
            total += cur_val
        prev_val = cur_val
        prev_char = ch

    # Классический диапазон
    if not (0 < total <= 3999):
        raise ValueError("Значение вне диапазона 1..3999")

    return total

# Задача 3
# Проверка монотонности (неубывающей или невозрастающей).

def is_monotonic(nums):
    if not isinstance(nums, list) or not all(isinstance(x, (int, float)) for x in nums):
        raise ValueError("Ожидается список чисел (int/float)")
    # Пустой или из одного элемента — монотонен
    if len(nums) < 2:
        return True
    return (
        all(nums[i] <= nums[i + 1] for i in range(len(nums) - 1)) or
        all(nums[i] >= nums[i + 1] for i in range(len(nums) - 1))
    )

if __name__ == "__main__":
    while True:
        print("\nВыберите действие:")
        print("1. Генерация чисел Фибоначчи")
        print("2. Конвертер римских чисел в десятичные")
        print("3. Проверка монотонности последовательности")
        print("4. Выход")

        choice = input("Ваш выбор: ").strip()

        if choice == '1':
            try:
                n = int(input("Введите количество чисел Фибоначчи: ").strip())
                print(list(fib_gen(n)))
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '2':
            s = input("Введите римское число: ").strip()
            try:
                print(f"Результат: {roman_to_int(s)}")
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '3':
            raw = input("Введите числа через пробел: ").strip()
            try:
                nums = [float(x) for x in raw.split()] if raw else []
                print("Монотонная:", is_monotonic(nums))
            except Exception as e:
                print(f"Ошибка: {e}")

        elif choice == '4':
            print("Выход из программы...")
            break
        else:
            print("Некорректный ввод. Пожалуйста, выберите от 1 до 4.")