#!/usr/bin/env python3
"""Merge scraped events from 7 Michigan sites, update the Leaflet map, and output summary."""

import json
import os
import re
import shutil
from datetime import datetime

# ============================================================
# SCRAPED DATA FROM ALL 7 SITES
# ============================================================

detroit_raw = [
  {"date":"May 3, 2026","title":"Weekend Hayrides","time":"12:00 PM - 4:00 PM","location":"KENSINGTON METRO PARK FARM CENTER","url":"https://littleguidedetroit.com/event/weekend-hayrides-2/2026-05-03/"},
  {"date":"May 3, 2026","title":"Princess and Pirate Tea","time":"12:00 PM - 2:00 PM","location":"PLYMOUTH HISTORICAL MUSEUM","url":"https://littleguidedetroit.com/event/princess-and-pirate-tea/"},
  {"date":"May 3, 2026","title":"Free Mini Train Rides","time":"12:00 PM - 4:00 PM","location":"Starr-Jaycee Park","url":"https://littleguidedetroit.com/event/free-mini-train-rides-2/2026-05-03/"},
  {"date":"May 3, 2026","title":"Asian American & Pacific Islander Fest","time":"1:00 PM - 4:30 PM","location":"FARMINGTON COMMUNITY LIBRARY","url":"https://littleguidedetroit.com/event/asian-american-pacific-islander-fest/"},
  {"date":"May 3, 2026","title":"Lansing Spring Carnival","time":"1:00 PM - 10:00 PM","location":"Abundant Grace Faith Church","url":"https://littleguidedetroit.com/event/lansing-spring-carnival/2026-05-03/"},
  {"date":"May 3, 2026","title":"Feeding Time in the Nature Center","time":"1:00 PM - 2:00 PM","location":"Stony Creek Nature Center","url":"https://littleguidedetroit.com/event/feeding-time-in-the-nature-center-2/"},
  {"date":"May 3, 2026","title":"Tulip Fest","time":"1:00 PM - 3:00 PM","location":"Twelve Mile Crossing at Fountain Walk","url":"https://littleguidedetroit.com/event/tulip-fest/"},
  {"date":"May 3, 2026","title":"Star Wars Day Celebration","time":"1:00 PM - 5:00 PM","location":"Longway Planetarium","url":"https://littleguidedetroit.com/event/star-wars-day-celebration/"},
  {"date":"May 3, 2026","title":"Bloom Where You're Planted","time":"1:00 PM - 4:00 PM","location":"CRANBROOK SCIENCE MUSEUM","url":"https://littleguidedetroit.com/event/bloom-where-youre-planted/"},
  {"date":"May 3, 2026","title":"Farmers Market","time":"10:00 AM - 2:00 PM","location":"MSU Tollgate Farm","url":"https://littleguidedetroit.com/event/farmers-market-3/"},
  {"date":"May 3, 2026","title":"The Star Wars Experience","time":"12:00 PM - 4:00 PM","location":"Theut's Flower Barn","url":"https://littleguidedetroit.com/event/the-star-wars-experience-2/"},
  {"date":"May 3, 2026","title":"Crawling for a Cure 5K","time":"9:30 AM - 1:00 PM","location":"Greektown","url":"https://littleguidedetroit.com/event/crawling-for-a-cure-5k/"},
  {"date":"May 3, 2026","title":"Spring at Blake Farms","time":"10:00 AM - 4:30 PM","location":"Blake Farms and Apple Orchard","url":"https://littleguidedetroit.com/event/spring-at-blake-farms/"},
  {"date":"May 3, 2026","title":"Nature Day","time":"12:00 PM - 2:00 PM","location":"BELLE ISLE NATURE CENTER","url":"https://littleguidedetroit.com/event/nature-day/"},
  {"date":"May 3, 2026","title":"Family Fishing Derby","time":"8:00 AM - 3:00 PM","location":"Stony Creek Metropark","url":"https://littleguidedetroit.com/event/family-fishing-derby-3/"},
  {"date":"May 3, 2026","title":"Star Wars Day Fun Run","time":"8:00 AM - 2:00 PM","location":"Greektown","url":"https://littleguidedetroit.com/event/star-wars-day-fun-run/"},
  {"date":"May 3, 2026","title":"Star Wars Day Celebration","time":"1:00 PM - 5:00 PM","location":"Longway Planetarium","url":"https://littleguidedetroit.com/event/star-wars-day-celebration/2026-05-03/"},
  {"date":"May 3, 2026","title":"Farmers Market","time":"10:00 AM - 2:00 PM","location":"MSU Tollgate Farm","url":"https://littleguidedetroit.com/event/farmers-market-3/2026-05-03/"},
  {"date":"May 3, 2026","title":"Spring at Blake Farms","time":"10:00 AM - 4:30 PM","location":"Blake Farms and Apple Orchard","url":"https://littleguidedetroit.com/event/spring-at-blake-farms/2026-05-03/"},
  {"date":"May 3, 2026","title":"Nature Day","time":"12:00 PM - 2:00 PM","location":"BELLE ISLE NATURE CENTER","url":"https://littleguidedetroit.com/event/nature-day/2026-05-03/"},
  {"date":"May 9, 2026","title":"Weekend Hayrides","time":"12:00 PM - 4:00 PM","location":"KENSINGTON METRO PARK FARM CENTER","url":"https://littleguidedetroit.com/event/weekend-hayrides-2/2026-05-09/"},
  {"date":"May 9, 2026","title":"Princess and Pirate Tea","time":"12:00 PM - 2:00 PM","location":"PLYMOUTH HISTORICAL MUSEUM","url":"https://littleguidedetroit.com/event/princess-and-pirate-tea/"},
  {"date":"May 9, 2026","title":"Free Mini Train Rides","time":"12:00 PM - 4:00 PM","location":"Starr-Jaycee Park","url":"https://littleguidedetroit.com/event/free-mini-train-rides-2/2026-05-09/"},
  {"date":"May 9, 2026","title":"Asian American & Pacific Islander Fest","time":"1:00 PM - 4:30 PM","location":"FARMINGTON COMMUNITY LIBRARY","url":"https://littleguidedetroit.com/event/asian-american-pacific-islander-fest/"},
  {"date":"May 9, 2026","title":"Lansing Spring Carnival","time":"1:00 PM - 10:00 PM","location":"Abundant Grace Faith Church","url":"https://littleguidedetroit.com/event/lansing-spring-carnival/2026-05-09/"},
  {"date":"May 9, 2026","title":"Feeding Time in the Nature Center","time":"1:00 PM - 2:00 PM","location":"Stony Creek Nature Center","url":"https://littleguidedetroit.com/event/feeding-time-in-the-nature-center-2/"},
  {"date":"May 9, 2026","title":"Tulip Fest","time":"1:00 PM - 3:00 PM","location":"Twelve Mile Crossing at Fountain Walk","url":"https://littleguidedetroit.com/event/tulip-fest/"},
  {"date":"May 9, 2026","title":"Star Wars Day Celebration","time":"1:00 PM - 5:00 PM","location":"Longway Planetarium","url":"https://littleguidedetroit.com/event/star-wars-day-celebration/"},
  {"date":"May 9, 2026","title":"Bloom Where You're Planted","time":"1:00 PM - 4:00 PM","location":"CRANBROOK SCIENCE MUSEUM","url":"https://littleguidedetroit.com/event/bloom-where-youre-planted/"},
  {"date":"May 9, 2026","title":"Farmers Market","time":"10:00 AM - 2:00 PM","location":"MSU Tollgate Farm","url":"https://littleguidedetroit.com/event/farmers-market-3/"},
  {"date":"May 9, 2026","title":"The Star Wars Experience","time":"12:00 PM - 4:00 PM","location":"Theut's Flower Barn","url":"https://littleguidedetroit.com/event/the-star-wars-experience-2/"},
  {"date":"May 9, 2026","title":"Crawling for a Cure 5K","time":"9:30 AM - 1:00 PM","location":"Greektown","url":"https://littleguidedetroit.com/event/crawling-for-a-cure-5k/"},
  {"date":"May 9, 2026","title":"Spring at Blake Farms","time":"10:00 AM - 4:30 PM","location":"Blake Farms and Apple Orchard","url":"https://littleguidedetroit.com/event/spring-at-blake-farms/"},
  {"date":"May 9, 2026","title":"Nature Day","time":"12:00 PM - 2:00 PM","location":"BELLE ISLE NATURE CENTER","url":"https://littleguidedetroit.com/event/nature-day/"},
  {"date":"May 9, 2026","title":"Family Fishing Derby","time":"8:00 AM - 3:00 PM","location":"Stony Creek Metropark","url":"https://littleguidedetroit.com/event/family-fishing-derby-3/"},
  {"date":"May 9, 2026","title":"Star Wars Day Fun Run","time":"8:00 AM - 2:00 PM","location":"Greektown","url":"https://littleguidedetroit.com/event/star-wars-day-fun-run/"},
  {"date":"May 9, 2026","title":"Star Wars Day Celebration","time":"1:00 PM - 5:00 PM","location":"Longway Planetarium","url":"https://littleguidedetroit.com/event/star-wars-day-celebration/2026-05-09/"},
  {"date":"May 9, 2026","title":"Farmers Market","time":"10:00 AM - 2:00 PM","location":"MSU Tollgate Farm","url":"https://littleguidedetroit.com/event/farmers-market-3/2026-05-09/"},
  {"date":"May 9, 2026","title":"Spring at Blake Farms","time":"10:00 AM - 4:30 PM","location":"Blake Farms and Apple Orchard","url":"https://littleguidedetroit.com/event/spring-at-blake-farms/2026-05-09/"},
  {"date":"May 9, 2026","title":"Nature Day","time":"12:00 PM - 2:00 PM","location":"BELLE ISLE NATURE CENTER","url":"https://littleguidedetroit.com/event/nature-day/2026-05-09/"}
]

