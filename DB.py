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

    def get_file(self, id):
        self.cur.execute(
            "SELECT id_file, name_file, path FROM public.files WHERE id_users = %s",
            (id,)
        )

        return self.cur.fetchall()

    def __del__(self):
        self.conn.close()
        self.cur.close()


if __name__ == "__main__":
    db = DB("react_db")
    print(db.get_file(13))
    # print(db.check_is_aut("email@email.com", "11111111"))
    # print(db.select_by("id", 1))
    # print(db.get_user_id("email@email.co"))
    # db.get_users()



