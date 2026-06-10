from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.domain import User, Event


async def get_recommended_events(
    db: AsyncSession,
    user_id: int
):
    # Obtener usuario
    result = await db.execute(
        select(User).where(User.id == user_id)
    )

    user = result.scalar_one_or_none()

    if not user:
        return []

    intereses = user.interests or []

    # Obtener todos los eventos
    result = await db.execute(
        select(Event)
    )

    eventos = result.scalars().all()

    recomendaciones = []

    for evento in eventos:

        score = 0

        for interes in intereses:

            if interes.lower() in evento.category.lower():
                score += 5

            for tag in (evento.tags or []):
                if interes.lower() == tag.lower():
                    score += 10

        recomendaciones.append({
            "evento": evento,
            "score": score
        })

    recomendaciones.sort(
        key=lambda x: x["score"],
        reverse=True
    )

    recomendaciones = [
    r for r in recomendaciones
    if r["score"] > 0
    ]
    return [r["evento"] for r in recomendaciones]