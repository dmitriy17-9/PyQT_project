import sqlite3
from PyQt5 import QtGui


def db_connect():
    con = sqlite3.connect('data/money_db.sqlite')
    cur = con.cursor()
    return con, cur


def category():
    con, cur = db_connect()
    category = cur.execute('SELECT product_name FROM categories')
    categories = [i[0] for i in category]
    return categories


def db_show_table_expenses():
    expen = []
    con_ex, cur_ex = db_connect()
    query = """SELECT id, product, expenditure FROM expenses"""
    res = cur_ex.execute(query).fetchall()
    for n, product, expenditure in res:
        expen.append({"id": n,
                      "product": product,
                      "expenditure": expenditure})
    return expen


def expenses():
    ex = []
    con_expenses, cur_expenses = db_connect()
    query = """SELECT id, product, expenditure FROM expenses"""
    res = cur_expenses.execute(query).fetchall()
    for n, product, expenditure in res:
        ex.append(int(expenditure))
    return ex


def db_delete_row(ids: list):
    ids = ", ".join(ids)
    con, cur = db_connect()
    cur.execute(f"""DELETE FROM expenses WHERE id IN ({ids})""")
    con.commit()


def db_update_row(modified):
    con, cur = db_connect()
    query = "UPDATE expenses SET\n"
    query += ", ".join([f"{key}='{modified.get(key)}'"
                        for key in modified.keys() if key != "id"])
    query += " WHERE id = " + modified["id"]
    cur.execute(query)
    con.commit()


# def db_add_row(name: str, url: str, bitrate: int, binary_image: bytes = None) -> None:
#     """
#     Добавляет в базу строку плейлиста
#     Такой длинный алгоритм проверки нужен, для совместимости,
#     так как UPSERT поддерживается не всеми версиями либы sqlite
#     UPSERT syntax was added to SQLite with version 3.24.0 (2018-06-04)
#     :param name: Имя радио
#     :type name: str
#     :param url: URL радио
#     :type url: str
#     :param bitrate: bitrate
#     :type bitrate: int
#     :param binary_image: byte obj img
#     :type binary_image: bytes
#     :return: None
#     """
#     try:
#         con, cur = db_connect()
#         query = f"""SELECT id FROM playlist WHERE name = '{name}';"""
#         update_id = cur.execute(query).fetchone()
#
#         if update_id:
#             query = f"""UPDATE playlist SET name='{name}', bitrate={bitrate}, url='{url}'
#                 WHERE name = '{name}';"""
#             cur.execute(query)
#             id_ = update_id[0]
#         else:
#             query = f"""INSERT INTO playlist (name, bitrate, status, url)
#                 VALUES ('{name}', {bitrate}, 1, '{url}');"""
#             res = cur.execute(query)
#             # получаем id последней вставки если id = 0 то вставки не было, был update
#             id_ = cur.execute("""SELECT last_insert_rowid();""").fetchone()[0]
#
#         if binary_image:
#             # если изображение было выбрано то добавляем его в таблицу
#             query = "INSERT INTO image (id, image) VALUES (?, ?);"
#             cur.execute(query, (id_, binary_image))
#         elif not update_id:
#             # если это был INSERT просто добавляем изображение по умолчанию
#             query = "INSERT INTO image (id) VALUES (?);"
#             cur.execute(query, (id_,))
#         con.commit()
#
#     except Exception as e:
#         logging.error(f"Произошла ошибка при добавлении строки\n"
#                       f"name={name} url={url} bitrate={bitrate} binary_image={binary_image}\n"
#                       f"{e}")
#
#


#
#
# def db_show_table() -> List[Dict[str, Any]]:
#     """
#     Читает плейлист из базы и возвращает список словарей
#     :return: плейлист
#     :rtype: List[Dict[str, Any]]
#     """
#     try:
#         playlist = []
#         con, cur = db_connect()
#         query = """SELECT playlist.id, playlist.name, playlist.url, playlist.status, playlist.bitrate, image.image
#             FROM playlist, image WHERE playlist.id = image.id ORDER BY playlist.name ASC"""
#         res = cur.execute(query).fetchall()
#         for n, name, url, status, bitrate, image in res:
#             q_img = QtGui.QImage.fromData(image)
#             pixmap = QtGui.QPixmap.fromImage(q_img)
#             playlist.append({"id": n,
#                              "name": name,
#                              "url": url,
#                              "bitrate": bitrate,
#                              "status": status,
#                              "image": pixmap})
#         return playlist
#     except:
#         raise Exception("Неизвестная ошибка чтения плейлиста, удалите файл базы resource/playlist.sqlite и "
#                         "он будет создан автоматически при следующем запуске")
#
#
# def db_update_row(modified: dict) -> None:
#     """
#     Обновляет строку при прямом редактировани таблицы
#     :param modified:
#     :type modified:
#     :return:
#     """
#     con, cur = db_connect()
#     query = "UPDATE playlist SET\n"
#     query += ", ".join([f"{key}='{modified.get(key)}'"
#                         for key in modified.keys() if key != "id"])
#     query += " WHERE id = " + modified["id"]
#     logging.info(f"save_results query\n{query}")
#     cur.execute(query)
#     con.commit()
#
#
# def check_db() -> None:
#     """
#     Проверяет что База работает. Если не работает или битая, удаляет файл и создает снова чистую базу
#     Пример пустой базы в виде SQL команд в file_db_blank
#     :return: None
#     """
#     query = """SELECT * FROM playlist, image WHERE playlist.id = image.id"""
#     try:
#         con, cur = db_connect()
#         cur.execute(query).fetchall()
#     except:
#         if os.path.exists(file_db_path):
#             logging.info("file DB exists, remove file")
#             os.remove(file_db_path)
#         con, cur = db_connect()
#
#         with open(file_db_blank) as file:
#             logging.info(f"read blank file DB {file_db_blank}")
#             res = " ".join(file.readlines()).split(";")
#             logging.info(res)
#         _ = [cur.execute(query.strip()) for query in res if res]
#         con.commit()
#         logging.warning(f"Creating new DB")
#
#
# def main():
#     """
#     Используется только для теста функций
#     :return:
#     """
#     # print(db_connect())
#     # db_add_row('Наше Радио132131', 'http://nashe1.hostingradio.ru/nashe-256', 256)
#     check_db()
#
#
# if __name__ == '__main__':
#     main()
