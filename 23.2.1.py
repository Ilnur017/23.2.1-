# coding: utf-8
import requests
from bs4 import BeautifulSoup
import pandas as pd


def collect_user_rates(user_login):
    page_num = 1
    data = []

    while True:
        url = f'https://www.kinopoisk.ru/user/{user_login}/votes/?page={page_num}'  # Обновляем URL для постраничного парсинга
        print(f"Запрос к URL: {url}")  # Отладочный вывод
        html_content = requests.get(url).text
        soup = BeautifulSoup(html_content, 'lxml')
        entries = soup.find_all('div', class_='item')

        if len(entries) == 0:  # Признак остановки
            print("Записи не найдены, завершаем сбор данных.")
            break

        for entry in entries:
            div_film_name = entry.find('div', class_='nameRus')
            film_name = div_film_name.find('a').text.strip() if div_film_name else "Неизвестно"

            my_rating_div = entry.find('div', class_="vote")
            my_rating = my_rating_div.text.strip() if my_rating_div else "Элемент не найден"

            data.append({
                'film_name': film_name,
                'my_rating': my_rating
            })

        print(f"Записей на странице {page_num}: {len(entries)}")  # Отладочный вывод
        page_num += 1  # Переходим на следующую страницу

    return data


def get_rated_films(user_rates, min_rating=8):
    rated_films = []
    for item in user_rates:
        try:
            my_rating = float(item['my_rating'])  # Преобразуем строку в число с плавающей точкой
            if my_rating >= min_rating:
                rated_films.append(item)
        except ValueError:
            print(f"Ошибка преобразования рейтинга: {item['my_rating']}")
            continue  # Пропускаем, если преобразование не удалось
    return rated_films


# Основная часть программы
if __name__ == "__main__":
    user_login = input("Введите данные (ID пользователя): ")  # Запрашиваем ID пользователя
    user_rates = collect_user_rates(user_login)

    print(f"Всего оценок: {len(user_rates)}")

    # Сохранение всех оценок в Excel
    if user_rates:
        df = pd.DataFrame(user_rates)
        df.to_excel('user_rates_all.xlsx', index=False)
        print("Файл 'user_rates_all.xlsx' успешно создан.")
    else:
        print("Нет данных для сохранения в файл 'user_rates_all.xlsx'.")

    # Получаем фильмы с рейтингом 8 и выше
    user_rates_ = get_rated_films(user_rates)
    print(f"Фильмов с рейтингом 8 и выше: {len(user_rates_)}")

    # Сохранение отфильтрованных оценок в другой файл Excel
    if user_rates_:
        df_filtered = pd.DataFrame(user_rates_)
        df_filtered.to_excel('user_rates_filtered.xlsx', index=False)
        print("Файл 'user_rates_filtered.xlsx' успешно создан.")
    else:
        print("Нет данных для сохранения в файл 'user_rates_filtered.xlsx'.")
