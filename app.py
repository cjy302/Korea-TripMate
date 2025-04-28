from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
import requests
import config

app = FastAPI()
templates = Jinja2Templates(directory="templates")

area_codes = {
    '서울': 1, '부산': 6, '대구': 4, '광주': 5, '대전': 3, '인천': 2,
    '울산': 7, '세종': 8, '경기': 31, '강원': 32,
    '충북': 33, '충남': 34, '경북': 35, '경남': 36,
    '전북': 37, '전남': 38, '제주': 39
}

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request, "areas": area_codes})

@app.get("/search", response_class=HTMLResponse)
async def search(request: Request, region: str):
    area_code = area_codes.get(region)
    if not area_code:
        return HTMLResponse(content="❌ 잘못된 지역입니다.", status_code=400)

    service_key = config.SERVICE_KEY

    url_tour = (
        f'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'
        f'?serviceKey={service_key}'
        f'&MobileApp=TripMateWeb'
        f'&MobileOS=ETC'
        f'&numOfRows=5'
        f'&pageNo=1'
        f'&areaCode={area_code}'
        f'&_type=json'
    )
    url_hotel = (
        f'http://apis.data.go.kr/B551011/KorService1/areaBasedList1'
        f'?serviceKey={service_key}'
        f'&MobileApp=TripMateWeb'
        f'&MobileOS=ETC'
        f'&numOfRows=5'
        f'&pageNo=1'
        f'&areaCode={area_code}'
        f'&contentTypeId=32'
        f'&_type=json'
    )

    response_tour = requests.get(url_tour)
    response_hotel = requests.get(url_hotel)

    if response_tour.status_code == 200 and response_hotel.status_code == 200:
        tour_items = response_tour.json()['response']['body']['items']['item']
        hotel_items = response_hotel.json()['response']['body']['items']['item']

        return templates.TemplateResponse("result.html", {
            "request": request,
            "region": region,
            "tour_items": tour_items,
            "hotel_items": hotel_items
        })
    else:
        return HTMLResponse(content="❌ 관광지 또는 숙박 정보를 가져오는 데 실패했습니다.", status_code=500)
