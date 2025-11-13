import json
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, EmailStr, Field, validator
from datetime import date
import re
from pathlib import Path


app = FastAPI(title="Сервис обращений абонентов")


class SubscriberRequest(BaseModel):
    фамилия: str = Field(..., description="Фамилия (с заглавной буквы, кириллица)")
    имя: str = Field(..., description="Имя (с заглавной буквы, кириллица)")
    дата_рождения: date
    номер_телефона: str = Field(..., description="Номер телефона в формате +7XXXXXXXXXX")
    email: EmailStr

    # --- Валидации ---
    @validator("фамилия", "имя")
    def check_cyrillic(cls, value):
        if not re.match(r"^[А-ЯЁ][а-яё]+$", value):
            raise ValueError("Должно начинаться с заглавной буквы и содержать только кириллицу.")
        return value

    @validator("номер_телефона")
    def check_phone(cls, value):
        if not re.match(r"^\+7\d{10}$", value):
            raise ValueError("Номер телефона должен быть в формате +7XXXXXXXXXX")
        return value


@app.post("/create_request")
async def create_request(data: SubscriberRequest):
    """Сохранение обращения в JSON"""
    output_dir = Path("requests")
    output_dir.mkdir(exist_ok=True)
    file_path = output_dir / f"{data.фамилия}_{data.имя}.json"

    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(data.model_dump(), f, ensure_ascii=False, indent=4, default=str)

    return {"status": "ok", "message": "Данные успешно сохранены", "file": str(file_path)}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