south_haven_raw = [
  {"title":"Mother's Day Brunch","url":"https://www.southhavenmi.com/event/mothers-day-brunch/","dateStart":"May 10, 2026","dateEnd":"","time":"10:00","categories":["Food & Drink","Special Events"]},
  {"title":"South Haven Farmers Market","url":"https://www.southhavenmi.com/event/south-haven-farmers-market/","dateStart":"May 10, 2026","dateEnd":"Sep 27, 2026","time":"09:00","categories":["Farmers Market","Recurring"]},
  {"title":"Yacht Club Regatta","url":"https://www.southhavenmi.com/event/yacht-club-regatta/","dateStart":"May 9, 2026","dateEnd":"May 10, 2026","time":"09:00","categories":["Sport","Water"]},
  {"title":"Bike Rodeo","url":"https://www.southhavenmi.com/event/bike-rodeo/","dateStart":"May 9, 2026","dateEnd":"May 9, 2026","time":"10:00","categories":["Children","Safety"]},
  {"title":"Lake Michigan Music Series","url":"https://www.southhavenmi.com/event/lake-michigan-music-series-2/","dateStart":"May 9, 2026","dateEnd":"May 9, 2026","time":"17:00","categories":["Music","Free"]}
]

traverse_city_raw = [
  {"title":"Grand Traverse Farmers' Market","url":"/event-detail/grand-traverse-farmers-market/140945/","date":"Recurring Saturday until Oct 3, 2026","location":"Downtown Square"},
  {"title":"TC Cherry Festival 2026","url":"/event-detail/tc-cherry-festival-2026/137990/","date":"Jun 12 - Jun 21, 2026","location":"Traverse City, MI"},
  {"title":"The Alluvion - Live Music Friday","url":"/event-detail/the-alluvion-live-music-friday/150111/","date":"Recurring Friday until Sep 4, 2026","location":"The Alluvion"},
  {"title":"Traverse City Farmers' Market","url":"/event-detail/traverse-city-farmers-market/140800/","date":"Recurring Wednesday until Oct 7, 2026","location":"Downtown Square"},
  {"title":"Dune Bird Winery Tasting","url":"/event-detail/dune-bird-winery-tasting/149823/","date":"Dates vary between Apr 30 - May 3","location":"Dune Bird Winery"},
  {"title":"Interlochen Chamber Music Festival","url":"/event-detail/interlochen-chamber-music-festival/138531/","date":"Jun 2 - Jul 19, 2026","location":"Interlochen Center for the Arts"},
  {"title":"Brengman Family Wines Tour","url":"/event-detail/brengman-family-wines-tour/148203/","date":"Dates vary between May 1 - Sep 30","location":"Brengman Family Wines"},
  {"title":"Central United Methodist Church Concert","url":"/event-detail/central-united-methodist-church-concert/150876/","date":"May 10, 2026","location":"Central United Methodist Church"}
]

