class Plaintiff:
    def __init__(self, name: str, inn: str):
        self.name = name
        self.inn = inn
        self.claims = []
        self.has_representative = False

    def add_claim(self, text: str):
        self.claims.append(text)
        print(f"Истец {self.name} добавил требование: {text}")

    def withdraw_claim(self, text: str):
        if text in self.claims:
            self.claims.remove(text)
            print(f"Истец {self.name} отозвал требование: {text}")
        else:
            print(f"Требование '{text}' не найдено")

    def appoint_representative(self):
        self.has_representative = True
        print(f"Истец {self.name} назначил представителя")

    def remove_representative(self):
        self.has_representative = False
        print(f"Истец {self.name} отказался от представителя")