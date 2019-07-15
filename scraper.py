from bs4 import BeautifulSoup as soup
from urllib.request import Request, urlopen
import re
from nltk.corpus import stopwords
from geopy.geocoders import Nominatim
import requests

# input coordinates of device in DD. CANNOT BE IN DMS OR PROGRAM WILL NOT WORK
# example coordinates are for Oracle Arena (should return Shawn Mendes)
GPSReturn = '37.7503° N, 122.2030° W'
dateReturn = 'Sun, Jul 14'
timeReturn = '2:30 PM'
USER_AGENT = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36'}

# cleans HTML tags from string


def cleanRequest(clientRequest: str):
    partlyCleaned = re.sub(re.compile('<.*?>'), '', str(clientRequest))
    cleanedRequest = re.sub('[^A-Za-z0-9]+', ' ', partlyCleaned)
    return cleanedRequest

# cuts full address string into necessary segment e.g. (SalesForce Tower, 415, Mission Street, ... to SalesForce Tower)


def relevantAddress(fullAddress: str):
    locationEnd = fullAddress.find(',')
    locationName = fullAddress[0:locationEnd]
    return locationName

# fetches HTML of Google Search query page


def fetch_results(search_term, number_results, language_code):
    assert isinstance(search_term, str), 'Search term must be a string'
    assert isinstance(
        number_results, int), 'Number of results must be an integer'

    escaped_search_term = search_term.replace(' ', '+')
    google_url = 'https://www.google.com/search?q={}&num={}&hl={}'.format(
        escaped_search_term, number_results, language_code)
    response = requests.get(google_url, headers=USER_AGENT)
    response.raise_for_status()

    return response.text

# takes in GPS coordinates and returns the search query


def searchResult(coordinates: str):
    geolocator = Nominatim(user_agent="app")
    location = geolocator.reverse(coordinates)
    locationAddress = location.address
    locationAddressString = str(locationAddress)
    searchLocation = relevantAddress(locationAddressString)

    return searchLocation

# parses web for events at given location


def eventFinder(address: str):
    eventsSearch = address + ' events'
    webpage = fetch_results(eventsSearch, 10, 'en')
    page = soup(webpage, "html.parser")  # parses HTML file

    if ((page.find_all(class_="ravrDc") != [])):
        listOfSingleEventBoxes = page.find_all(class_="rl_item rl_item_base")

        if (int(len(listOfSingleEventBoxes)) != 0):
            soupOfEventBoxes = soup(str(listOfSingleEventBoxes), "html.parser")
            eventDates = soupOfEventBoxes.find_all(class_="aXUuyd")
            stringOfEventDates = cleanRequest(str(eventDates))
            positionInString = stringOfEventDates.find(dateReturn)
            dateString = stringOfEventDates[positionInString:(
                positionInString+len(dateReturn))]

            if (dateString != []):
                eventDate = soupOfEventBoxes.find_all(string=dateReturn)
                if(len(eventDate) > 0):
                    dateAndTimeBox = eventDate[0].parent.parent.parent
                    bigBox = dateAndTimeBox.next_sibling
                    eventName = cleanRequest(
                        str(bigBox.find_all(class_="title")))
                    return eventName
                else:
                    return None
            else:
                return None

        else:
            return None

    elif (page.find_all(class_="AxJnmb") is not []):
        allEventsBox = page.find_all(class_="AxJnmb")
        soupOfAllEventsBox = soup(str(allEventsBox), "html.parser")
        listOfSingleEventBoxes = soupOfAllEventsBox.find_all(
            class_="PZPZlf kno-fb-ctx")

        if (int(len(listOfSingleEventBoxes)) != 0):
            soupOfEventBoxes = soup(str(listOfSingleEventBoxes), "html.parser")
            eventDates = soupOfEventBoxes.find_all(class_="aXUuyd")
            stringOfEventDates = str(eventDates)
            positionInString = stringOfEventDates.find(dateReturn)
            dateString = stringOfEventDates[positionInString:(
                positionInString+len(dateReturn))]

            if (dateString != ''):
                eventDate = soupOfEventBoxes.find_all(string=dateReturn)
                dateAndTimeBox = eventDate[0].parent.parent.parent
                bigBox = dateAndTimeBox.next_sibling
                eventName = cleanRequest(str(bigBox.find_all(class_="title")))
                return eventName
            else:
                return None
        else:

            return None
    else:
        return None


print(eventFinder(searchResult(GPSReturn)))
