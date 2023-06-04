from db.DataBaseBiblioteca import BooksDataBase
from Utils.str_functions import clean_str_sig, build_list


class FilterBook:
    def __init__(self, ):
        self.index = dict()
        db = BooksDataBase()
        self.build_index(db.getAllBookForSearching())

    def build_index(self, books):
        for r in books:
            id = r[0]
            descr = build_list(r[1])
            titulo = build_list(r[2])
            autor = build_list(r[3])
            editorial = build_list(r[4])
            isbn = build_list(r[5])

            claves = descr + autor + titulo + editorial + isbn

            for i in claves:
                if i in self.index.keys():
                    self.index[i].add(id)
                else:
                    self.index.setdefault(i, {id})

    def get_records_by_keys(self, keys):
        v = set()
        for i in keys:
            if i in self.index.keys():
                v = v | self.index[i]
        return v