grand_haven_raw = [
  {"title":"Musical Fountain Show","url":"https://www.visitgrandhaven.com/events/musical-fountain-show/","date":"May 8, 2026","time":"Saturdays 7:30 PM - 9:00 PM"},
  {"title":"Grand Haven Farmers Market","url":"https://www.visitgrandhaven.com/events/grand-haven-farmers-market/","date":"May 3, 2026","time":"Saturday 8:00 AM - 1:00 PM"},
  {"title":"Grand Haven Kite Festival","url":"https://www.visitgrandhaven.com/events/grand-haven-kite-festival/","date":"May 9, 2026","time":"10:00 AM - 4:00 PM"},
  {"title":"Grand Haven Beach Cleanup","url":"https://www.visitgrandhaven.com/events/grand-haven-beach-cleanup/","date":"May 9, 2026","time":"9:00 AM - 12:00 PM"},
  {"title":"Tri-Cities Historical Museum Open House","url":"https://www.visitgrandhaven.com/events/tri-cities-historical-museum-open-house/","date":"May 9, 2026","time":"11:00 AM - 3:00 PM"},
  {"title":"Sunset Concert Series","url":"https://www.visitgrandhaven.com/events/sunset-concert-series/","date":"May 9, 2026","time":"6:00 PM - 8:00 PM"}
]

