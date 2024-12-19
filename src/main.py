import logging
import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup
import requests_cache
from tqdm import tqdm

from configs import configure_argument_parser, configure_logging
from constants import BASE_DIR, EXPECTED_STATUS, MAIN_DOC_URL, PEP_URL
from exceptions import ParserFindTagException
from outputs import control_output
from utils import find_tag, get_response

counter = {}  # Общий словарь-счетчик


def single_pep_parser(session, pep_link):
    pep_response = get_response(session, pep_link)
    if pep_response is None:
        return
    pep_soup = BeautifulSoup(pep_response.text, features='lxml')
    article = find_tag(
        pep_soup,
        'dl',
        attrs={'class': 'rfc2822 field-list simple'}
    )
    dt_tags = article.find_all('dt')
    for dt_tag in dt_tags:
        if re.search(r'Status:', dt_tag.text) is not None:
            status_from_page = dt_tag.find_next('dd').abbr.text
            if status_from_page not in counter:
                counter[status_from_page] = 0
            counter[status_from_page] += 1
    return status_from_page


def pep(session):
    response = get_response(session, PEP_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    tables = soup.find_all(
        'table',
        attrs={'class': 'pep-zero-table docutils align-default'}
    )
    total_count = 0
    for table in tables:
        tbody_tag = find_tag(table, 'tbody')
        tr_tags = tbody_tag.find_all('tr')
        for tr_tag in tr_tags:
            status_tag = find_tag(tr_tag, 'td')
            pep_link = urljoin(PEP_URL, status_tag.find_next('td').a['href'])
            total_count += 1
            status_from_page = single_pep_parser(session, pep_link)
            try:
                status = find_tag(status_tag, 'abbr').text[1:]
            except ParserFindTagException:
                status = ''
            expected_status = EXPECTED_STATUS[status]
            if status_from_page not in expected_status:
                logging.info(f'Несовпадающий статус: {pep_link}')
                logging.info(
                    f'Ожидаемый статус: {expected_status}. '
                    f'Фактический: {status_from_page}'
                )
    counter['Total'] = total_count
    results = [('Статус', 'Количество')]
    for key in counter:
        results.append(
            (key, counter[key])
        )
    return results


def whats_new(session):
    whats_new_url = urljoin(MAIN_DOC_URL, 'whatsnew/')
    response = get_response(session, whats_new_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_div = find_tag(soup, 'section', attrs={'id': 'what-s-new-in-python'})
    div_with_ul = find_tag(main_div, 'div', attrs={'class': 'toctree-wrapper'})
    sections_by_python = div_with_ul.find_all(
        'li',
        attrs={'class': 'toctree-l1'}
    )
    results = [('Ссылка на статью', 'Заголовок', 'Редактор, автор')]
    for section in tqdm(sections_by_python):
        version_a_tag = find_tag(section, 'a')
        href = version_a_tag['href']
        version_link = urljoin(whats_new_url, href)
        response = get_response(session, version_link)
        if response is None:
            continue
        soup = BeautifulSoup(response.text, features='lxml')
        h1 = soup.find('h1')
        dl = soup.find('dl')
        dl_text = dl.text.replace('\n', ' ')
        results.append(
            (version_link, h1.text, dl_text)
        )
        return results


def latest_versions(session):
    response = get_response(session, MAIN_DOC_URL)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    sidebar = find_tag(soup, 'div', attrs={'class': 'sphinxsidebarwrapper'})
    ul_tags = sidebar.find_all('ul')
    for ul in ul_tags:
        if 'All versions' in ul.text:
            a_tags = ul.find_all('a')
            break
    else:
        raise Exception('Ничего не нашлось')
    results = [['Ссылка на документацию', 'Версия', 'Статус']]
    pattern = r'Python (?P<version>\d\.\d+) \((?P<status>.*)\)'
    for a_tag in a_tags:
        link = a_tag['href']
        search = re.search(pattern, a_tag.text)
        if search is not None:
            version, status = search.groups()
        else:
            version, status = a_tag.text, ''
        results.append(
            (link, version, status)
        )
    return results


def download(session):
    downloads_url = urljoin(MAIN_DOC_URL, 'download.html')
    response = get_response(session, downloads_url)
    if response is None:
        return
    soup = BeautifulSoup(response.text, features='lxml')
    main_tag = find_tag(soup, 'div', {'role': 'main'})
    table_tag = find_tag(main_tag, 'table', {'class': 'docutils'})
    pdf_a4_tag = find_tag(
        table_tag,
        'a',
        {'href': re.compile(r'.+pdf-a4\.zip$')}
    )
    pdf_a4_link = pdf_a4_tag['href']
    archive_url = urljoin(downloads_url, pdf_a4_link)
    filename = archive_url.split('/')[-1]
    downloads_dir = BASE_DIR / 'downloads'
    downloads_dir.mkdir(exist_ok=True)
    archive_path = downloads_dir / filename
    response = session.get(archive_url)
    with open(archive_path, 'wb') as file:
        file.write(response.content)
    logging.info(f'Архив был загружен и сохранён: {archive_path}')


MODE_TO_FUNCTION = {
    'whats-new': whats_new,
    'latest-versions': latest_versions,
    'download': download,
    'pep': pep
}


def main():
    configure_logging()
    logging.info('Парсер запущен!')
    arg_parser = configure_argument_parser(MODE_TO_FUNCTION.keys())
    args = arg_parser.parse_args()
    logging.info(f'Аргументы командной строки: {args}')
    session = requests_cache.CachedSession()
    if args.clear_cache:
        session.cache.clear()
    parser_mode = args.mode
    results = MODE_TO_FUNCTION[parser_mode](session)
    if results is not None:
        control_output(results, args)
        logging.info('Парсер завершил работу.')


if __name__ == '__main__':
    main()
