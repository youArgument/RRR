import reflex as rx
class User(rx.Model, table=True):
    username: str
    email: str
    password: str
    
class Films(rx.Model,table=True):
    filmid:str
    url:str
    title:str
    year:str
    genre:str
    rating:str
    description:str
    img:str
class FilmLike(rx.Model,table=True):
    filmid:str
    username:str
    
class FilmDisLike(rx.Model,table=True):
    filmid:str
    username:str
