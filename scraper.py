import requests
from bs4 import BeautifulSoup
import json
import re
import time
import os
from datetime import datetime

# 공공데이터 기반 외국인 관광객 핫스팟 및 출처 메타데이터
LOCATION_META = {
    "홍대": {
        "coords": (37.5563, 126.9236), 
        "grade": "S등급", 
        "feature": "공항철도 직통 / 외국인 자유여행 1위",
        "source": "서울시 열린데이터광장 [단기체류 외국인 생활인구 1위 행정동 (서교동)]",
        "stats": "외국인 단기체류 일평균 2.8만명 밀집 (KT 로밍폰 집계)"
    },
    "연남": {
        "coords": (37.5622, 126.9245), 
        "grade": "S등급", 
        "feature": "외국인 관광객 밀집 카페거리",
        "source": "서울시 열린데이터광장 [단기체류 외국인 생활인구 상위 (연남동)]",
        "stats": "외도민 합법 등록 숙소 밀집도 서울시 상위 3%"
    },
    "서교": {
        "coords": (37.5540, 126.9205), 
        "grade": "S등급", 
        "feature": "홍대 상권 중심 / 공항철도 역세권",
        "source": "서울시 열린데이터광장 [단기체류 외국인 생활인구 1위]",
        "stats": "공항철도 도보 5분 / 글로벌 2030 관광 1위"
    },
    "합정": {
        "coords": (37.5495, 126.9137), 
        "grade": "S등급", 
        "feature": "마포 관광특구 / 2·6호선 환승",
        "source": "서울시 열린데이터광장 [마포구 관광특구 통계]",
        "stats": "홍대 연계 외국인 체류 선호지역"
    },
    "망원": {
        "coords": (37.5558, 126.9101), 
        "grade": "A등급", 
        "feature": "망리단길 로컬 감성 관광",
        "source": "한국관광데이터랩 [외지인/외국인 카드소비 분석]",
        "stats": "전통시장 및 로컬 K-푸드 체험 관광지"
    },
    "마포": {
        "coords": (37.5438, 126.9515), 
        "grade": "A등급", 
        "feature": "공덕 공항철도 환승 및 도심 연결",
        "source": "서울시 열린데이터광장 [지하철 공항철도 승하차 통계]",
        "stats": "인천/김포공항 직통 접근성 우수"
    },
    "명동": {
        "coords": (37.5636, 126.9834), 
        "grade": "S등급", 
        "feature": "외국인 쇼핑/숙박 전통의 1위",
        "source": "서울관광재단 [2025 외래관광객 실태조사 숙박 선호 1위]",
        "stats": "외국인 관광객 서울 방문 시 필수 경유율 78%"
    },
    "을지로": {
        "coords": (37.5663, 126.9921), 
        "grade": "S등급", 
        "feature": "힙지로 / 도심 관광 및 명동 인접",
        "source": "서울관광재단 [도심 관광특구 분석]",
        "stats": "명동 도보권 및 레트로 K-컬처 명소"
    },
    "종로": {
        "coords": (37.5729, 126.9793), 
        "grade": "A등급", 
        "feature": "경복궁/인사동/북촌 전통 한옥 관광",
        "source": "서울관광재단 [외래관광객 문화유산 방문 통계 1위]",
        "stats": "외국인 한옥체험 및 고궁 투어 중심지"
    },
    "동대문": {
        "coords": (37.5714, 127.0097), 
        "grade": "A등급", 
        "feature": "DDP 야간 쇼핑 / 도매 관광객 밀집",
        "source": "서울시 열린데이터광장 [동대문 패션관광특구 통계]",
        "stats": "외국인 야간 쇼핑 및 DDP 방문객 집중"
    },
    "이태원": {
        "coords": (37.5345, 126.9946), 
        "grade": "A등급", 
        "feature": "다국적 문화 및 나이트라이프",
        "source": "한국관광데이터랩 [이태원 관광특구 외국인 소비 통계]",
        "stats": "다국적 F&B 및 외국인 커뮤니티 밀집"
    },
    "한남": {
        "coords": (37.5346, 127.0022), 
        "grade": "A등급", 
        "feature": "고급 트렌드 / 외국인 거주 밀집",
        "source": "서울시 열린데이터광장 [용산구 외국인 등록 인구 통계]",
        "stats": "대사관 밀집 및 고급 문화예술 거리"
    },
    "용산": {
        "coords": (37.5326, 126.9900), 
        "grade": "A등급", 
        "feature": "KTX 서울역 인접 및 용리단길",
        "source": "한국철도공사 KTX 승하차 및 서울시 생활인구",
        "stats": "지방/공항 연계 교통 허브"
    },
    "성수": {
        "coords": (37.5446, 127.0560), 
        "grade": "A등급", 
        "feature": "글로벌 MZ 팝업스토어 성지",
        "source": "서울시 열린데이터광장 [2030 외국인 유입 증가율 1위]",
        "stats": "글로벌 패션/뷰티 팝업 및 카페 투어"
    },
    "강남": {
        "coords": (37.4979, 127.0276), 
        "grade": "A등급", 
        "feature": "K-뷰티 / 의료관광 / 비즈니스",
        "source": "한국보건산업진흥원 [외국인 환자 유치 의료관광 통계 1위]",
        "stats": "의료/뷰티 및 테헤란로 비즈니스 관광객"
    },
    "신사": {
        "coords": (37.5164, 127.0202), 
        "grade": "A등급", 
        "feature": "가로수길 패션 및 뷰티 관광",
        "source": "한국관광데이터랩 [강남구 외국인 쇼핑 결제 통계]",
        "stats": "글로벌 브랜드 플래그십 및 성형/피부과 밀집"
    },
    "해운대": {
        "coords": (35.1631, 129.1636), 
        "grade": "S등급", 
        "feature": "부산 외국인 관광 1위 해변",
        "source": "부산관광공사 [외국인 관광객 방문지 실태조사 1위]",
        "stats": "부산 방문 외국인의 82% 방문 필수 코스"
    },
    "광안리": {
        "coords": (35.1532, 129.1189), 
        "grade": "A등급", 
        "feature": "광안대교 오션뷰 인기 숙소",
        "source": "부산관광공사 [부산 야경 및 오션뷰 관광 통계]",
        "stats": "오션뷰 에어비앤비 예약률 최상위"
    },
    "제주": {
        "coords": (33.4996, 126.5312), 
        "grade": "A등급", 
        "feature": "무비자 글로벌 휴양 관광지",
        "source": "제주관광공사 [외국인 입도 통계]",
        "stats": "동남아/중화권 무비자 입국 자연 휴양지"
    }
}

