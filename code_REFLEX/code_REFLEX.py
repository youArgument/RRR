from rxconfig import config
import reflex as rx
from .models import FilmLike,FilmDisLike,User
from sqlalchemy import text
import random
filename = f"{config.app_name}/{config.app_name}.py"




class FilmState(rx.State):
    pass

class FilmRequest(FilmState):
    
    _film_id: str = ""   
    username:str = ""
    userpassword: str = ""
    
    @rx.var
    def get_user_name(self):
        
        
        user = 'you_argument'
        return user
    
    def on_mount(self):
            self.username = self.get_user_name
            userid = {'userid': f'{self.username}'}
            
            with rx.session() as s: 
                select = text("select filmid FROM films AS f WHERE f.filmid NOT IN(select filmid FROM filmlike WHERE username =:userid) AND f.filmid NOT IN(select filmid FROM filmdislike WHERE username =:userid) ORDER BY RANDOM() LIMIT 1")
                try:
                    film = s.execute(select,userid).fetchone()
                    
                    self._film_id = film[0]
                    print(self._film_id)
                except:
                    print("НЕТ ФИЛЬМОВ")
                    self._film_id = 'sm1613230'
                
    @rx.var
    def get_film_name(self):
        
        filmid = {'film': f'{self._film_id}'}
        with rx.session() as s:
            
            select = text("select title FROM films WHERE filmid =:film")
            try:
                name = s.execute(select,filmid).fetchone()
                film_name = name[0]
                return film_name
            except:
                return "Название"
    
    @rx.var
    def get_film_descr(self):
        
        filmid = {'film': f'{self._film_id}'}
        with rx.session() as s:
            
            select = text("select description FROM films WHERE filmid =:film")
            try:
                descr = s.execute(select,filmid).fetchone()
                film_descr = descr[0]
                return film_descr
            except:
                return "Описание"
    
    @rx.var
    def get_film_poster(self):
        
        filmid = {'film': f'{self._film_id}'}
        with rx.session() as s:
            
            select = text("select img FROM films WHERE filmid =:film")
            try:
                img = s.execute(select,filmid).fetchone()
                film_img = img[0]
                return f'/image/{film_img}'
            except:
                return "Загрузка"

    def like_film(self):
        with rx.session() as s:
            s.add(
                FilmLike(
                    username=self.username, filmid=self._film_id
                )
            )
            s.commit()
            self.on_mount()
            
    def dislike_film(self):
        with rx.session() as s:
            s.add(
                FilmDisLike(
                    username=self.username, filmid=self._film_id
                )
            )
            s.commit()
            self.on_mount()
    
    def loginform(self):
        print(self.username)
        print(self.userpassword)
        
    def registerform(self):
        if self.username:
            print(self.username)    
        else:
            print('ERROR')   
        print(self.userpassword)
    

def home() :
    return rx.container(
        rx.center(
            rx.vstack(
                rx.box(rx.flex(rx.heading("WEESEE·BOT", ))), rx.accordion(
                    rx.accordion_item(
                        rx.accordion_button(
                            rx.center(
                                rx.heading(f'{FilmRequest.get_film_name}'),width="100%",
                            ),
                            rx.accordion_icon(),

                        ),
                        rx.accordion_panel(
                            
                            rx.text(f'{FilmRequest.get_film_descr}', textalign="center")
                        ),
                    ),
                    allow_toggle=True,
                    width="100%",
                ),
                rx.container
                (
                    
                    rx.image(src=f'{FilmRequest.get_film_poster}',border_radius="20px",height="70vh"),

                ),
                rx.flex(rx.button("Like",on_click=FilmRequest.like_film), rx.spacer(), rx.popover(
                    rx.popover_trigger(rx.button("О фильме")),
                    rx.popover_content(
                        rx.grid(
                            rx.grid_item(rx.text("Год производства:")),
                            rx.grid_item(rx.text("2001")),
                            rx.grid_item(rx.text("Страна:")),
                            rx.grid_item(rx.text("Япония")),
                            rx.grid_item(rx.text("Жанр:")),
                            rx.grid_item(
                                rx.text("аниме, мультфильм, фэнтези, приключения, семейный")),
                            rx.grid_item(rx.text("Время:")),
                            rx.grid_item(rx.text("125 мин. / 02:05")),
                            template_columns="repeat(2, 1fr)",
                            h="17em",
                            width="100%",
                            gap=4,
                        ),
                        rx.popover_close_button()
                    ),
                ), rx.spacer(), rx.button("DisLike",on_click=FilmRequest.dislike_film), width="70%"),
                rx.flex(rx.button("Моя коллекция",on_click=FilmRequest.on_mount), rx.spacer(),
                        rx.button(f'{FilmRequest.get_user_name}'), width="60%")
            )
        ),on_mount= FilmRequest.on_mount
        
    )
def sign():
    
    return rx.vstack(rx.script(src="https://telegram.org/js/telegram-web-app.js"),
                     rx.script("""const handle_press = (arg) =>{let tg = window.Telegram.WebApp;
                               window.alert(tg.initDataUnsafe.username)}"""),
                     rx.container(rx.center(rx.vstack(rx.heading(f'Привет ! {FilmRequest.username}'),
                                                      rx.button("Войти",on_click=rx.client_side("handle_press(args)")),height="200px")),
                                  margin="0",position="absolute",top="50%",border="2px solid red"),height="800px",position="relative",border="3px solid green")
# def sign():
    
#     return rx.vstack(rx.heading(f'WEESEE·BOT'),
#         rx.container
#         (
#             rx.center
#             (           
#                 rx.vstack
#                 (
#                     rx.heading(f'Добро пожаловать !'),
#                     rx.input(placeholder="Логин",on_change=FilmRequest.set_username),
#                     rx.input(placeholder="Пароль",on_change=FilmRequest.set_userpassword,type_="password"),
#                     rx.vstack(rx.box(rx.button("Регистрация",on_click=FilmRequest.registerform)),rx.spacer(),rx.box(rx.button("Войти",on_click=FilmRequest.loginform)),width="100%",border="2px solid red",text_align="center"),
#                     # rx.text(,color="RED")
#                 )
#             ),margin="0",position="absolute",top="50%",border="2px solid red"
#         ),height="600px",position="relative",border="3px solid green"
#                     )


# Add state and page to the app.
app = rx.App()

app.add_page(sign,route='/')
app.add_page(home, route='/home')
app.compile()
