import threading
from bs4 import BeautifulSoup
import os
from PIL import Image
import time
import requests
import sqlite3


# Функция для обработки одного фильма
def process_movie(filmurl, filmid, conn):
    cursor = conn.cursor()
    film_data = BeautifulSoup(requests.get(filmurl).content, 'html.parser')
    # # Устанавливаем качество сжатия для больших и маленьких изображений
    high_quality = 10
    low_quality = 70
    if conn is not None:

        cursor.execute("SELECT filmid FROM films WHERE filmid=?", (filmid,))
        film_in_db = cursor.fetchone()
        if film_in_db:
            print(f"Запись с ID: {filmid} уже существует.")
            return
        else:
            print(filmurl)
            print(filmid)


            ##НАЗВАНИЕ ФИЛЬМА
            film_name = film_data.find('div', class_='wrapper_movies_top_main_right').find('h1').text[:-13]

            imdb_data = film_data.find_all(class_='wrapper_movies_scores_score')
            # Пройдемся по найденным элементам и извлечем текст из элемента, содержащего "IMDb"

            film_rat = 0
            for score in imdb_data:
                if 'IMDb' in score.get_text():
                    imdb_score = score.find('div').get_text()  # Извлекаем рейтинг IMDb
                    print(f'{imdb_score} - РЕЙТИНГ IMDB')
                    film_rat = imdb_score

            ##IMdB рейтинг
            film_rat_res = film_rat

            ##Описание фильма
            film_description = film_data.find('div', class_='wrapper_movies_text')

            if film_description:
                new_film_description = film_description.text.strip()
            else:
                new_film_description = "Описание отсутствует"
            ##########################################################################################
            film_img = film_data.find('div',
                                      class_='wrapper_movies_top_main_left').find('a',
                                                                                  class_='wrapper_block_stack '
                                                                                         'wrapper_movies_poster').get(
                'data-src')

            film_img_res = 'https://www.film.ru' + film_img
            allowed_extensions = ['.jpg', '.jpeg', '.png', '.gif']
            file_extension = os.path.splitext(film_img_res)[1]

            new_img = ''
            if file_extension.lower() in allowed_extensions:
                save_folder = 'filmPoster'
                # Создайте папку, если она не существует
                if not os.path.exists(save_folder):
                    os.makedirs(save_folder)
                # Определите имя файла на основе URL (можно улучшить эту логику)
                file_name = os.path.join(save_folder, f"{filmid}_{os.path.basename(film_img_res)}")
                # Загрузите изображение и сохраните его в файл
                response = requests.get(film_img_res, stream=True)

                if response.status_code == 200:
                    # Проверяем размер ответа (в байтах)
                    response_size = int(response.headers.get('Content-Length', 0))
                    if response_size > 13 * 1024 * 1024:  # Если размер больше 13 МБ
                        with open(file_name, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)
                        print(f"Изображение слишком большое в {file_name}")
                        new_img = file_name  # Просто сохраняем путь к скачанному файлу без обработки
                    else:
                        with open(file_name, "wb") as file:
                            for chunk in response.iter_content(chunk_size=8192):
                                file.write(chunk)

                        # Попытайтесь открыть изображение с помощью Pillow (PIL)
                        try:
                            image = Image.open(file_name)
                            if image.mode == 'RGBA':
                                # Создайте новое изображение с режимом RGB и скопируйте данные
                                image = image.convert('RGB')
                            # Устанавливаем желаемый размер (ширину и высоту) для сжатого изображения
                            desired_width = 1920
                            desired_height = 1920
                            # Изменяем размер изображения
                            image.thumbnail((desired_width, desired_height))
                            # Сохраняем сжатое изображение
                            # Определяем размер файла после изменения размера
                            file_size_mb = os.path.getsize(file_name) / (1024 * 1024)  # Размер файла в МБ

                            # Устанавливаем качество сжатия в зависимости от размера файла
                            if file_size_mb > 5:
                                quality = high_quality
                            else:
                                quality = low_quality

                            image.save(file_name, quality=quality)
                            print(f"Изображение сохранено в {file_name}")
                            new_img = file_name
                        except OSError as e:
                            print(f"Ошибка при открытии изображения: {e}")

            else:
                print("Некорректный URL изображения, пропускаем его")

            ##Год и жанры
            film_yar_rat_ganre_elements = film_data.find('div', class_='block_info').find_all('a')

            # ГОД ВЫПУСКА
            if len(film_yar_rat_ganre_elements) > 1:
                film_year = film_yar_rat_ganre_elements[0].get_text()
            else:

                film_year = 'Нет данных'
                print(f'{film_year} - Без даты')
            # ЖАНРЫ ФИЛЬМЫ
            film_genres = []
            film_country = []
            for link in film_yar_rat_ganre_elements[1:]:
                link_data = link.get_text()

                if link_data[0].isupper():
                    print(f'СТРАНА - {link_data}')
                    film_country.append(link_data)
                else:
                    print(f'ЖАНР - {link_data}')
                    film_genres.append(link_data)

            if len(film_genres) == 0:
                f_genres = 'жанр отсутствует'
            else:
                f_genres = film_genres[0]

            for ganre in film_genres:
                cursor.execute("INSERT INTO films_genre (filmid,genres) VALUES (?,?)", (filmid, ganre))

            for country in film_country:
                cursor.execute("INSERT INTO films_country (filmid,country) VALUES (?,?)", (filmid, country))

            cursor.execute("INSERT INTO films_rating (filmid,rating) VALUES (?,?)", (filmid, film_rat_res))
            cursor.execute("INSERT INTO films_year (filmid,year) VALUES (?,?)", (filmid, film_year))

            cursor.execute("INSERT INTO films (filmid, url, title, year, genre, rating, description, img) "
                           "VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                           (filmid, filmurl, film_name, film_year, f_genres, film_rat_res, new_film_description,
                            new_img))

            conn.commit()
            cursor.close()

            print("__________СЛЕДУЮЩИЙ ФИЛЬМ__________")


