import json
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from time import sleep
from typing import Dict, List, Tuple
import requests
import os

NOME_DO_CANDIDATO = 'Fernando Oliveira Barbosa'
EMAIL_DO_CANDIDATO = 'ofernandobarbosa@gmail.com'

MAIN_FOLDER = Path(__file__).parent.parent


def request_journals(start_date, end_date):
    url = 'https://engine.procedebahia.com.br/publish/api/diaries'

    r = requests.post(url, data={"cod_entity": '50', "start_date": start_date, "end_date": end_date})
    if r.status_code == 200:
        return r.json()
    elif r.status_code == 400:
        sleep(10)
        return request_journals(start_date, end_date)
    return {}


def download_jornal(edition, path):
    url = f'http://procedebahia.com.br/irece/publicacoes/Diario%20Oficial' \
          f'%20-%20PREFEITURA%20MUNICIPAL%20DE%20IRECE%20-%20Ed%20{edition}.pdf'
    r = requests.get(url, allow_redirects=True)
    if r.status_code == 200:
        with open(path, 'wb') as writer:
            writer.write(r.content)
        return edition, path
    return edition, ''


def download_mutiple_jornals(editions, paths):
    threads = []
    with ThreadPoolExecutor(max_workers=10) as executor:
        for edition, path in zip(editions, paths):
            threads.append(executor.submit(download_jornal, edition, path))

        results = []
        for task in as_completed(threads):
            results.append(task.result())

    results = [[r for r in results if r[0] == e][0] for e in editions]
    return [r[1] for r in results]


def format_date(num):
    if num < 10:
        num = f'0{num}'
    return num


class JournalDownloader:
    def __init__(self):
        self.todos_diarios = request_journals('1970-01-01', '2022-02-22')
        self.pdfs_folder = MAIN_FOLDER / 'pdfs'
        self.jsons_folder = MAIN_FOLDER / 'out'

        self.pdfs_folder.mkdir(exist_ok=True)
        self.jsons_folder.mkdir(exist_ok=True)

        for data, edicao in self.parse(self.todos_diarios):
            self.dump_json(f'../pdfs/{edicao}.pdf', edicao, data)

    def get_day_journals(self, year: int, month: int, day: int, obj: str) -> List[str]:
        out_path = '../out/'
        list_day = []
        list_file = list(os.walk('../out'))[0][2]
        date = f'{year}-{format_date(month)}-{format_date(day)}'
        for i in list_file:
            with open(f'{out_path}{i}', encoding='utf-8') as file:
                json_object = json.load(file)
                if date in json_object['date']:
                    list_day.append(json_object[obj])
                file.close()
        return list_day
        # TODO: get all journals of a day, returns a list of JSON paths

    def get_month_journals(self, year: int, month: int, obj: str) -> List[str]:
        out_path = '../out/'
        list_month = []
        list_file = list(os.walk('../out'))[0][2]
        date = f'{year}-{format_date(month)}'
        for i in list_file:
            with open(f'{out_path}{i}', encoding='utf-8') as file:
                json_object = json.load(file)
                if date in json_object['date']:
                    list_month.append(json_object[obj])
                file.close()
        return list_month
        # TODO: get all journals of a month, returns a list of JSON paths

    def get_year_journals(self, year: int, obj: str) -> List[str]:
        out_path = '../out/'
        list_year = []
        list_file = list(os.walk('../out'))[0][2]
        date = f'{year}'
        for i in list_file:
            with open(f'{out_path}{i}', encoding='utf-8') as file:
                json_object = json.load(file)
                if date in json_object['date']:
                    list_year.append(json_object[obj])
                file.close()
        return list_year
        # TODO: get all journals of a year, returns a list of JSON paths

    @staticmethod
    def parse(response: Dict) -> List[Tuple[str, str]]:
        # TODO: parses the response and returns a tuple list of the date and edition
        lista_edicoes = []
        for diarie in response['diaries']:
            _data = diarie['data']
            _edicao = diarie['edicao']
            lista_edicoes += ((_data, _edicao),)
        return lista_edicoes

    def download_all(self, editions: List[str]) -> List[str]:
        # TODO: download journals and return a list of PDF paths. download in `self.pdfs_folder` folder
        #  OBS: make the file names ordered. Example: '0.pdf', '1.pdf', ...
        pass

    def dump_json(self, pdf_path: str, edition: str, date: str) -> str:
        if pdf_path == '':
            return ''
        output_path = self.jsons_folder / f"{edition}.json"
        data = {
            'path': str(pdf_path),
            'name': str(edition),
            'date': date,
            'origin': 'Irece-BA/DOM'
        }
        with open(output_path, 'w', encoding='utf-8') as file:
            file.write(json.dumps(data, indent=4, ensure_ascii=False))
        return str(output_path)


if __name__ == '__main__':
    download = JournalDownloader()
    obj_1 = 'path'
    obj_2 = 'name'
    download_jornal(download.get_day_journals(2022, 2, 1, obj_2)[0], download.get_day_journals(2022, 2, 1, obj_1)[0])
