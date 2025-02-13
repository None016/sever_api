import psycopg2
from psycopg2.extras import execute_values


class DB:
    def __init__(self, data_base):
        self.conn = psycopg2.connect(host='localhost',
                                     database=data_base,
                                     user='postgres',
                                     password='hiro12')

        self.cur = self.conn.cursor()

    def select_by(self, param, data):
        self.cur.execute(f"SELECT * FROM public.user WHERE {param} = %s", (data,))
        return self.cur.fetchone()

    def get_users(self):
        self.cur.execute("SELECT * FROM public.user")
        print(self.cur.fetchall())

    def get_user_id(self, email):
        answer = self.select_by("email", email)
        if answer is not None:
            return answer[0]
        else:
            return None

    def set_user(self, name, email, password):
        execute_values(self.cur, "INSERT INTO public.user(name, email, password) VALUES %s", [(name, email, password)])
        self.conn.commit()

    def check_is_reg(self, email):
        self.cur.execute(
            "SELECT EXISTS (SELECT * FROM public.user WHERE email = %s)",
            (email,)
        )
        return self.cur.fetchall()[0][0]

    def check_is_aut(self, email, password):
        return self.select_by("email", email)[-1] == password

    def get_files(self, id):
        self.cur.execute(
            "SELECT id_file, name_file, path FROM public.files WHERE id_users = %s",
            (id,)
        )
        return self.cur.fetchall()

    def get_file_name(self, id_file):
        self.cur.execute(
            "SELECT name_file FROM public.files WHERE id_file = %s",
            (id_file,)
        )
        return self.cur.fetchone()

    def __del__(self):
        self.conn.close()
        self.cur.close()

    def set_name(self, new_name_file, new_path, id_file):
        self.cur.execute(
            "UPDATE public.files SET name_file=%s, path=%s WHERE id_file=%s",
            (new_name_file, new_path, id_file)
        )
        self.conn.commit()

    def get_file(self, id_file):
        self.cur.execute(
            "SELECT name_file, path, id_users FROM public.files WHERE id_file = %s",
            (id_file,)
        )
        return self.cur.fetchone()

    def check_download(self, id_file, id_user):
        try:
            self.cur.execute(
                "SELECT * FROM public.download_rights WHERE id_file = %s AND id_user = %s",
                (id_file, id_user)
            )
            if self.cur.fetchone() is not None:
                return True
            else:
                return False
        except:
            return False

    def get_access_download(self, id_file, id_user):
        try:
            self.cur.execute(
                "SELECT id_user FROM public.download_rights WHERE id_file = %s AND id_user != %s",
                (id_file, id_user)
            )
            return self.cur.fetchall()
        except:
            return None

    def del_user_from_access_list(self, id_file, id_user):
        try:
            self.cur.execute(
                "DELETE FROM public.download_rights	WHERE id_file = %s AND id_user = %s;",
                (id_file, id_user)
            )
            self.conn.commit()
        except:
            print("Ошибка удаления 'del_user_from_access_list'")

    def add_user_access_list(self, id_file, id_user):
        try:
            self.cur.execute(
                "INSERT INTO public.download_rights(id_file, id_user) VALUES (%s, %s);",
                (id_file, id_user)
            )
            self.conn.commit()
        except:
            print("Ошибка добавления")

    def del_file(self, id_file):
        try:
            self.cur.execute(
                "DELETE FROM public.files WHERE id_file = %s",
                (id_file,)
            )
            self.conn.commit()
        except:
            print("Ошибка удаления файла")

    def get_frend_file(self, id_user):
        try:
            self.cur.execute(
                "SELECT id_file FROM public.download_rights WHERE id_user = %s",
                (id_user,)
            )
            return self.cur.fetchall()
        except:
            return None

    def set_file(self, name_file, path, id_users):
        try:
            self.cur.execute(
                "INSERT INTO public.files(name_file, path, id_users) VALUES (%s, %s, %s);",
                (name_file, path, id_users)
            )
            self.conn.commit()
        except:
            print("Ошибка")

    def get_id_file(self, id_user, path):
        # try:
        self.cur.execute(
            "SELECT id_file FROM public.files WHERE id_users = %s AND path = %s",
            (id_user, path)
        )
        return self.cur.fetchone()
        # except:
        #     print("Ошибка")


if __name__ == "__main__":
    db = DB("react_db")
    # db.set_file("111", "111.txt", 13)
    db.get_id_file(13, '2.txt')




