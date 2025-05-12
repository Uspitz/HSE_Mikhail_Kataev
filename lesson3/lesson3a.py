import json
from pathlib import Path
from datetime import datetime

# Путь к исходному файлу
ics_path = Path("А40-183194-2015.ics")

# Считываем содержимое файла
with open(ics_path, "r", encoding="utf-8") as file:
    lines = file.readlines()

# Группируем строки в блоки VEVENT
blocks = []
current_block = []
inside_event = False

for line in lines:
    if line.strip() == "BEGIN:VEVENT":
        inside_event = True
        current_block = [line]
    elif line.strip() == "END:VEVENT":
        current_block.append(line)
        blocks.append(current_block)
        inside_event = False
    elif inside_event:
        current_block.append(line)

# Функция парсинга блока VEVENT
def parse_block(block_lines):
    data = {
        "DTSTART": "",
        "DTEND": "",
        "LOCATION": "",
        "DESCRIPTION": ""
    }
    desc_lines = []
    is_desc = False

    for line in block_lines:
        if line.startswith("DTSTART"):
            data["DTSTART"] = line.split(":")[-1].strip()
        elif line.startswith("DTEND"):
            data["DTEND"] = line.split(":")[-1].strip()
        elif line.startswith("LOCATION"):
            data["LOCATION"] = line.split(":", 1)[-1].strip()
        elif line.startswith("DESCRIPTION"):
            desc_lines = [line.split(":", 1)[-1].strip()]
            is_desc = True
        elif is_desc and (line.startswith(" ") or line.startswith("\t")):
            desc_lines.append(line.strip())
        else:
            is_desc = False

    data["DESCRIPTION"] = " ".join(desc_lines)
    return data

# Фильтруем и собираем данные о реальных заседаниях
court_sessions = []
for block in blocks:
    event = parse_block(block)
    if event["DTSTART"][:8] != "00010101" and event["LOCATION"]:
        session = {
            "case_number": "А40-183194/2015",
            "start": datetime.strptime(event["DTSTART"], "%Y%m%dT%H%M%S").isoformat(),
            "end": datetime.strptime(event["DTEND"], "%Y%m%dT%H%M%S").isoformat(),
            "location": event["LOCATION"],
            "description": event["DESCRIPTION"]
        }
        court_sessions.append(session)

# Сохраняем результат в JSON
output_path = Path("court_dates.json")
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(court_sessions, f, ensure_ascii=False, indent=2)

print(f"Сохранено {len(court_sessions)} заседаний в файл '{output_path}'")