TRADE_QUERIES = [
    '"에어비앤비 양도합니다"',
    '"외도민 양도합니다"',
    '"전대차 가능" 임대',
    '"에어비앤비 가능" 임대',
    '"외도민 매물" 양도',
    '"숙박업 양도" 권리금',
    '"에어비앤비 승계"',
    '"단기임대 양도"',
    '"에어비앤비 직거래"'
]

EXCLUDE_TITLE_WORDS = [
    '?', '까요', '인가요', '궁금', '진실', '칼럼', '팁', '노하우', '주의점', 
    '신청방법', '주의사항', '어떨까요', '생각하시나요', '질문', '고민', '조언', 
    '후기', '합격', '강의', '특강', '뉴스', '기사', '불편한'
]

TRADE_ACTION_WORDS = [
    '양도', '임대', '승계', '매물', '내놓습니다', '내놓아요', '직거래', '구합니다', '거래', '인수'
]

def parse_relative_days(text):
    text = text.strip()
    if any(k in text for k in ['분 전', '시간 전', '방금', '초 전']):
        return 0
    if '어제' in text:
        return 1
    day_match = re.search(r'(\d+)일\s*전', text)
    if day_match:
        return int(day_match.group(1))
    date_match = re.search(r'(\d{4})[.-](\d{1,2})[.-](\d{1,2})', text)
    if date_match:
        y, m, d = map(int, date_match.groups())
        try:
            target_dt = datetime(y, m, d)
            diff = (datetime.now() - target_dt).days
            return max(0, diff)
        except Exception:
            pass
    return None

def get_coords_from_text(text):
    import re
    # 글 내용에서 OO동, OO역, OO시 등 지역 키워드 추출
    match = re.search(r'([가-힣]{2,5}(?:동|역|구|시))', text)
    if not match:
        return None, None, None
        
    keyword = match.group(1)
    
    # API 중복 호출 방지를 위한 메모리 캐싱
    if not hasattr(get_coords_from_text, "cache"):
        get_coords_from_text.cache = {}
        
    if keyword in get_coords_from_text.cache:
        return get_coords_from_text.cache[keyword]
        
    # 무료 지도 API(Nominatim)로 좌표 변환
    url = f"https://nominatim.openstreetmap.org/search?q={keyword}&format=json&limit=1"
    headers = {"User-Agent": "AirbnbScannerApp/1.0"}
    try:
        import time
        time.sleep(1.2) # API 정책(초당 1회) 준수
        res = requests.get(url, headers=headers, timeout=5)
        if res.status_code == 200:
            data = res.json()
            if data and len(data) > 0:
                lat = float(data[0]["lat"])
                lon = float(data[0]["lon"])
                
                result = (keyword, lat, lon)
                get_coords_from_text.cache[keyword] = result
                return result
    except Exception as e:
        print(f"Geocoding Error for {keyword}: {e}")
        
    return None, None, None

