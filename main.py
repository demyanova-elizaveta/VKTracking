import re
import time
from abc import abstractmethod

import requests
from settings import api_v


class RequestHandler:
    request_count = 0

    @staticmethod
    def create_request_url(method_name, parameters, token):
        req_url = 'https://api.vk.com/method/{method_name}?{parameters}&v={api_v}&access_token={token}'.format(
            method_name=method_name, parameters=parameters, api_v=api_v, token=token)

        return req_url

    @staticmethod
    def time_process():
        time.sleep(1)
        RequestHandler.request_count = 0


class VkException(Exception):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return self.message


def create_parts(lst, n=25):
    return (lst[i:i + n] for i in iter(range(0, len(lst), n)))


def create_targets(lst):
    return ",".join(str(id) for id in lst)


class ImplementReactions:
    @abstractmethod
    def get_likes_on_post(self, post_id, count, offset):
        pass

    @abstractmethod
    def get_comments_on_post(self, post_id):
        pass


class GroupVK(ImplementReactions):

    def __init__(self, id, given_token):
        self.token = given_token
        self.group_id = id
        self.name, self.description = self.get_group_description(self.group_id)

        self.all_members = self.get_group_members()
        self.members_count = len(self.all_members)
        self.last_comments_for_post = []

    def get_group_description(self, id):
        r = requests.get(
            RequestHandler.create_request_url('groups.getById', 'group_id=%s&fields=description' % id, self.token)).json()[
            'response']['groups'][0]
        return r['name'], r['description']

    def get_group_members(self):
        # try:
        r = requests.get(RequestHandler.create_request_url('groups.getMembers',
                                                           'group_id=%s&fields=uid,first_name,last_name,photo,country,city,sex,bdate'
                                                           % self.group_id, self.token)).json()['response']
        return {item['id']: item for item in r['items']}
        # except VkException as e:
        #     sys.exit(e)

    def get_friends(self, id):
        try:
            r = requests.get(RequestHandler.create_request_url('friends.get',
                                                           'user_id=%s&fields=uid,first_name,last_name,photo,country,city,sex,bdate'
                                                           % id, self.token)).json()['response']
            return {item['id']: item for item in r['items']}
        except Exception:
             print('get_friends not processed on group %s on user %s' % (self.group_id, id))

    # def get_common_vk_members(self):
    #
    #     self.all_members = self.get_group_members()
    #     set_members = set(self.all_members)
    #
    #     result = []
    #
    #     for i in create_parts(list(self.all_members.keys())):
    #         targets = create_targets(i)
    #         try:
    #             r = requests.get(create_request_url('execute.getGroupConnections',
    #                                                 "targets='%s'" % targets)).json()['response']
    #             for j, id in enumerate(i):
    #                 if self.all_members[id]['can_access_closed'] and not self.all_members[i]['is_closed']:
    #                     if r[j] != 0:
    #                         friends_i = r[j]['items']
    #                         set_friends_for_i = set(friends_i)
    #                         common_friends = set_members & set_friends_for_i
    #
    #                         result.append((self.all_members[id],
    #                                        [self.all_members[k] for k in common_friends] if common_friends else None))
    #                     else:
    #                         sys.exit('execute.getGroupConnections 29 error')
    #                 # else:
    #                 #     result.append((self.all_members[id], None)) #тут можно как-то элемент выделить, что профиль закрыт у него
    #         except VkException:
    #             sys.exit('execute.getGroupConnections response error')
    #
    #     return result

    def get_common_vk_members(self):
        result = []

        for i in list(self.all_members.keys()):
            if RequestHandler.request_count == 3:
                RequestHandler.time_process()
            RequestHandler.request_count += 1
            result.append(self.process_person(i))

        return result

    def process_person(self, i):

        if self.all_members[i]['can_access_closed'] and not self.all_members[i]['is_closed']:
            friends_i = self.get_friends(i)
            # self.all_friends.update({self.all_members[i]['id']: friends_i})  # заполняем словарь друзей

            if friends_i is not None:
                set_members = set(self.all_members)
                set_friends_for_i = set(friends_i)

                common_friends = set_members & set_friends_for_i

                return self.all_members[i], [self.all_members[j] for j in common_friends] if common_friends else None
            else:
                return self.all_members[i], None
        else:
            return self.all_members[i], None

    def get_last_posts(self, count):
        result = []
        r = requests.get(
            RequestHandler.create_request_url('wall.get', 'owner_id=-%s&count=%s' % (self.group_id, count), self.token)).json()[
            'response']['items']
        for item in r:
            type = re.search(r"^.+?[\w\d]{2,}[^\w]?[.?!\n]", item['text'])
            result.append((item['id'], item['date'], 0,
                           type.group().replace("'", '').replace('"', '') if type is not None else item['text'].replace(
                               "'", '').replace('"', '')))
        return result

    def get_specific_posts(self, posts):
        result = []
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getById', 'posts=%s' % posts, self.token)).json()['response'][
                'items']
            RequestHandler.time_process()
            for item in r:
                type = re.search(r"^.+?[\w\d]{2,}[^\w]?[.?!\n]", item['text'])
                if 'is_deleted' in item.keys():
                    result.append((item['id'], item['date'], 1,
                                   type.group().replace("'", '').replace('"', '') if type is not None else item[
                                       'text'].replace("'", '').replace('"', '')))
                else:
                    result.append((item['id'], item['date'], 0,
                                   type.group().replace("'", '').replace('"', '') if type is not None else item[
                                       'text'].replace("'", '').replace('"', '')))
            return result
        except Exception:
            print(('get_specific_posts method failed for posts %s' % posts))

    def get_likes_on_post(self, post_id, count=1000, offset=0):
        r = requests.get(RequestHandler.create_request_url('likes.getList', 'type=post&owner_id=-%s&item_id=%s&count'
                                                                            '=%s&offset=%s'
                                                           % (self.group_id, post_id, count, offset), self.token)).json()[
            'response']
        return [item for item in r['items']], r['count']

    def get_comments_count(self, post_id):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getComments',
                                                               'owner_id=-%s&post_id=%s'
                                                               % (self.group_id, post_id), self.token)).json()['response']
            return r['count']
        except Exception:
            print(("post's count with id %s not processed for group %s" % (post_id, self.group_id)))

    def get_posts_by_query(self, query, count=100, offset=0):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.search',
                                                               'owner_id=-%s&query=%s&owners_only=1&count=%s&offset=%s'
                                                               % (self.group_id, query, count,
                                                                  offset), self.token)).json()['response']
            RequestHandler.time_process()
            return r
        except Exception:
            print('get_posts_by_query not processed on group %s with offset %s' % (self.group_id, offset))

    def get_comments_on_post(self, post_id, count=100, offset=0, comment_id=''):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getComments',
                                                               'owner_id=-%s&post_id=%s&comment_id=%s&count=%s&offset=%s'
                                                               % (self.group_id, post_id, comment_id, count,
                                                                  offset), self.token)).json()['response']
            RequestHandler.time_process()
            parent_id = {}
            for item in r['items']:
                if len(item['parents_stack']) > 0:
                    parent_id[item['id']] = item['parents_stack'][0]
                else:
                    parent_id[item['id']] = 0
                    self.get_comments_on_post(post_id, comment_id=item['id'])
            self.last_comments_for_post += [
                (item['id'], item['from_id'], item['date'], parent_id[item['id']], item['text']) for item in r['items']]

        except Exception:
            print(("post's comments with id %s not processed for group %s" % (post_id, self.group_id)))


