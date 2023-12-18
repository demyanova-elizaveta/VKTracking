import re
import sys
import time
import traceback

import sqlite3
from datetime import date
from hashlib import sha256


class DBHandler:
    def __init__(self):
        self.comments_info = []
        self.sqlite_connection = sqlite3.connect('sqlite_python.db')
        self.cursor = self.sqlite_connection.cursor()
        self.deleted_count = 0
        self.updated_count = 0
        self.added_count = 0
        self.unable_to_process = 0
        print("database connected to SQLite")

    def update_likes(self, id, posts, table_name, id_name, object):
        split_posts = list(map(int, posts.split(',')))

        sqlite_select_query = f"""SELECT * from {table_name}"""
        self.cursor.execute(sqlite_select_query)
        records = self.cursor.fetchall()
        old_data = set()
        for record in records:
            if record[0] == int(id) and record[1] in split_posts:
                old_data.add((record[0], record[1], record[2]))

        new_data = set()
        for post in split_posts:
            users_ids, count = object.get_likes_on_post(post)
            if count > 1000:
                for i in range(1000, count, 1000):
                    more_ids = object.get_likes_on_post(post, offset=i)
                    users_ids += more_ids[0]
            for user_id in users_ids:
                hash_obj = sha256(str(user_id).encode('ASCII')).hexdigest()
                new_data.add((int(id), int(post), hash_obj))

        delete_set = old_data.difference(new_data)
        add_set = new_data.difference(old_data)
        update_set = new_data.intersection(old_data)

        for item in delete_set:
            try:
                sqlite_insert_query = f"DELETE FROM {table_name} WHERE {id_name}=%s AND post_id=%s AND user_id='%s'" % (
                    item[0], item[1], item[2])
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.deleted_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

        for item in add_set:
            try:
                sqlite_insert_query = f'INSERT INTO {table_name}({id_name}, post_id, user_id, refreshed_date) VALUES ' \
                                      '("%s", "%s", ' \
                                      '"%s", "%s")' % (
                                          item[0], item[1], item[2], date.today())
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.added_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

        for item in update_set:
            try:
                sqlite_update_query = f"UPDATE {table_name} SET refreshed_date='%s' WHERE {id_name}=%s AND post_id=%s AND user_id='%s'" % (
                    date.today(), item[0], item[1], item[2])
                self.cursor.execute(sqlite_update_query)
                self.sqlite_connection.commit()
                self.updated_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

    def update_comments(self, id, posts, table_name, id_name, object, comment_id=0):
        split_posts = list(map(int, posts.split(',')))

        sqlite_select_query = f"""SELECT * from {table_name}"""
        self.cursor.execute(sqlite_select_query)
        records = self.cursor.fetchall()
        old_data = set()
        for record in records:
            if record[0] == int(id) and record[1] in split_posts:
                old_data.add((record[0], record[1], record[3], record[2], record[4],
                              record[5], record[7]))  # community_id, post_id, comment_id, user_id, comment_date, parent_id, comment_text

        new_data = set()
        for post_id in split_posts:
            if 'communities' in table_name:
                self.update_specific_posts(id, '-'+str(id)+'_'+str(post_id), 'communitiesPosts', 'community_id', object)
            elif 'profiles' in table_name:
                self.update_specific_posts(id, str(id) + '_' + str(post_id), 'profilesPosts', 'profile_id', object)
            object.last_comments_for_post = []
            count = object.get_comments_count(post_id)
            object.get_comments_on_post(post_id, comment_id=comment_id)
            if count > 100:
                for i in range(100, count, 100):
                    object.get_comments_on_post(post_id, offset=i, comment_id=comment_id)
            self.comments_info = object.last_comments_for_post
            for comment in self.comments_info:
                hash_obj = sha256(str(comment[1]).encode('ASCII')).hexdigest()  # comment[1] - user_id

                pattern = r"\[id\d+\|[A-Za-zА-Яа-я]+\], "
                comment_text_without_personal_data = re.sub(pattern, "", comment[4])

                new_data.add((int(id), int(post_id), comment[0], hash_obj,
                              time.strftime('%Y-%m-%d', time.localtime(int(comment[2]))),
                              comment[3], comment_text_without_personal_data))  # community_id, post_id, comment_id, user_id, comment_date, parent_id, comment_text

        old_set = old_data.difference(new_data)
        new_set = new_data.difference(old_data)
        update_set = new_data.intersection(old_data)

        for item in old_set:
            try:
                sqlite_insert_query = f"DELETE FROM {table_name} WHERE {id_name}=%s AND post_id=%s AND comment_id='%s'" % (
                    item[0], item[1], item[2])
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.deleted_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

        for item in new_set:
            try:
                sqlite_insert_query = f'INSERT INTO {table_name}({id_name}, post_id, comment_id, user_id, comment_date, refreshed_date, parent_id, comment_text) VALUES ' \
                                      "('%s', '%s', '%s', '%s', '%s', '%s', '%s', '%s')" % (
                                          item[0], item[1], item[2], item[3], item[4], date.today(), item[5], item[6])
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.added_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

        for item in update_set:
            try:
                sqlite_update_query = f"UPDATE {table_name} SET refreshed_date='%s' WHERE {id_name}=%s AND post_id=%s AND comment_id='%s'" \
                                      % (date.today(), item[0], item[1], item[2])
                self.cursor.execute(sqlite_update_query)
                self.sqlite_connection.commit()
                self.updated_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(item[1], error)

    def update_last_posts(self, id, count, table_name, id_name, object):
        sqlite_select_query = f"""SELECT * from {table_name}"""
        self.cursor.execute(sqlite_select_query)
        records = self.cursor.fetchall()
        old_data = set()
        for record in records:
            if record[0] == int(id):
                old_data.add((record[0], record[1]))

        new_posts = object.get_last_posts(count)
        posts_dict = {}
        for post in new_posts:
            posts_dict[(int(id), post[0])] = (post[1], post[2], post[3])

        new_set = set(posts_dict.keys()).difference(old_data)
        update_set = old_data.intersection(set(posts_dict.keys()))

        for key in new_set:
            try:
                sqlite_insert_query = f'INSERT INTO {table_name}({id_name}, post_id, post_date, refreshed_date, is_deleted, post_theme) VALUES ' \
                                      '("%s", "%s", ' \
                                      '"%s", "%s", "%s", "%s")' % (
                                          key[0], key[1], posts_dict[key][0], date.today(), posts_dict[key][1],
                                          posts_dict[key][2])
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.added_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(key[1], error)

        for key in update_set:
            try:
                sqlite_update_query = f'UPDATE {table_name} SET refreshed_date="%s", is_deleted=%s, post_theme="%s" WHERE {id_name}=%s ' \
                                      f' AND post_id=%s' % (
                                          date.today(), posts_dict[key][1], posts_dict[key][2], key[0], key[1])
                self.cursor.execute(sqlite_update_query)
                self.sqlite_connection.commit()
                self.updated_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(key[1], error)

    def update_specific_posts(self, id, ids_list, table_name, id_name, object):
        sqlite_select_query = f"""SELECT * from {table_name}"""
        self.cursor.execute(sqlite_select_query)
        records = self.cursor.fetchall()
        old_data = set()
        for record in records:
            if record[0] == int(id):
                old_data.add((record[0], record[1]))

        new_posts = object.get_specific_posts(ids_list)
        posts_dict = {}
        for post in new_posts:
            posts_dict[(int(id), post[0])] = (post[1], post[2], post[3])

        new_set = set(posts_dict.keys()).difference(old_data)
        update_set = old_data.intersection(set(posts_dict.keys()))

        # sql = 'SELECT user_id, count(user_id) FROM communitiesComments WHERE community_id=15755094 GROUP BY user_id ORDER BY COUNT(user_id) DESC'
        # df = pd.DataFrame(pd.read_sql(sql, self.sqlite_connection))

        for key in new_set:
            try:
                sqlite_insert_query = f'INSERT INTO {table_name}({id_name}, post_id, post_date, refreshed_date, is_deleted, post_theme) VALUES ' \
                                      '("%s", "%s", ' \
                                      '"%s", "%s", "%s", "%s")' % (
                                          key[0], key[1], posts_dict[key][0], date.today(), posts_dict[key][1],
                                          posts_dict[key][2])
                self.cursor.execute(sqlite_insert_query)
                self.sqlite_connection.commit()
                self.added_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(key[1], error)

        for key in update_set:
            try:
                sqlite_update_query = f'UPDATE {table_name} SET refreshed_date="%s", is_deleted=%s, post_theme="%s" WHERE {id_name}=%s ' \
                                      f' AND post_id=%s' % (
                                          date.today(), posts_dict[key][1], posts_dict[key][2], key[0], key[1])
                self.cursor.execute(sqlite_update_query)
                self.sqlite_connection.commit()
                self.updated_count += 1
            except sqlite3.Error as error:
                self.print_exception_info(key[1], error)

    def print_exception_info(self, id, error):
        self.unable_to_process += 1
        print('class: ', error.__class__)
        print('exception', error.args)
        print('exception data SQLite: ')
        exc_type, exc_value, exc_tb = sys.exc_info()
        print(traceback.format_exception(exc_type, exc_value, exc_tb))