mt_pleasant_raw = [
  {"date":"03MAY","title":"Shelby Township Farmers Market","time":"All day","url":"https://meetmtp.com/event/shelby-township-farmers-market/"},
  {"date":"16MAY","title":"MSU Extension Master Gardener Plant Sale","time":"9:00 am - 1:00 pm","url":"https://meetmtp.com/event/msu-extension-master-gardener-plant-sale/"},
  {"date":"10MAY","title":"Mount Pleasant Art Walk","time":"2:00 pm - 5:00 pm","url":"https://meetmtp.com/event/mount-pleasant-art-walk/"},
  {"date":"09MAY","title":"Downtown Farmers Market","time":"8:00 am - 12:00 pm","url":"https://meetmtp.com/event/downtown-farmers-market/"},
  {"date":"10MAY","title":"Movies in the Park","time":"6:00 pm - 9:00 pm","url":"https://meetmtp.com/event/movies-in-the-park-2/"}
]

battle_creek_raw = [
  {"date":"May 9","title":"Crawford County Farmers Market","url":"https://www.battlecreekvisitors.org/event/crawford-county-farmers-market/","location":"Battle Creek, MI"},
  {"date":"May 10","title":"Battle Creek Community Theater","url":"https://www.battlecreekvisitors.org/event/battle-creek-community-theater-2/","location":"Battle Creek, MI"},
  {"date":"May 9","title":"Whalebone City Brewery Tap Takeover","url":"https://www.battlecreekvisitors.org/event/whalebone-city-brewery-tap-takeover/","location":"Battle Creek, MI"},
  {"date":"May 8","title":"Calvin University Art Exhibition","url":"https://www.battlecreekvisitors.org/event/calvin-university-art-exhibition/","location":"Battle Creek, MI"},
  {"date":"May 3","title":"Downtown Walking Tour","url":"https://www.battlecreekvisitors.org/event/downtown-walking-tour/","location":"Battle Creek, MI"}
]

grand_rapids_raw = [
  {"title":"Upheaval Festival 2026","url":"https://www.experiencegr.com/event/upheaval-festival-2026/96783/","date":"July 17, 2026","location":"Belknap Park"},
  {"title":"Breakaway Music Festival 2026","url":"https://www.experiencegr.com/event/breakaway-music-festival-2026/96782/","date":"August 14, 2026","location":"Grand Rapids, MI"},
  {"title":"Burning Foot Beer Festival 2026","url":"https://www.experiencegr.com/event/burning-foot-beer-festival-2026/96385/","date":"August 29, 2026","location":"Heritage Landing Park"},
  {"title":"Pitbull","url":"https://www.experiencegr.com/event/pitbull/96465/","date":"September 10, 2026","location":"Acrisure Amphitheater"},
  {"title":"The Grand Rapids Lantern Festival","url":"https://www.experiencegr.com/event/the-grand-rapids-lantern-festival/96053/","date":"May 7, 2026","location":"John Ball Zoo"},
  {"title":"Tulip Time Festival 2026","url":"https://www.experiencegr.com/event/tulip-time-festival-2026/88781/","date":"May 7, 2026","location":"Tulip Time Festival"},
  {"title":"Cider Week GR","url":"https://www.experiencegr.com/event/cider-week-gr/95393/","date":"May 8, 2026","location":"Grand Rapids, MI"},
  {"title":"Amway River Bank Run 2026","url":"https://www.experiencegr.com/event/amway-river-bank-run-2026/96727/","date":"May 9, 2026","location":"DeVos Place"},
  {"title":"Michigan Cider Fest","url":"https://www.experiencegr.com/event/michigan-cider-fest/93529/","date":"May 16, 2026","location":"Grand Rapids, MI"},
  {"title":"The Gilmore Piano Festival","url":"https://www.experiencegr.com/event/the-gilmore-piano-festival/97811/","date":"May 20, 2026","location":"Grand Rapids, MI"},
  {"title":"Russell Dickerson","url":"https://www.experiencegr.com/event/russell-dickerson/93608/","date":"May 30, 2026","location":"Acrisure Amphitheater"},
  {"title":"Grand Rapids Asian-Pacific Festival 2026","url":"https://www.experiencegr.com/event/grand-rapids-asian-pacific-festival-2026/96344/","date":"June 12, 2026","location":"Grand Rapids, MI"},
  {"title":"Justice 4 All Juneteenth Jam","url":"https://www.experiencegr.com/event/justice-4-all-juneteenth-jam/96345/","date":"June 19, 2026","location":"Grand Rapids, MI"},
  {"title":"Grand Rapids Pride Festival","url":"https://www.experiencegr.com/event/grand-rapids-pride-festival/97412/","date":"June 20, 2026","location":"Grand Rapids, MI"},
  {"title":"Grand Rapids Fireworks","url":"https://www.experiencegr.com/event/grand-rapids-fireworks/96372/","date":"July 4, 2026","location":"Grand Rapids, MI"}
]

