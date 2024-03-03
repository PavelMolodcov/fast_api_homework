from typing import Annotated

from fastapi import APIRouter, Depends, status, Response
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import joinedload

from src.configurations.database import get_async_session
from src.models.sellers import Seller
from src.schemas import IncomingSeller, ReturnedSeller, ReturnedAllSellers, ReturnedSellerWithBooks

sellers_router = APIRouter(tags=["sellers"], prefix="/sellers")

# Больше не симулируем хранилище данных. Подключаемся к реальному, через сессию.
DBSession = Annotated[AsyncSession, Depends(get_async_session)]

# Добавляем продавца
@sellers_router.post("/", response_model=ReturnedSeller, status_code=status.HTTP_201_CREATED)  # Прописываем модель ответа
async def create_seller(
    seller: IncomingSeller, session: DBSession
):  

    
    new_seller = Seller(
        first_name=seller.first_name,
        last_name=seller.last_name,
        email=seller.email,
        password=seller.password.get_secret_value(),
        )
    session.add(new_seller)
    await session.flush()

    return new_seller

# Возвращаем список всех продавцов
@sellers_router.get("/", response_model=ReturnedAllSellers)
async def get_all_sellers(session: DBSession):

    query = select(Seller.id, Seller.first_name, Seller.last_name, Seller.email)
    res = await session.execute(query)
    sellers = res.all()
    
    return {"sellers": sellers}

# Ручка для получения продавца с его книгами по ИД
@sellers_router.get("/{seller_id}", response_model=ReturnedSellerWithBooks)
async def get_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == seller_id)
    res = await session.execute(query)
    seller = res.scalars().first()
    return seller

# Обновление данных о продавце
@sellers_router.put("/{seller_id}")
async def update_seller(seller_id: int, new_data: ReturnedSeller, session: DBSession):
    # Оператор "морж", позволяющий одновременно и присвоить значение и проверить его.
    if updated_seller := await session.get(Seller, seller_id):
        updated_seller.first_name = new_data.first_name
        updated_seller.last_name = new_data.last_name
        updated_seller.email = new_data.email
        
        

        await session.flush()

        return updated_seller

    return Response(status_code=status.HTTP_404_NOT_FOUND)


@sellers_router.delete("/{seller_id}")
async def delete_seller(seller_id: int, session: DBSession):
    query = select(Seller).options(joinedload(Seller.books)).filter(Seller.id == seller_id)
    res = await session.execute(query)
    seller = res.scalars().first()
    
    # Удаление всех связанных книг продавца
    for book in seller.books:
        await session.delete(book)
    
    # Удаление самого продавца
    await session.delete(seller)
    
    return Response(status_code=status.HTTP_204_NO_CONTENT) 