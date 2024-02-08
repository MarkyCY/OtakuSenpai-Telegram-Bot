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
    	nextAiringEpisode {
    		episode
            airingAt
    	}
    	genres
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
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")
    
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
        genres
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
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")
    
    return response.json()

def searchCharacter(name):
    query = '''
    query ($search: String) {
      Character(search: $search) {
        name {
          full
          native
        }
        image {
          large
        }
        description(asHtml: true)
        gender
        dateOfBirth {
          year
          month
          day
        }
        age
        bloodType
        isFavourite
        siteUrl
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
    try:
        response = requests.post(url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")
    
    return response.json()
