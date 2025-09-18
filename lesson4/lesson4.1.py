from datetime import datetime

class CourtCase:
    def __init__(self, case_number: str):
        if not isinstance(case_number, str) or not case_number.strip():
            raise ValueError("case_number не должен быть пустой строкой")
        self.case_number = case_number
        self.case_participants = []       # список участников
        self.listening_datetimes = []     # список заседаний
        self.is_finished = False          # дело не завершено
        self.verdict = ""                 # решение пока пустое

###

    # Добавить участника
    def add_participant(self, inn: str):
        if not isinstance(inn, str) or not inn.strip():
            raise ValueError("ИНН должен быть строкой")
        if inn in self.case_participants:
            print(f"Участник {inn} уже есть в деле")
        else:
            self.case_participants.append(inn)

    # Удалить участника
    def remove_participant(self, inn: str):
        if inn in self.case_participants:
            self.case_participants.remove(inn)
            print(f"Участник {inn} удалён из дела")
        else:
            print(f"Участник {inn} не найден в деле")

###

    # Добавить судебное заседание
    def set_a_listening_datetime(self, dt: datetime):
            if not isinstance(dt, datetime):
                raise ValueError("Ожидался объект datetime")
            self.listening_datetimes.append(dt)

    # Вывод времени в чистовом формате
    def get_formatted_datetime(self, fmt: str = "%d.%m.%Y %H:%M") -> list[str]:
        return [dt.strftime(fmt) for dt in self.listening_datetimes]

###

    # Изменить статус решения
    def make_a_decision(self, verdict_text: str):
        if not isinstance(verdict_text, str) or not verdict_text.strip():
            raise ValueError("Текст решения не должен быть пустой строкой")
        self.verdict = verdict_text
        self.is_finished = True
        print(f"Решение вынесено: {self.verdict}")

###

# Для тестов

def assert_raises(exc, fn, *args, **kwargs):
    try:
        fn(*args, **kwargs)
    except exc:
        return True
    else:
        raise AssertionError(f"Ожидалось исключение {exc.__name__}, но его не было")

# 1) Конструктор и дефолты
c1 = CourtCase("А40-12345/2025")
assert c1.case_number == "А40-12345/2025"
assert c1.case_participants == []
assert c1.listening_datetimes == []
assert c1.is_finished is False
assert c1.verdict == ""

# 2) Неверный case_number
assert_raises(ValueError, CourtCase, "   ")
assert_raises(ValueError, CourtCase, None)  # type: ignore

# 3) Добавление участников + защита от дублей
c1.add_participant("7701234567")
c1.add_participant("7701234567")   # дубль не должен добавиться
c1.add_participant("7809876543")
assert c1.case_participants == ["7701234567", "7809876543"]

# 4) Удаление участника (существующий и несуществующий)
c1.remove_participant("7701234567")
assert c1.case_participants == ["7809876543"]
c1.remove_participant("0000000000")  # просто сообщение, список не меняется
assert c1.case_participants == ["7809876543"]

# 5) Заседания: корректный тип и формат
d1 = datetime(2025, 9, 20, 10, 30)
d2 = datetime(2025, 10, 1, 14, 0)
c1.set_a_listening_datetime(d1)
c1.set_a_listening_datetime(d2)
assert c1.listening_datetimes == [d1, d2]
assert c1.get_formatted_datetime() == ["20.09.2025 10:30", "01.10.2025 14:00"]

# 6) Заседания: неверный тип должен падать
assert_raises(ValueError, c1.set_a_listening_datetime, "2025-09-20 10:30")

# 7) Решение по делу
c1.make_a_decision("Иск удовлетворён частично")
assert c1.is_finished is True
assert c1.verdict == "Иск удовлетворён частично"

# 8) Отсутствие «общих» списков между экземплярами
c2 = CourtCase("А40-99999/2025")
c2.add_participant("1234567890")
c2.set_a_listening_datetime(datetime(2025, 12, 31, 23, 59))
assert c1.case_participants != c2.case_participants
assert c1.listening_datetimes != c2.listening_datetimes

print("Все тесты пройдены ✔")