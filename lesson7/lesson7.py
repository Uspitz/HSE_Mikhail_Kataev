from __future__ import annotations

from dataclasses import dataclass
from datetime import date as Date, datetime
from decimal import Decimal, InvalidOperation, getcontext
from pathlib import Path
from typing import Dict, Iterable, Optional
import json
import time
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET


getcontext().prec = 16  # точность для Decimal


@dataclass
class ParserConfig:
    """
    Конфигурация парсера ЦБ РФ.

    :param target_date: Дата, за которую нужно получить курсы (по умолчанию — сегодня).
    :param currency_filter: Набор кодов валют (ISO 4217, напр. {"USD","EUR"}) для фильтрации.
                            Если None/пусто — берём все валюты из файла.
    :param workdir: Рабочая директория, куда сохранять сырой XML и результат.
    :param save_parsed_json: Сохранять ли итоговый словарь в JSON.
    :param retries: Кол-во попыток при скачивании.
    :param retry_delay_sec: Пауза между попытками.
    """
    target_date: Optional[Date] = None
    currency_filter: Optional[Iterable[str]] = None
    workdir: Path | str = Path("./data")
    save_parsed_json: bool = True
    retries: int = 3
    retry_delay_sec: float = 1.5


class ParserCBRF:
    """
    Парсер ЦБ РФ: скачивает XML ежедневных курсов и парсит его.

    Публичный интерфейс только один — start().

    Структура хранения:
        {
            "YYYY-MM-DD": {
                "USD": Decimal("##.####"),
                "EUR": Decimal("##.####"),
                ...
            }
        }

    Номинал из XML учитывается: курс приводится к значению "за 1 единицу" (делим на Nominal).
    """

    def __init__(self, config: Optional[ParserConfig] = None) -> None:
        self._cfg = config or ParserConfig()
        if self._cfg.target_date is None:
            self._cfg.target_date = Date.today()

        # Нормализуем фильтр валют к сету в верхнем регистре
        self._currency_filter = (
            set(code.upper() for code in self._cfg.currency_filter)
            if self._cfg.currency_filter
            else None
        )

        self._workdir = Path(self._cfg.workdir)
        self._workdir.mkdir(parents=True, exist_ok=True)

    # ---------------------------
    #        ПУБЛИЧНЫЙ API
    # ---------------------------
    def start(self) -> Dict[str, Dict[str, Decimal]]:
        """
        Запускает полный цикл: скачать XML, распарсить, сохранить результат при необходимости.
        Возвращает словарь вида {"YYYY-MM-DD": {"USD": Decimal(...), ...}}.
        """
        url = self._build_xml_daily_url(self._cfg.target_date)
        xml_path = self._download_file(url, self._xml_filename(self._cfg.target_date))
        data = self._parse_xml_daily(xml_path)

        if self._cfg.save_parsed_json:
            self._save_json(
                data,
                self._workdir / f"parsed_fx_{self._cfg.target_date.isoformat()}.json",
            )

        return data

    # ---------------------------
    #      ПРИВАТНЫЕ МЕТОДЫ
    # ---------------------------
    def _build_xml_daily_url(self, d: Date) -> str:
        """
        Собирает ссылку вида:
        https://www.cbr.ru/scripts/XML_daily.asp?date_req=DD/MM/YYYY
        """
        # ЦБ принимает русскую дату в формате ДД/ММ/ГГГГ
        ddmmyyyy = d.strftime("%d/%m/%Y")
        query = urllib.parse.urlencode({"date_req": ddmmyyyy})
        return f"https://www.cbr.ru/scripts/XML_daily.asp?{query}"

    def _xml_filename(self, d: Date) -> Path:
        """
        Имя файла для сохранения исходного XML.
        """
        return self._workdir / f"cbrf_{d.isoformat()}.xml"

    def _download_file(self, url: str, dst_path: Path) -> Path:
        """
        Скачивает файл по URL в dst_path с повторными попытками.
        """
        last_err: Optional[Exception] = None
        for attempt in range(1, self._cfg.retries + 1):
            try:
                req = urllib.request.Request(
                    url,
                    headers={
                        # простой User-Agent, чтобы не споткнуться о защиту от ботов
                        "User-Agent": "Mozilla/5.0 (compatible; ParserCBRF/1.0)"
                    },
                )
                with urllib.request.urlopen(req, timeout=20) as resp:
                    content = resp.read()
                dst_path.write_bytes(content)
                return dst_path
            except Exception as e:
                last_err = e
                if attempt < self._cfg.retries:
                    time.sleep(self._cfg.retry_delay_sec)
        # если все попытки провалились — поднимаем последнюю ошибку
        assert last_err is not None
        raise last_err

    def _parse_xml_daily(self, xml_path: Path) -> Dict[str, Dict[str, Decimal]]:
        """
        Разбирает XML ежедневных курсов и возвращает структуру хранения.
        Пример XML: <ValCurs Date="02.10.2025" name="Foreign Currency Market">
                        <Valute ID="R01235">
                          <NumCode>840</NumCode>
                          <CharCode>USD</CharCode>
                          <Nominal>1</Nominal>
                          <Name>Доллар США</Name>
                          <Value>101,2345</Value>
                        </Valute>
                        ...
                    </ValCurs>
        """
        tree = ET.parse(xml_path)
        root = tree.getroot()

        xml_date_attr = root.attrib.get("Date")  # формат ДД.ММ.ГГГГ
        if not xml_date_attr:
            # на всякий случай берём дату из конфигурации
            d_iso = self._cfg.target_date.isoformat()
        else:
            d_iso = self._convert_dd_mm_yyyy_to_iso(xml_date_attr)

        out: Dict[str, Dict[str, Decimal]] = {d_iso: {}}
        for valute in root.findall("Valute"):
            char_code_el = valute.find("CharCode")
            nominal_el = valute.find("Nominal")
            value_el = valute.find("Value")
            if char_code_el is None or nominal_el is None or value_el is None:
                continue

            code = (char_code_el.text or "").strip().upper()
            if self._currency_filter and code not in self._currency_filter:
                continue

            nominal = self._safe_int(nominal_el.text)
            value_dec = self._safe_decimal(value_el.text)

            if nominal is None or value_dec is None or nominal == 0:
                continue

            # приводим курс к "за 1 единицу"
            per_unit = (value_dec / Decimal(nominal)).quantize(Decimal("0.0001"))
            out[d_iso][code] = per_unit

        return out

    def _save_json(self, data: Dict[str, Dict[str, Decimal]], path: Path) -> None:
        """
        Сохраняет словарь в JSON (Decimal сериализуем в строку).
        """
        def default(o):
            if isinstance(o, Decimal):
                return str(o)
            if isinstance(o, (datetime,)):
                return o.isoformat()
            raise TypeError(f"Unserializable type: {type(o)}")

        path.write_text(json.dumps(data, ensure_ascii=False, indent=2, default=default), encoding="utf-8")

    # ---------- вспомогательные приватные ----------
    def _convert_dd_mm_yyyy_to_iso(self, s: str) -> str:
        # '02.10.2025' -> '2025-10-02'
        try:
            return datetime.strptime(s, "%d.%m.%Y").date().isoformat()
        except Exception:
            # fallback — дата из конфигурации
            return self._cfg.target_date.isoformat()

    def _safe_decimal(self, raw: Optional[str]) -> Optional[Decimal]:
        if raw is None:
            return None
        # В XML ЦБ десятичный разделитель — запятая
        sanitized = raw.replace("\u00A0", "").replace(" ", "").replace(",", ".").strip()
        try:
            return Decimal(sanitized)
        except (InvalidOperation, ValueError):
            return None

    def _safe_int(self, raw: Optional[str]) -> Optional[int]:
        if raw is None:
            return None
        try:
            return int(raw.strip())
        except ValueError:
            return None


# ---------------------------
# Пример использования
# ---------------------------
if __name__ == "__main__":
    # Пример: берём USD и EUR за конкретную дату, сохраняем файлы в ./data
    cfg = ParserConfig(
        target_date=Date(2025, 10, 1),
        currency_filter={"USD", "EUR"},
        workdir=Path("./data"),
        save_parsed_json=True,
    )
    parser = ParserCBRF(cfg)
    result = parser.start()
    print(result)