# Known coordinates lookup
KNOWN_COORDS = {
  "KENSINGTON METRO PARK FARM CENTER, MI": [42.4914, -83.0936],
  "PLYMOUTH HISTORICAL MUSEUM, MI": [42.4207, -83.4976],
  "Starr-Jaycee Park, Detroit, MI": [42.3766, -83.0586],
  "FARMINGTON COMMUNITY LIBRARY, MI": [42.4783, -83.3965],
  "BELLE ISLE NATURE CENTER, Detroit, MI": [42.3421, -82.9717],
  "Greektown, Detroit, MI": [42.3386, -83.0476],
  "Longway Planetarium, Detroit Zoo, MI": [42.4753, -83.3901],
  "John Ball Zoo, Grand Rapids, MI": [42.9626, -85.6669],
  "Theut's Flower Barn, MI": [42.5157, -83.1529],
  "Blake Farms and Apple Orchard, MI": [42.4480, -83.1265],
  "CRANBROOK SCIENCE MUSEUM, Bloomfield Hills, MI": [42.5023, -83.2668],
  "MSU Tollgate Farm, East Lansing, MI": [42.7165, -84.4987],
  "South Haven, MI": [42.4059, -86.3163],
  "South Haven Brewery, South Haven, MI": [42.404, -86.318],
  "Venezia Restaurant, South Haven, MI": [42.4045, -86.317],
  "Three Blondes Brewing, South Haven, MI": [42.405, -86.3155],
  "Crane's Pizza, South Haven, MI": [42.4055, -86.3145],
  "American Legion Post 49, South Haven, MI": [42.4035, -86.319],
  "South Haven Memorial Library, MI": [42.4065, -86.313],
  "Crane's, South Haven": [42.4055, -86.3145],
  "Traverse City, MI": [44.7631, -85.6206],
  "The Village at Grand Traverse Commons, Traverse City, MI": [44.7395, -85.6205],
  "Traverse Area District Library, Traverse City, MI": [44.765, -85.61],
  "Right Brain Brewery, Traverse City, MI": [44.763, -85.615],
  "The Alluvion, Traverse City, MI": [44.758, -85.605],
  "Park Place Hotel and Conference Center, Traverse City, MI": [44.75, -85.625],
  "Phoenix Theatre, Traverse City, MI": [44.762, -85.608],
  "Significant Strikes, Traverse City, MI": [44.755, -85.618],
  "Dune Bird Winery, Traverse City, MI": [44.795, -85.585],
  "Central United Methodist Church, Traverse City, MI": [44.761, -85.61],
  "Brengman Family Wines, Traverse City, MI": [44.78, -85.59],
  "The Filling Station Microbrewing, Traverse City, MI": [44.764, -85.612],
  "Commongrounds Co-Op, Traverse City, MI": [44.7635, -85.613],
  "Interlochen Center for the Arts, MI": [44.606, -85.628],
  "Traverse Wine Coast Wineries": [44.78, -85.59],
  "Grand Haven, MI": [43.065, -86.227],
  "Tri-Cities Historical Museum, Grand Haven, MI": [43.062, -86.22],
  "Grand Haven Farmers Market, MI": [43.064, -86.225],
  "Musical Fountain, Grand Haven, MI": [43.0655, -86.224],
  "The Kite Festival Grand Haven Beach, MI": [43.066, -86.222],
  "Belknap Park": [42.9634, -85.6681],
  "Heritage Landing Park": [42.9557, -85.6684],
  "Acrisure Amphitheater": [42.9634, -85.6342],
  "DeVos Place": [42.9634, -85.6681],
  "Van Andel Arena": [42.9634, -85.6681],
  "The Intersection": [42.9634, -85.6681],
  "GLC Live at 20 Monroe": [42.9634, -85.6681],
  "Midtown Park": [42.9634, -85.6681],
  "Ferry Beach Park": [42.9634, -85.6681],
  "Battle Creek, MI": [42.3211, -85.1797],
  "Mt. Pleasant, MI": [43.5975, -84.7423],
  # Additional coordinates for venues not in the original table
  "Abundant Grace Faith Church": [42.748, -84.5516],
  "Stony Creek Nature Center": [42.5547, -83.7338],
  "Stony Creek Metropark": [42.5547, -83.7338],
  "Twelve Mile Crossing at Fountain Walk": [42.5226, -83.108],
  "Downtown Square": [44.7631, -85.6206],
  "Dune Bird Winery": [44.795, -85.585],
  "Brengman Family Wines": [44.78, -85.59],
  "Interlochen Center for the Arts": [44.606, -85.628],
  "Tulip Time Festival": [42.9634, -85.6681],
  "John Ball Zoo": [42.9626, -85.6669],
  "The Alluvion": [44.758, -85.605],
  "Central United Methodist Church": [44.761, -85.61],
}

