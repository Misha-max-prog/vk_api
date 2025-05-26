import argparse
import requests

class VKAPIError(Exception):
    pass

class VKAPIClient:
    API_BASE_URL = 'https://api.vk.com/method/'

    def __init__(self, access_token, api_version='5.131'):
        self.access_token = access_token
        self.api_version = api_version

    def _make_request(self, method, params=None):
        url = f"{self.API_BASE_URL}{method}"
        params = params or {}
        params.update({
            'access_token': self.access_token,
            'v': self.api_version
        })

        try:
            response = requests.get(url, params=params, timeout=10)
            response.raise_for_status()
            data = response.json()

            if 'error' in data:
                error_msg = data['error'].get('error_msg', 'Unknown API error')
                raise VKAPIError(f"API Error: {error_msg}")
            return data['response']
        except requests.exceptions.ConnectionError:
            raise VKAPIError("Connection error: Could not connect to server.")
        except requests.exceptions.Timeout:
            raise VKAPIError("Request timed out.")
        except requests.exceptions.HTTPError as e:
            raise VKAPIError(f"HTTP error: {str(e)}")
        except requests.exceptions.RequestException as e:
            raise VKAPIError(f"Request failed: {str(e)}")

    def get_friends(self, user_id):
        params = {
            'user_id': user_id,
            'fields': 'first_name,last_name'
        }
        try:
            friends = self._make_request('friends.get', params)
            return [f"{friend['first_name']} {friend['last_name']}" for friend in friends['items']]
        except VKAPIError as e:
            print(f"Error fetching friends: {e}")
            return []

    def get_albums(self, user_id):
        params = {'owner_id': user_id}
        try:
            albums = self._make_request('photos.getAlbums', params)
            return [album['title'] for album in albums['items']]
        except VKAPIError as e:
            print(f"Error fetching albums: {e}")
            return []

def main():
    parser = argparse.ArgumentParser(description='Fetch user information from VK API')
    parser.add_argument('--token', required=True, help='VK OAuth Access Token')
    parser.add_argument('--user-id', required=True, help='VK User ID')
    parser.add_argument('--method', choices=['friends', 'albums'], required=True, help='Data to fetch')
    args = parser.parse_args()

    client = VKAPIClient(args.token)

    try:
        if args.method == 'friends':
            friends = client.get_friends(args.user_id)
            print("\nFriends list:")
            for friend in friends:
                print(f"- {friend}")
        elif args.method == 'albums':
            albums = client.get_albums(args.user_id)
            print("\nPhoto albums:")
            for album in albums:
                print(f"- {album}")
    except VKAPIError as e:
        print(f"Operation failed: {e}")

if __name__ == "__main__":
    main()
