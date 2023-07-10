import requests
from graphqlclient import GraphQLClient

url = 'https://graphql.anilist.co'

client = GraphQLClient(url)

def search_anime(name):
    query = '''
    query ($search: String) {
      Media(search: $search, type: ANIME) {
        id
        title {
            romaji
            english
            native
        }
        description
        coverImage {
            large
        }
        duration
        episodes
        endDate {
            year
            month
            day
        }
        status
        isAdult
      }
    }
    '''

    variables = {
        'search': name
    }

    #headers = {
    #    'Authorization': f'Bearer {api_key}'
    #}

    # Envía la solicitud a la API de AniList
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    return response.json()


def search_manga(name):
    query = '''
    query ($search: String) {
      Media(search: $search, type: MANGA) {
        id
        title {
            romaji
            english
            native
        }
        description
        coverImage {
            large
        }
        popularity
        endDate {
            year
            month
            day
        }
        status
        isAdult
      }
    }
    '''

    variables = {
        'search': name
    }

    #headers = {
    #    'Authorization': f'Bearer {api_key}'
    #}

    # Envía la solicitud a la API de AniList
    response = requests.post(url, json={'query': query, 'variables': variables})
    
    return response.json()

