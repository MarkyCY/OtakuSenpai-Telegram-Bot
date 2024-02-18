import requests
from graphqlclient import GraphQLClient

url = 'https://graphql.anilist.co'

client = GraphQLClient(url)


def search_anime(name):
    query = '''
    query ($page: Int, $perPage: Int, $search: String) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
    media (search: $search, type: ANIME) {
        id
        title {
            romaji
        	english
        	native
            }
    	}
    }
}
    '''

    variables = {
        'search': name,
        "page": 1,
        "perPage": 8
    }

    # headers = {
    #    'Authorization': f'Bearer {api_key}'
    # }

    # Envía la solicitud a la API de AniList
    try:
        response = requests.post(
            url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")

    return response.json()

def search_anime_id(id):
    query = '''
    query ($id: Int) {
      Media(id: $id, type: ANIME) {
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
        bannerImage
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
        'id': id
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
    query ($page: Int, $perPage: Int, $search: String) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
    media (search: $search, type: MANGA) {
        id
        title {
            romaji
        	english
        	native
            }
    	}
    }
}
    '''

    variables = {
        'search': name,
        "page": 1,
        "perPage": 8
    }

    # headers = {
    #    'Authorization': f'Bearer {api_key}'
    # }

    # Envía la solicitud a la API de AniList
    try:
        response = requests.post(
            url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")

    return response.json()


def search_manga_id(id):
    query = '''
    query ($id: Int) {
      Media(id: $id, type: MANGA) {
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
        bannerImage
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
        'id': id
    }

    # headers = {
    #    'Authorization': f'Bearer {api_key}'
    # }

    # Envía la solicitud a la API de AniList
    try:
        response = requests.post(
            url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")

    return response.json()



def searchCharacter(name):
    query = '''
    query ($page: Int, $perPage: Int, $search: String) {
    Page (page: $page, perPage: $perPage) {
        pageInfo {
            total
            currentPage
            lastPage
            hasNextPage
            perPage
        }
      characters(search: $search) {
        id
        name {
          full
          native
            }
        }
    }
}
    '''

    variables = {
        'search': name,
        "page": 1,
        "perPage": 8
    }

    # headers = {
    #    'Authorization': f'Bearer {api_key}'
    # }

    # Envía la solicitud a la API de AniList
    try:
        response = requests.post(
            url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")

    return response.json()


def searchCharacterId(id):
    query = '''
    query ($id: Int) {
      Character(id: $id) {
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
        'id': id
    }

    # headers = {
    #    'Authorization': f'Bearer {api_key}'
    # }

    # Envía la solicitud a la API de AniList
    try:
        response = requests.post(
            url, json={'query': query, 'variables': variables})
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as error:
        print(f"Error al realizar la solicitud: {error}")
    except requests.exceptions.RequestException as error:
        print(f"Error de red: {error}")

    return response.json()
