
from src.books.schemas import Book,BookUpdateModel
from src.books.book_data import books
from fastapi import APIRouter,status
from fastapi.exceptions import HTTPException


book_router = APIRouter()




book_router.get("/",response_model=list[Book])
async def read_all_books():
    return books

book_router.post("/",status_code=status.HTTP_201_CREATED)
async def create_a_books(book_data: Book) -> dict:
    new_book = book_data.model_dump()
    books.append(new_book)
    return new_book

book_router.get("/{book_id}")
async def get_book(book_id: int) -> dict:
    for book in books:
        if book["id"] == book_id:
            return book
    raise HTTPException(status_code=404, detail="Book not found")

book_router.patch("/{book_id}")
async def update_book(book_id: int, book_update: BookUpdateModel) -> dict:
    
    for book in books:
        if book["id"] == book_id:
            book["title"] = book_update.title
            book["author"] = book_update.author
            book["publisher"] = book_update.publisher
            book["page_count"] = book_update.page_count
            book["language"] = book_update.language

            return book
    raise HTTPException(status_code=404, detail="Book not found")

book_router.delete("/books/{book_id}",status_code=status.HTTP_204_NO_CONTENT)
async def delete_book(book_id: int):
    for book in books:
        if book["id"] == book_id:
            books.remove(book)

    return {}
            
    raise HTTPException(status_code=404, detail="Book not found")