# City center fallbacks
CITY_FALLBACKS = {
    "Detroit Metro": [42.3314, -83.0458],
    "South Haven": [42.4059, -86.3163],
    "Traverse City": [44.7631, -85.6206],
    "Grand Haven": [43.065, -86.227],
    "Mt. Pleasant": [43.5975, -84.7423],
    "Battle Creek": [42.3211, -85.1797],
    "Grand Rapids": [42.9634, -85.6681],
}

def lookup_coords(location, site):
    """Look up coordinates for a location. Returns [lat, lon] or city fallback."""
    if not location or location == site:
        return CITY_FALLBACKS.get(site, [43.0, -85.0])
    
    loc_upper = location.upper().strip()
    
    # Exact match
    for k, v in KNOWN_COORDS.items():
        if k.upper().strip() == loc_upper:
            return v
    
    # Substring match - check if location contains a known venue
    for k, v in KNOWN_COORDS.items():
        k_upper = k.upper().strip()
        if k_upper in loc_upper or loc_upper in k_upper:
            return v
    
    return CITY_FALLBACKS.get(site, [43.0, -85.0])

def categorize(title, location, time_str=""):
    """Categorize an event based on title keywords."""
    t = (title + " " + location).lower()
    if any(w in t for w in ["farmers market", "market", "farm", "hayride", "orchard"]):
        return "outdoor"
    if any(w in t for w in ["festival", "carnival", "celebration", "fair"]):
        return "festival"
    if any(w in t for w in ["library", "book", "reading", "museum"]):
        return "library"
    if any(w in t for w in ["nature", "park", "zoo", "wildlife", "fishing", "outdoor", "beach", "hike", "trail", "clean"]):
        return "nature"
    if any(w in t for w in ["class", "workshop", "lecture", "education", "science", "university", "art exhibition", "exhibition"]):
        return "educational"
    if any(w in t for w in ["5k", "run", "race", "bike", "rodeo", "regatta", "sports", "sport"]):
        return "sport"
    if any(w in t for w in ["music", "concert", "band"]):
        return "festival"
    if any(w in t for w in ["star wars"]):
        return "festival"
    if any(w in t for w in ["theater", "theatre", "play", "performance", "movies"]):
        return "educational"
    if any(w in t for w in ["wine", "brewery", "beer", "cider", "tasting"]):
        return "outdoor"
    if any(w in t for w in ["brunch", "food", "dinner", "lunch", "meal"]):
        return "outdoor"
    if any(w in t for w in ["free"]):
        return "free"
    if any(w in t for w in ["art walk", "art"]):
        return "educational"
    if any(w in t for w in ["yoga", "wellness", "health"]):
        return "outdoor"
    return "outdoor"

def normalize_date(raw_date, site):
    """Normalize date strings to a readable format."""
    if not raw_date:
        return ""
    d = raw_date.strip()
    
    # Handle Mt. Pleasant format like "03MAY"
    mp_match = re.match(r'^(\d{2})(JAN|FEB|MAR|APR|MAY|JUN|JUL|AUG|SEP|OCT|NOV|DEC)$', d, re.IGNORECASE)
    if mp_match:
        day = mp_match.group(1)
        month = mp_match.group(2).lower()
        months = {'jan':'Jan','feb':'Feb','mar':'Mar','apr':'Apr','may':'May','jun':'Jun',
                  'jul':'Jul','aug':'Aug','sep':'Sep','oct':'Oct','nov':'Nov','dec':'Dec'}
        return f"{months[month]} {day}"
    
    # Already clean
    return d

def format_time(raw_time):
    """Format time strings nicely."""
    if not raw_time or raw_time in ("", "All day"):
        return raw_time if raw_time else ""
    
    # Convert 24h to 12h format
    t = raw_time.strip()
    if re.match(r'^\d{2}:\d{2}$', t):
        hour, minute = int(t.split(':')[0]), int(t.split(':')[1])
        if hour == 0:
            return f"12:{minute:02d} AM"
        elif hour < 12:
            return f"{hour}:{minute:02d} AM"
        elif hour == 12:
            return f"12:{minute:02d} PM"
        else:
            return f"{hour-12}:{minute:02d} PM"
    
    return t

