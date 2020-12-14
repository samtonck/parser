from app.avito_parser import AvitoParser
from fastapi import FastAPI


app = FastAPI()
p = AvitoParser()


@app.get("/")
def my_app():
    return p.get_info()


@app.get("/app/{geo}/{request}")
def my_app(geo: str, request: str):
    p = AvitoParser(geo, request)
    return p.get_info()


@app.get("/stat/{id}")
def my_stat(id: str):
    return p.stat_request(id)


def main():
    p.get_info()
    p.stat_request()
    p.stat_request()


if __name__ == '__main__':
    main()
