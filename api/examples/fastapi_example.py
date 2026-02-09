"""
FastAPI Example - рабочий API для получения данных о GitHub пользователях
Демонстрирует: async/await, HTTP запросы, обработка ошибок, валидация
"""
import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI(title="GitHub Info API", version="1.0.0")


class UserInfo(BaseModel):
    """Информация о пользователе GitHub"""
    login: str
    name: Optional[str] = None
    bio: Optional[str] = None
    public_repos: int
    followers: int
    following: int
    location: Optional[str] = None


@app.get("/")
async def root():
    """Главная страница"""
    return {
        "message": "GitHub Info API",
        "endpoints": {
            "/user/{username}": "Получить информацию о пользователе",
            "/health": "Проверка здоровья сервиса"
        }
    }


@app.get("/health")
async def health_check():
    """Проверка доступности сервиса и внешнего API"""
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                "https://api.github.com",
                timeout=5.0
            )
            github_available = response.status_code == 200
    except Exception:
        github_available = False
    
    return {
        "status": "healthy",
        "github_api_available": github_available
    }


@app.get("/user/{username}", response_model=UserInfo)
async def get_user_info(username: str):
    """
    Получить информацию о пользователе GitHub
    Делает реальный запрос к GitHub API
    """
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"https://api.github.com/users/{username}",
                timeout=10.0
            )
            
            if response.status_code == 404:
                raise HTTPException(
                    status_code=404,
                    detail=f"Пользователь {username} не найден"
                )
            
            response.raise_for_status()
            data = response.json()
            
            return UserInfo(
                login=data.get("login", username),
                name=data.get("name"),
                bio=data.get("bio"),
                public_repos=data.get("public_repos", 0),
                followers=data.get("followers", 0),
                following=data.get("following", 0),
                location=data.get("location")
            )
            
    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=e.response.status_code,
            detail=f"Ошибка GitHub API: {e.response.status_code}"
        )
    except httpx.RequestError as e:
        raise HTTPException(
            status_code=503,
            detail=f"Не удалось подключиться к GitHub API: {str(e)}"
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