# ============================================================
# MERGE ALL EVENTS
# ============================================================

all_events = []
site_stats = {}

# Process Detroit Metro
det_seen = set()
for e in detroit_raw:
    key = (e['title'].lower(), e['url'])
    if key in det_seen:
        continue
    det_seen.add(key)
    lat, lon = lookup_coords(e.get('location', ''), "Detroit Metro")
    all_events.append({
        "title": e['title'],
        "date": e.get('date', ''),
        "time": e.get('time', ''),
        "location": e.get('location', ''),
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], e.get('location', '')),
        "url": e['url'],
        "site": "Detroit Metro"
    })
site_stats["Detroit Metro"] = len(det_seen)

# Process South Haven
sh_seen = set()
for e in south_haven_raw:
    key = (e['title'].lower(), e['url'])
    if key in sh_seen:
        continue
    sh_seen.add(key)
    lat, lon = lookup_coords("", "South Haven")  # Location not in listing view
    date_str = e.get('dateStart', '')
    time_str = format_time(e.get('time', ''))
    all_events.append({
        "title": e['title'],
        "date": date_str,
        "time": time_str,
        "location": "South Haven, MI",
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], "", time_str),
        "url": e['url'],
        "site": "South Haven"
    })
site_stats["South Haven"] = len(sh_seen)

# Process Traverse City
tc_seen = set()
for e in traverse_city_raw:
    key = (e['title'].lower(), e['url'])
    if key in tc_seen:
        continue
    tc_seen.add(key)
    lat, lon = lookup_coords(e.get('location', ''), "Traverse City")
    all_events.append({
        "title": e['title'],
        "date": e.get('date', ''),
        "time": "",
        "location": e.get('location', 'Traverse City, MI'),
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], e.get('location', '')),
        "url": e['url'] if e['url'].startswith('http') else f"https://www.traversecity.com{e['url']}",
        "site": "Traverse City"
    })
site_stats["Traverse City"] = len(tc_seen)

# Process Grand Haven
gh_seen = set()
for e in grand_haven_raw:
    key = (e['title'].lower(), e['url'])
    if key in gh_seen:
        continue
    gh_seen.add(key)
    lat, lon = lookup_coords(e.get('title', ''), "Grand Haven")
    all_events.append({
        "title": e['title'],
        "date": e.get('date', ''),
        "time": e.get('time', ''),
        "location": "Grand Haven, MI",
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], ""),
        "url": e['url'],
        "site": "Grand Haven"
    })
site_stats["Grand Haven"] = len(gh_seen)

# Process Mt. Pleasant
mp_seen = set()
for e in mt_pleasant_raw:
    key = (e['title'].lower(), e['url'])
    if key in mp_seen:
        continue
    mp_seen.add(key)
    lat, lon = lookup_coords("", "Mt. Pleasant")
    all_events.append({
        "title": e['title'],
        "date": normalize_date(e.get('date', ''), "Mt. Pleasant"),
        "time": e.get('time', ''),
        "location": "Mt. Pleasant, MI",
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], ""),
        "url": e['url'],
        "site": "Mt. Pleasant"
    })
site_stats["Mt. Pleasant"] = len(mp_seen)

# Process Battle Creek
bc_seen = set()
for e in battle_creek_raw:
    key = (e['title'].lower(), e['url'])
    if key in bc_seen:
        continue
    bc_seen.add(key)
    lat, lon = lookup_coords(e.get('location', ''), "Battle Creek")
    all_events.append({
        "title": e['title'],
        "date": e.get('date', ''),
        "time": "",
        "location": e.get('location', 'Battle Creek, MI'),
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], e.get('location', '')),
        "url": e['url'],
        "site": "Battle Creek"
    })
site_stats["Battle Creek"] = len(bc_seen)

# Process Grand Rapids - deduplicate
gr_seen = set()
for e in grand_rapids_raw:
    key = (e['title'].lower(), e['url'])
    if key in gr_seen:
        continue
    gr_seen.add(key)
    lat, lon = lookup_coords(e.get('location', ''), "Grand Rapids")
    all_events.append({
        "title": e['title'],
        "date": e.get('date', ''),
        "time": "",
        "location": e.get('location', 'Grand Rapids, MI'),
        "lat": lat,
        "lon": lon,
        "category": categorize(e['title'], e.get('location', '')),
        "url": e['url'],
        "site": "Grand Rapids"
    })
site_stats["Grand Rapids"] = len(gr_seen)

print(f"Total unique events: {len(all_events)}")
for site, count in site_stats.items():
    print(f"  {site}: {count}")

