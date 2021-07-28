import re

from bs4 import BeautifulSoup
from selenium import webdriver

URL_HH = '''https://hh.ru/search/vacancy?area=1&fromSearchLine
=true&st=searchVacancy&text=Python+junior&from=suggest_post'''


def get_page(url):
    """Получаем HTML одной страницы с указанного url"""
    try:
        browser = init_browser()
        browser.get(url)
        required_html = browser.page_source
        browser.quit()
        return required_html

    except Exception as e:
        raise Exception(
            f'Не удалось получить данные: {e}')


def get_vacancies(url):
    """Получаем HTML с нескольких страниц с указанного url
и парсим возвращаем вакансии"""
    try:
        browser = init_browser()
        browser.get(url)
        required_html = browser.page_source
        vacancies = parse_vacancies(required_html)
        next_page = get_next_page_or_none(required_html)

        if next_page is not None:
            next_page = 'https:/hh.ru' + next_page
            loop_breaker = 20
            while True:
                loop_breaker -= 1
                if loop_breaker <= 0:
                    break
                browser.get(next_page)
                new_required_html = browser.page_source
                vacancies = {**vacancies, **parse_vacancies(new_required_html)}
                next_page = get_next_page_or_none(new_required_html)
                if next_page is not None:
                    next_page = 'https:/hh.ru' + next_page
                else:
                    break

        browser.quit()
        return vacancies

    except Exception as e:
        raise Exception(
            f'Не удалось получить данные: {e}')


def init_browser():
    """Настраиваем и запускаем браузер"""
    options = webdriver.ChromeOptions()
    options.add_argument('headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    return webdriver.Chrome(chrome_options=options)


def get_next_page_or_none(required_html):
    """Получаем ссылку на следующую страницу или None"""
    try:
        data = BeautifulSoup(required_html, features='html.parser')
        next_page = data.find('a', {"data-qa": "pager-next"})
        if next_page is None:
            return None
        return next_page.get('href')

    except Exception as e:
        raise Exception(
            f'Не удалось получить следующую страницу: {e}')


def parse_vacancies(raw_text):
    """Парсим вакансии"""
    try:
        data = BeautifulSoup(raw_text, features='html.parser')
        vacancies = data.find_all('div', class_='vacancy-serp-item')
        all_vacancies = {}
        for vacancy in vacancies:
            vacancy_name = vacancy.find('a', class_='bloko-link')
            if vacancy_name is not None:
                vacancy_name = vacancy_name.text
            else:
                vacancy_name = None

            vacancy_salary = vacancy.find('span', {"data-qa": "vacancy-serp__vacancy-compensation"})
            if vacancy_salary is not None:
                vacancy_salary = vacancy_salary.text
                vacancy_salary = vacancy_salary.replace('\u202f', '')
            else:
                vacancy_salary = None

            vacancy_employer = vacancy.find('a', {"data-qa": "vacancy-serp__vacancy-employer"})
            if vacancy_employer is not None:
                vacancy_employer = vacancy_employer.text
                vacancy_employer = vacancy_employer.replace('\xa0', ' ')
            else:
                vacancy_employer = None

            vacancy_responsibility = vacancy.find('div', {"data-qa": "vacancy-serp__vacancy_snippet_responsibility"})
            if vacancy_responsibility is not None:
                vacancy_responsibility = vacancy_responsibility.text
            else:
                vacancy_responsibility = None

            vacancy_requirement = vacancy.find('div', {"data-qa": "vacancy-serp__vacancy_snippet_requirement"})
            if vacancy_requirement is not None:
                vacancy_requirement = vacancy_requirement.text
            else:
                vacancy_requirement = None

            vacancy_date = vacancy.find('span',
                                        class_='vacancy-serp-item__publication-date vacancy-serp-item__publication-date_short').text

            vacancy_id = vacancy.find('a',
                                      class_='bloko-button bloko-button_primary bloko-button_small bloko-button_rounded').get('href')
            vacancy_id = int(re.sub(r'\D*', '', vacancy_id))

            vacancy_link = f'https://hh.ru/vacancy/{vacancy_id}'

            all_vacancies[vacancy_id] = {
                'Название': str(vacancy_name),
                'Зарплата': str(vacancy_salary),
                'Дата': str(vacancy_date),
                'Работодатель': str(vacancy_employer),
                'Обязанности': str(vacancy_responsibility),
                'Требования': str(vacancy_requirement),
                'Cсылка': str(vacancy_link)
            }
        return all_vacancies

    except Exception as e:
        raise Exception(
            f'Не удалось распарсить вакансии: {e}')


if __name__ == '__main__':
    # html = get_page(URL_HH)
    # vacancies = parse_vacancies(html)
    vacancies = get_vacancies(URL_HH)
    print(len(vacancies))
