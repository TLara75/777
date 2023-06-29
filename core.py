from pprint import pprint
import vk_api
from vk_api.exceptions import ApiError
from config import acces_token
from datetime import datetime

class VkTools:
    def __init__(self, acces_token):
        self.api = vk_api.VkApi(token=acces_token)

    def bdate_toage(self, bdate):
        user_year = bdate.split('.')[2]
        now = datetime.now().year
        age = now - int(user_year)
        return age

    def get_profile_info(self, user_id):

        try:
            info, = self.api.method('users.get',
                                      {'user_id': user_id,
                                       'fields': 'city,sex,relation,bdate'
                                       }
                                      )
        except ApiError as e:
            info = {}
            print(f'error = {e}')

        result = {'name': f"{info['first_name']} {info['last_name']}" if 'first_name'
                  in info and 'last_name' in info else None,
                  'sex': info.get('sex'),
                  'age': self.bdate_toage(info.get('bdate') ) if 'bdate' in info else None,
                  'city': info.get('city')['title'] if info.get('city') is not None else None
                  }
        return result

    def serch_users(self, params, offset):
        try:
            users = self.api.method('users.search',
                                    {'count': 10,
                                     'offset': offset,
                                     'age_from': params['age']-5,
                                     'age_to': params['age']+2,
                                     'sex': 1 if params['sex'] == 2 else 2,
                                     'hometown': params['city'],
                                     'has_photo': True,
                                     'status': 6,
                                     'is_closed': False
                                    }
                                    )
        except ApiError as e:
            users = []
            print(f'error = {e}')

        result = [{'name': f"{item['first_name']} {item['last_name']}",
                   'id': item['id']
                   } for item in users['items'] if item['is_closed'] is False
                  ]

        return result

    def get_photos(self, id):
        try:
            photos = self.api.method('photos.get',
                                       {'owner_id': id,
                                        'album_id': 'profile',
                                        'extended': 1
                                        }
                                       )
        except ApiError as e:
            photos = {}
            print(f'error = {e}')

        result = [
                 {'owner_id': item['owner_id'],
                  'id': item['id'],
                  'likes': item['likes']['count'],
                   'comments': item['comments']['count']
                  } for item in photos['items']
                  ]
        '''сортировка по лайкам и комментам'''
        result.sort(key=lambda x: x['likes']*10 + x['comments'], reverse=True)
        return result[:3]


if __name__ == '__main__':
    user_id = 789657038
    tools = VkTools(acces_token)
    params = tools.get_profile_info(user_id)
    users = tools.serch_users(params, 20)
    user = users.pop()
    photos = tools.get_photos(user['id'])

    pprint(users)