# Write events JSON
os.makedirs("/home/tong/workspace/pocket/events", exist_ok=True)
with open("/home/tong/workspace/pocket/events/events_final.json", "w") as f:
    json.dump(all_events, f, indent=2, ensure_ascii=False)
print(f"\nWrote events_final.json with {len(all_events)} events")

# ============================================================
# UPDATE HTML MAP
# ============================================================

template_path = "/home/tong/workspace/pocket/events/hn_events_map_2026-05-03.html"
output_path = "/home/tong/workspace/pocket/events/events_map_2026-05-07.html"

with open(template_path, "r") as f:
    html = f.read()

# Update title
html = html.replace("Mid Michigan & Lake Michigan Events Map - May 2026", 
                     "Lake Michigan Weekend Events Map - May 2026")

# Replace the embedded events JSON
start = html.find('const events = [')
if start == -1:
    print("ERROR: Could not find 'const events = [' in template!")
    exit(1)

# Find the closing ]; - search for the pattern after the events array
# The events array ends with ]; on line 576
end = html.find('\n\n    const categoryColors', start + 200)
if end == -1:
    # Fallback: find the ]; before const categoryColors
    end = html.find('];', start + 100)
    # But make sure we find the right one (end of the events array)
    # The events JSON is on one line, so find the newline after ]
    end = html.find('\n', html.find('],', start + 100))

new_events_json = json.dumps(all_events, ensure_ascii=False)
html = html[:start] + f'const events = {new_events_json};' + html[end:]

# Update event count badge
old_count_match = re.search(r'<span id="event-count">(\d+)', html)
if old_count_match:
    html = html[:old_count_match.start(1)] + str(len(all_events)) + html[old_count_match.end(1):]
else:
    # Try alternative patterns
    old_count_match = re.search(r'(\d+) Events', html)
    if old_count_match:
        html = html[:old_count_match.start(1)] + str(len(all_events)) + html[old_count_match.end(1):]

with open(output_path, "w") as f:
    f.write(html)

print(f"Wrote {output_path}")

# Verify the embedded JSON
with open(output_path, "r") as f:
    verify_html = f.read()
    
start2 = verify_html.find('const events = [')
end2 = verify_html.find('];', start2 + 100)
embedded_json = verify_html[start2 + len('const events = '):end2]
verify_events = json.loads(embedded_json + ']')
print(f"Verified: {len(verify_events)} events embedded in HTML")

# ============================================================
# GENERATE DISCORD SUMMARY
# ============================================================

summary = "🗺️ **Weekend Events Update — 2026-05-07**\n\n"

# Detroit events
det_events = [e for e in all_events if e['site'] == 'Detroit Metro']
summary += f"🏙️ **Detroit Metro** ({len(det_events)} events)\n"
for e in det_events[:8]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
if len(det_events) > 8:
    summary += f"• ...and {len(det_events) - 8} more\n"
summary += "\n"

# South Haven events
sh_events = [e for e in all_events if e['site'] == 'South Haven']
summary += f"🌊 **South Haven** ({len(sh_events)} events)\n"
for e in sh_events[:5]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

# Traverse City events
tc_events = [e for e in all_events if e['site'] == 'Traverse City']
summary += f"🍇 **Traverse City** ({len(tc_events)} events)\n"
for e in tc_events[:5]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

# Grand Haven events
gh_events = [e for e in all_events if e['site'] == 'Grand Haven']
summary += f"🎢 **Grand Haven** ({len(gh_events)} events)\n"
for e in gh_events[:5]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

# Mt. Pleasant events
mp_events = [e for e in all_events if e['site'] == 'Mt. Pleasant']
summary += f"🎓 **Mt. Pleasant** ({len(mp_events)} events)\n"
for e in mp_events[:5]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

# Battle Creek events
bc_events = [e for e in all_events if e['site'] == 'Battle Creek']
summary += f"🌾 **Battle Creek** ({len(bc_events)} events)\n"
for e in bc_events[:5]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

# Grand Rapids events
gr_events = [e for e in all_events if e['site'] == 'Grand Rapids']
summary += f"🏛️ **Grand Rapids** ({len(gr_events)} events)\n"
for e in gr_events[:8]:
    time_str = f" ⏰ {e['time']}" if e.get('time') else ""
    summary += f"• [{e['title']}]({e['url']}) — {e['date']} @ {e['location']}{time_str}\n"
summary += "\n"

summary += f"📊 **Total: {len(all_events)} events across 7 regions**\n"
summary += f"🗺️ **Interactive map:** https://zhangt58.github.io/pocket/events/\n\n"
summary += "MAP UPDATED & COMMITTED TO REPO ✓"

print("\n" + "="*60)
print("DISCORD SUMMARY:")
print("="*60)
print(summary)
