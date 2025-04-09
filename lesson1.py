def get_main():
    while True:
        print("\nВведите число для продолжения:")
        print("1. Сравнить числа (работа с переменными)")
        print("2. Ввести время в секундах и преобразовать в часы, минуты и секунды")
        print("3. Найти сумму чисел")
        print("4. Выход")

        choice = input()

        if choice == '1':
            compare_numbers()
        elif choice == '2':
            get_time_in_seconds()
        elif choice == '3':
            get_addition()
        elif choice == '4':
            print("Выход из программы...")
            break
        else:
            print("Некорректный ввод. Пожалуйста, выберите 1, 2, 3 или 4.")

# Задание 1
    # Поработайте с переменными, создайте несколько, выведите на экран.
    # Запросите у пользователя некоторые числа и строки и сохраните в переменные, а затем выведите на экран.
    # Используйте функции для консольного ввода input() и консольного вывода print().
    # Попробуйте также через встроенную функцию id() понаблюдать, какие типы объектов могут изменяться и сохранять за собой адрес в оперативной памяти.

def compare_numbers():

    def get_number(prompt):
        while True:
            user_input = input(prompt)
            try:
                number = float(user_input)
                return number
            except ValueError:
                print('Некорректный ввод. Повторите попытку еще раз.')

    user_number1 = get_number("Введите первое число: ")
    user_number2 = get_number("Введите второе число: ")

    num1 = int(user_number1) if user_number1.is_integer() else user_number1
    num2 = int(user_number2) if user_number2.is_integer() else user_number2

    print("Адрес памяти для первого числа после преобразования: ", id(num1))
    print("Адрес памяти для второго числа после преобразования: ", id(num2))

    print("")

    if num1 > num2:
        print(num1, "больше", num2)
    elif num1 < num2:
        print(num1, "меньше", num2)
    else:
        print(num1, "равен", num2)

# Задание 2
    # Пользователь вводит время в секундах.
    # Рассчитайте время и сохраните отдельно в каждую переменную количество часов, минут и секунд.
    # Переведите время в часы, минуты, секунды и сохраните в отдельных переменных.
    # Используйте приведение типов для перевода строк в числовые типы.
    # Предусмотрите проверку строки на наличие только числовых данных через встроенный строковый метод .isdigit().
    # Выведите рассчитанные часы, минуты и секунды по отдельности в консоль.

def get_time_in_seconds():
    while True:
        user_input = input("Введите время в секундах: ")
        if user_input.isdigit():
            total_seconds = int(user_input)
            hours = total_seconds // 3600  # Часы = общее количество секунд разделить на 3600 (количество секунд в часе)
            minutes = (total_seconds % 3600) // 60  # Минуты = оставшиеся секунды после получения часов, делим на 60
            seconds = total_seconds % 60  # Секунды = остаток от деления на 60

            print(f"Часы: {hours}")
            print(f"Минуты: {minutes}")
            print(f"Секунды: {seconds}")
            break
        else:
            print("Некорректный ввод. Пожалуйста, введите только числовые значения.")

# Задание 3.
    # Запросите у пользователя через консоль число n (от 1 до 9). Найдите сумму чисел n + nn + nnn.
    # Например, пользователь ввёл число 3. Считаем 3 + 33 + 333 = 369.
    # Выведите данные в консоль.

def get_addition():
    while True:
        user_input = input("Введите число от 1 до 9: ")
        if user_input.isdigit() and 1 <= int(user_input ) <= 9:
            n1 = int(user_input)  # n
            n2 = int(user_input  * 2)  # nn
            n3 = int(user_input  * 3)  # nnn

            result = n1 + n2 + n3

            print(str(n1) + " + " + str(n2) + " + " + str(n3) + " = " + str(result))
            break
        else:
            print("Ошибка: Введите число от 1 до 9.")

if __name__ == "__main__":
    get_main()