# Функция для обработки одной страницы
def process_page(page_number):
    url = f"https://www.film.ru/a-z/movies/nojs?page={page_number}"
    response = requests.get(url)

    if response.status_code == 200:
        soup = BeautifulSoup(response.content, "html.parser")
        films = soup.find_all('div', class_='film_list')

        conn = sqlite3.connect('FilmRU.db')
        if conn is not None:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS films (id INTEGER NOT NULL PRIMARY KEY,filmid text, url text, title text,
                year text,genre text,rating text,description text, img text)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS films_year (filmid text, year text)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS films_genre (filmid text ,genres text)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS films_rating (filmid text ,rating text)''')
            cursor.execute('''CREATE TABLE IF NOT EXISTS films_country (filmid text ,country text)''')
            conn.commit()

            for film in films:
                time.sleep(0.8)
                new_url = 'https://www.film.ru' + film.find('a', class_='film_list_link').get('href')
                film_id = film.get('id', None)
                if film_id:
                    process_movie(new_url, film_id, conn)
                else:
                    film_id = new_url[:9]
                    process_movie(new_url, film_id, conn)
                    print('У фильма нет идентификатора')


            cursor.close()
            conn.close()

            print(f"Страница {page_number}: статус код 200")
    else:
        print(f"Страница {page_number}: статус код {response.status_code}")


# Функция для запуска процесса асинхронного обращения к страницам
def start():
    total_pages = 4
    threads_count = 2
    pages_per_thread = total_pages // threads_count

    # Создаем и запускаем потоки
    threads = []
    for i in range(threads_count):
        start_page = i * pages_per_thread
        end_page = (i + 1) * pages_per_thread if i < threads_count - 1 else total_pages
        thread = threading.Thread(target=process_pages_range, args=(start_page, end_page))
        threads.append(thread)
        thread.start()

    # Ожидаем завершения всех потоков
    for thread in threads:
        thread.join()


# Функция для обработки диапазона страниц
def process_pages_range(start_page, end_page):
    for page_number in range(start_page, end_page):
        process_page(page_number)


# Запускаем процесс
start()
