import argparse
import asyncio
import pathlib
import os
import logging
import aiohttp
import requests
from lxml import etree
from bs4 import BeautifulSoup
import aiohttp.client_exceptions as aio_cl_err


DOCUMENT_ROOT = 'saved_article'
URL = 'https://news.ycombinator.com/'
TIMEOUT = 10
HANDLE_INTERVAL = 1
CHECK_INTERVAL = 120
MAX_RATE = 30



class FetchTask:
    """
    Класс для загрузки данных со страницы
    и сохранения их в указанной директории
    (под каждую страницу создается объект данного класса)
    """
    def __init__(self, id_link, result_dir):
        self.id = id_link[0]
        self.url = id_link[1]
        self.result_dir = result_dir

    def save(self, data, name):
        """
        Метод сохранения спарсенных данных

        :param data: данные для сохранения
        :param name: имя файла
        """
        try:
            os.makedirs(self.result_dir+'/'+self.id, exist_ok=True)
            with open(self.result_dir+'/'+self.id+'/'+name+'.html', 'wb') as file:
                file.write(data)
        except OSError:
            logging.error('Can\'t save file')

    def get_name(self):
        """
        :return: имя файла для сохранения данных со страницы
        """
        return self.url.strip('/').split('/')[-1]

    async def perform(self):
        """
        Метод для асинхронного получения данных с указанной страницы

        """
        logging.debug('downloading url: {}'.format(self.url))
        async with aiohttp.ClientSession() as session:
            try:
                async with session.get(self.url) as resp:
                    data = await resp.read()
                    name = self.get_name()
                    await asyncio.get_running_loop().run_in_executor(
                        None, self.save, data, name)
            except (aio_cl_err.ClientConnectorError, aio_cl_err.InvalidURL):
                logging.error('Can\'t parse link: {}'.format(self.url))


class Pool:
    """
    Класс, предназначенный для управления количеством запросов к ресурсу
    за еденицу времени (решение использовать данный класс пришло в связи
    с тем, что бывают ресурсы, которые ограничивают кол-во однотипных запросов,
    а данный класс позволит избежать данных блокировок без применения Selenium)
    """
    def __init__(self, max_rate, interval=HANDLE_INTERVAL):
        self.max_rate = max_rate # максимальное количество запросов
        self.interval = interval # интервал запросов
        self.is_running = False # флаг работы
        self.queue = asyncio.Queue() # очередь задач на выполнение
        self._scheduler_task = None # для корректного завершения работы
        self._sem = asyncio.Semaphore(max_rate)
        self._cuncurrent_workers = 0
        self._stop_event = asyncio.Event()

    async def _worker(self, task):
        async with self._sem:
            self._cuncurrent_workers += 1
            await task.perform()
            self.queue.task_done()
        self._cuncurrent_workers -= 1
        print(self._cuncurrent_workers)
        if not self.is_running and self._cuncurrent_workers == 0:
            self._stop_event.set()

    async def _scheduler(self):
        """
        планировщик scheduler, который работает постоянно,
        просыпается раз в объявленный интервал, достает из
        очереди max_rate задач и запускает их исполнение
        """
        while self.is_running:
            for _ in range(self.max_rate):
                async with self._sem:
                    task = await self.queue.get()
                    asyncio.create_task(self._worker(task))
            await asyncio.sleep(self.interval)

    def start(self):
        # Запускает задачи
        self.is_running = True
        self._scheduler_task = asyncio.create_task(self._scheduler())

    async def stop(self):
        # Останавливает работу
        self.is_running = False
        self._scheduler_task.cancel()
        if self._cuncurrent_workers != 0:
            await self._stop_event.wait()


def get_article_urls(last_news):
    """
    Функция получения ссылок на "свежие" новости

    :param last_news: id последней скачанной новости
    :return: data list of tuple, состоящих из id и url новости
            last_id - id последней скачанной новости
    """
    resp = requests.get(URL)
    data =  resp.text
    soup = BeautifulSoup(data, "html.parser")
    all_news = (news.a['href'] if 'item?' not in news.a['href'] else ''
                for news in soup.findAll('span', class_='titleline'))
    id_news = (news['id'] for news in soup.findAll('tr', class_='athing'))
    data = []
    for id_news, link in zip(id_news, all_news):
        if id_news == last_news:
            break
        data.append((id_news, link))
    last_id = data[0][0] if data else last_news
    logging.info('Handle main page: {} new articles'.format(len(data)))
    return data, last_id


async def pump_over_links(news_id):
    """
    Функция получения ссылок из комментариев новости

    :param id: id новости
    :return: list of ссылок из комментариев
    """
    url = URL+'/item?id='+news_id
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            logging.debug('Pump over comments for {}'.format(url))
            data = await resp.text()
            root = etree.HTML(data)
            all_href = [(news_id, href.get('href')) for href in root.xpath('//div[@class="comment"]//a[@rel="nofollow"]')]
            return all_href


async def start(pool, result_dir, interval):
    """
    Функция запуска краулера

    :param pool: объект класса Pool
            (сущность умеет управлять количеством запросов в единицу времени)
    :param result_dir: апка для хранения данных
    :param interval: Интервал запуска обкачки страниц
    :return:
    """
    last_id = 0
    while True:
        pool.start()
        # получаем url статей с основной страницы
        links, last_id = get_article_urls(last_id)
        for link in links:
            # кладем в очередь обкачки каждую статью
            await pool.queue.put(FetchTask(link, result_dir))
            # получаем url из комментариев на комментарии
            sub_links = await pump_over_links(link[0])
            for sub_link in sub_links:
                # кладем в очередь обкачки каждую ссылку из комментария
                await pool.queue.put(FetchTask(sub_link, result_dir))
        await pool.queue.join()
        await pool.stop()
        # ждем установленное время для начала след итерации обкачки сайта
        await asyncio.sleep(interval)


def main(result_dir, interval, rate):
    """
    Основная функция запуска цикла событий

    :param result_dir: Папка для хранения данных
    :param interval: Интервал запуска обкачки страниц
    :param rate: Максимальное кол-во запросов в (HANDLE_INTERVAL сек) для предотвращения блокировок
    """
    loop = asyncio.get_event_loop()
    pool = Pool(rate)
    try:
        logging.info('Crawler started')
        loop.run_until_complete(start(pool, result_dir, interval))
    # Обработка принудительной остановки краулера
    except KeyboardInterrupt:
        logging.info('Crawler stopped')
        loop.run_until_complete(pool.stop())
        loop.close()


def parse_arguments():
    """
    Функция парсинга аргументов

    :return: argparse.Namespace: Program arguments
    """
    parser = argparse.ArgumentParser(
        description='Async crawler for news.ycombinator.com (YCrawler)'
    )
    parser.add_argument('-o', '--output',  default=DOCUMENT_ROOT)
    parser.add_argument('-i', '--interval', default=CHECK_INTERVAL)
    parser.add_argument('-d', '--debug', action='store_true')
    parser.add_argument('-r', '--rate', default=MAX_RATE)
    return parser.parse_args()


if __name__ == '__main__':
    args = parse_arguments()
    # Создаем папку для хранения страниц
    result_dir = str(pathlib.Path(args.output))
    os.makedirs(result_dir, exist_ok=True)
    # Настраиваем логгирование
    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='[%(asctime)s] %(levelname).1s %(message)s',
                        datefmt='%Y-%m-%d %H:%M:%S')
    main(result_dir, args.interval, args.rate)