class UserVK(ImplementReactions):

    def __init__(self, id, given_token):
        self.token = given_token
        self.user_id = id

        self.my_name, self.my_last_name, self.photo = self.get_base_info(self.user_id)
        self.groups = self.get_user_groups(self.user_id)

        self.all_friends = self.get_friends()
        self.friends_count = len(self.all_friends)
        self.last_comments_for_post = []

    def get_base_info(self, id):
        # try:
        r = requests.get(RequestHandler.create_request_url('users.get', 'user_id=%s&fields=photo' % id, self.token)).json()
        r = r['response'][0]
        # Проверяем, если id из settings.py не деактивирован
        if 'deactivated' in r.keys():
            raise VkException("User deactivated")
        return r['first_name'], r['last_name'], r['photo']
        # except VkException:
        #     sys.exit('users.get error')

    def get_user_groups(self, id):
        try:
            r = requests.get(RequestHandler.create_request_url('groups.get', 'user_id=%s&extended=1' % id, self.token)).json()[
            'response']
            return [item['name'] for item in r['items']]
        except Exception:
            print('get_user_groups not processed on processing user %s' % self.user_id)

    def get_friends(self):
        try:
            r = requests.get(RequestHandler.create_request_url('friends.get',
                                                           'user_id=%s&fields=uid,first_name,last_name,photo,'
                                                           'country,city,sex,bdate '
                                                           % self.user_id, self.token)).json()['response']
            return {item['id']: item for item in r['items']}
        except Exception:
            print('get_friends not processed on processing user %s on user-friend %s' % (self.user_id, id))

        # r = list(filter((lambda x: 'deactivated' not in x.keys()), r['items']))

    # def get_common_friends(self):
    #
    #     self.all_friends = self.get_friends()
    #     result = []
    #     for i in create_parts(list(self.all_friends.keys())):
    #         targets = create_targets(i)
    #         try:
    #             r = requests.get(RequestHandler.create_request_url('execute.getMutual',
    #                                                                "source=%s&targets='%s'" % (
    #                                                                self.user_id, targets))).json()['response']
    #             time.sleep(1)
    #             for j, id in enumerate(i):
    #                 result.append((self.all_friends[int(id)], [self.all_friends[int(i)] for i in r[j]] if r[j] else None))
    #         except VkException:
    #             sys.exit('execute.getMutual error')
    #
    #     return result

    def get_common_friends(self):
        result = []

        for i in list(self.all_friends.keys()):
            try:
                if self.all_friends[i]['can_access_closed'] and not self.all_friends[i]['is_closed']:
                    # if RequestHandler.request_count == 2:
                    RequestHandler.time_process()
                    # RequestHandler.request_count += 1
                    r = requests.get(RequestHandler.create_request_url('friends.getMutual',
                                                                       "source_uid=%s&target_uid=%s" % (
                                                                           self.user_id, i), self.token)).json()['response']
                    result.append((self.all_friends[i], [self.all_friends[int(j)] for j in r] if r else None))
            except Exception:
                print('execute.getMutual error')
        return result

    def get_last_posts(self, count):
        result = []
        r = requests.get(
            RequestHandler.create_request_url('wall.get', 'owner_id=%s&count=%s' % (self.user_id, count), self.token)).json()[
            'response']
        for item in r:
            type = re.search(r"^.+?[\w\d]{2,}[^\w]?[.?!\n]", item['text'])
            result.append((item['id'], item['date'], 0,
                           type.group().replace("'", '').replace('"', '') if type is not None else item['text'].replace(
                               "'", '').replace('"', '')))
        return result

    def get_specific_posts(self, posts):
        result = []
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getById', 'posts=%s' % posts, self.token)).json()['response'][
                'items']
            RequestHandler.time_process()
            for item in r:
                type = re.search(r"^.+?[\w\d]{2,}[^\w]?[.?!\n]", item['text'])
                if 'is_deleted' in item.keys():
                    result.append((item['id'], item['date'], 1,
                                   type.group().replace("'", '').replace('"', '') if type is not None else item[
                                       'text'].replace("'", '').replace('"', '')))
                else:
                    result.append((item['id'], item['date'], 0,
                                   type.group().replace("'", '').replace('"', '') if type is not None else item[
                                       'text'].replace("'", '').replace('"', '')))
            return result
        except Exception:
            print(('get_specific_posts method failed for posts %s' % posts))

    def get_likes_on_post(self, post_id, count=1000, offset=0):
        r = requests.get(RequestHandler.create_request_url('likes.getList', 'type=post&owner_id=%s&item_id=%s&count'
                                                                            '=%s&offset=%s'
                                                           % (self.user_id, post_id, count, offset), self.token)).json()['response']
        return [item for item in r['items']], r['count']

    def get_comments_count(self, post_id):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getComments',
                                                               'owner_id=%s&post_id=%s'
                                                               % (self.user_id, post_id), self.token)).json()['response']
            return r['count']
        except Exception:
            print(("post %s not processed for user %s" % (post_id, self.user_id)))

    def get_posts_by_query(self, query, count=100, offset=0):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.search',
                                                               'owner_id=%s&query=%s&owners_only=1&count=%s&offset=%s'
                                                               % (self.user_id, query, count,
                                                                  offset), self.token)).json()['response']
            RequestHandler.time_process()
            return r
        except Exception:
            print('get_posts_by_query not processed on user %s with offset %s' % (self.user_id, offset))

    def get_comments_on_post(self, post_id, count=100, offset=0, comment_id=''):
        try:
            r = requests.get(RequestHandler.create_request_url('wall.getComments',
                                                               'owner_id=%s&post_id=%s&comment_id=%s&count=%s&offset=%s'
                                                               % (self.user_id, post_id, comment_id, count,
                                                                  offset), self.token)).json()['response']
            RequestHandler.time_process()
            parent_id = {}
            for item in r['items']:
                if len(item['parents_stack']) > 0:
                    parent_id[item['id']] = item['parents_stack'][0]
                else:
                    parent_id[item['id']] = 0
                    self.get_comments_on_post(post_id, comment_id=item['id'])
            self.last_comments_for_post += [
                (item['id'], item['from_id'], item['date'], parent_id[item['id']], item['text']) for item in r['items']]
        except Exception:
            print(("post's comments with id %s not processed for user %s" % (post_id, self.user_id)))