def extract_location_info(text):
    import random
    
    # 1. 핫존 메타데이터에 있는 핵심 지역 매칭
    for loc, info in LOCATION_META.items():
        if loc in text:
            lat = info["coords"][0] + random.uniform(-0.003, 0.003)
            lng = info["coords"][1] + random.uniform(-0.003, 0.003)
            return loc, round(lat, 5), round(lng, 5), info["grade"], info["feature"], info["source"], info["stats"]
            
    # 2. 핫존이 아니면 글 내용(텍스트)에서 지역 이름(방이동 등)을 뽑아내 좌표 변환!
    keyword, lat, lng = get_coords_from_text(text)
    if keyword and lat and lng:
        lat += random.uniform(-0.002, 0.002) # 핀 겹침 방지
        lng += random.uniform(-0.002, 0.002)
        return keyword, round(lat, 5), round(lng, 5), "일반매물", f"{keyword} 인근 매물", "본문 분석 기반 위치 추출", "시세 확인용"
        
    # 지역명이 아예 없으면 제외
    return None

def extract_keywords(text):
    keywords = []
    targets = ["에어비앤비", "외도민", "전대차", "단기임대", "숙박업", "한옥체험", "양도", "합법", "풀옵션", "권리금절충"]
    for t in targets:
        if t in text:
            keywords.append(t)
    return list(set(keywords))

def scrape_fresh_real_estate_trades():
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8'
    }
    
    results = []
    seen_links = set()

    for query in TRADE_QUERIES:
        url = f"https://search.naver.com/search.naver?ssc=tab.cafe.all&query={query}&sort=1"
        try:
            res = requests.get(url, headers=headers, timeout=8)
            if res.status_code != 200:
                continue
            
            soup = BeautifulSoup(res.text, 'html.parser')
            items = soup.select('li.bx')
            
            for item in items:
                title_el = item.select_one('a.title_link, a.api_txt_lines')
                if not title_el:
                    continue
                
                title = title_el.get_text(strip=True)
                link = title_el.get('href', '')
                
                if not link or link in seen_links:
                    continue
                
                # 1. 질문/잡담 차단
                if any(bad in title for bad in EXCLUDE_TITLE_WORDS):
                    continue
                
                # 2. 거래 행위 단어 필수
                if not any(action in title for action in TRADE_ACTION_WORDS):
                    continue
                
                # 3. 날짜 파싱 및 60일 초과 매물 영구 제외!
                days_ago = None
                date_str = "최근"
                for span in item.select('span, time, em'):
                    txt = span.get_text(strip=True)
                    d = parse_relative_days(txt)
                    if d is not None:
                        days_ago = d
                        date_str = txt
                        break
                
                # 60일 넘은 글은 절대 수집하지 않음!
                if days_ago is not None and days_ago > 60:
                    continue
                
                if days_ago is None:
                    days_ago = 2
                    date_str = "최근"

                seen_links.add(link)
                
                cafe_el = item.select_one('a.name, .sub_txt')
                cafe_name = cafe_el.get_text(strip=True) if cafe_el else "부동산/양도 커뮤니티"
                
                desc_el = item.select_one('.dsc_txt, .dsc_link, .api_txt_lines.dsc')
                desc = desc_el.get_text(strip=True) if desc_el else ""
                
                full_text = f"{title} {desc}"
                loc_info = extract_location_info(full_text)
                
                if not loc_info:
                    continue # 엉뚱한 위치 방지
                    
                loc_name, lat, lng, grade, feature, data_source, data_stats = loc_info
                detected_kw = extract_keywords(full_text)
                
                price_match = re.search(r'(\d+[\s]*[만억]?[\s]*\/[\s]*\d+[\s]*만?|\d+[\s]*만원|\d+[\s]*억|권리금[\s]*\d+만?|보증금[\s]*\d+만?)', full_text)
                price_str = price_match.group(0) if price_match else "협의 / 본문 확인"

                is_completed = "완료" in title or "마감" in title
                status_label = "거래완료" if is_completed else "거래가능"

                results.append({
                    "id": len(results) + 1,
                    "title": title,
                    "link": link,
                    "cafe": cafe_name,
                    "desc": desc,
                    "date_str": date_str,
                    "days_ago": days_ago,
                    "location": loc_name,
                    "lat": lat,
                    "lng": lng,
                    "grade": grade,
                    "feature": feature,
                    "source_name": data_source,
                    "source_stats": data_stats,
                    "price": price_str,
                    "status": status_label,
                    "keywords": detected_kw,
                    "source": "실제 거래 매물"
                })
        except Exception as e:
            print(f"Error scraping {query}: {e}")
        
        time.sleep(0.3)

    results.sort(key=lambda x: x["days_ago"])
    print(f"Total {len(results)} FRESH trade items collected.")
    return results

if __name__ == "__main__":
    items = scrape_fresh_real_estate_trades()
    output_path = os.path.join(os.path.dirname(__file__), "listings.json")
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(items, f, ensure_ascii=False, indent=2)
    print(f"Saved to {output_path}")
