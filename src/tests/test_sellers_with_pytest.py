import pytest
from fastapi import status
from sqlalchemy import select

from src.models import books
from src.models import sellers


# Тест на ручку создающую продавца
@pytest.mark.asyncio
async def test_create_seller(async_client):

    
    data = {"first_name": "Vasya", "last_name": "Pupkin", "email": "user@gmail.com", "password": "88888888"}
    response = await async_client.post("/api/v1/sellers/", json=data)

    assert response.status_code == status.HTTP_201_CREATED

    result_data = response.json()
    id = result_data["id"] # Не уверен, что так можно, но мы тестируем создание продавца, а не выдачу айдигников БД
    

    assert result_data == {
        "id": id,
        "first_name": "Vasya",
        "last_name": "Pupkin",
        "email": "user@gmail.com",
    }


# Тест на ручку получения списка продавцов
@pytest.mark.asyncio
async def test_get_books(db_session, async_client):



    seller = sellers.Seller(first_name="Vasya", last_name="Pupkin", email="user@gmail.com", password="88888888")
    seller_2 =sellers.Seller(first_name="Kolya", last_name="Popkin", email="user2@gmail.com", password="12345678")

    db_session.add_all([seller, seller_2])
    await db_session.flush()

    response = await async_client.get("/api/v1/sellers/")

    assert response.status_code == status.HTTP_200_OK

    assert len(response.json()["sellers"]) == 2  # Очень забавно, записей в базе больше двух и айдишник присваевается больший, но срабатывает

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        "sellers": [
            {"first_name": "Vasya", "last_name": "Pupkin", "email": "user@gmail.com", "id": seller.id},
            {"first_name": "Kolya", "last_name": "Popkin", "email": "user2@gmail.com", "id": seller_2.id},
        ]
    }


# Тест на ручку получения одного продавца и его книг
@pytest.mark.asyncio
async def test_get_single_seller(db_session, async_client):

    seller = sellers.Seller(first_name = "Vasya", last_name = "Pupkin", email = "user@gmail.com", password = "88888888")
    db_session.add(seller)
    await db_session.flush()

    seller_id = seller.id

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller_id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_id)

    db_session.add_all([book, book_2])
    await db_session.flush()

    response = await async_client.get(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_200_OK
    

    # Проверяем интерфейс ответа, на который у нас есть контракт.
    assert response.json() == {
        'first_name': 'Vasya', 
        'last_name': 'Pupkin', 
        'id': seller_id, 
        'email': 'user@gmail.com', 
        'books': [
            {'title': 'Eugeny Onegin', 
             'author': 'Pushkin', 
             'year': 2001, 'id': book.id, 
             'count_pages': 104}, 
             {'title': 'Mziri', 
              'author': 'Lermontov', 
              'year': 1997, 
              'id': book_2.id, 
              'count_pages': 104
              }
            ]
        }
    

# Тест на ручку удаления продавца
@pytest.mark.asyncio
async def test_delete_sellers(db_session, async_client):

    seller = sellers.Seller(first_name = "Vasya", last_name = "Pupkin", email = "user@gmail.com", password = "88888888")
    db_session.add(seller)
    await db_session.flush()

    seller_id = seller.id

    book = books.Book(author="Pushkin", title="Eugeny Onegin", year=2001, count_pages=104, seller_id=seller.id)
    book_2 = books.Book(author="Lermontov", title="Mziri", year=1997, count_pages=104, seller_id=seller_id)

    db_session.add(book)
    await db_session.flush()

    response = await async_client.delete(f"/api/v1/sellers/{seller_id}")

    assert response.status_code == status.HTTP_204_NO_CONTENT
    await db_session.flush()

    all_sellers = await db_session.execute(select(sellers.Seller))
    res = all_sellers.scalars().all()
    assert len(res) == 0
    # так как мы удаляем и книги
    all_books = await db_session.execute(select(books.Book))
    res = all_books.scalars().all()
    assert len(res) == 0


# Тест на ручку обновления книги
@pytest.mark.asyncio
async def test_update_seller(db_session, async_client):

    seller = sellers.Seller(first_name = "Vasya", last_name = "Pupkin", email = "user@gmail.com", password = "88888888")
    db_session.add(seller)
    await db_session.flush()

    seller_id = seller.id
    


    response = await async_client.put(
        f"/api/v1/sellers/{seller_id}",
        json={"first_name": "Kolya", "last_name": "Popkin", "email": "user2@gmail.com", "id": seller_id},
    )

    assert response.status_code == status.HTTP_200_OK
    await db_session.flush()

    # Проверяем, что обновились все поля
    res = await db_session.get(sellers.Seller, seller_id)
    assert res.first_name == "Kolya"
    assert res.last_name == "Popkin"
    assert res.email == "user2@gmail.com"
    assert res.id == seller_id
