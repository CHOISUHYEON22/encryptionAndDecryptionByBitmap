def drop_while(fn, coll):

    if __name__ == 'Clojure_fn':

        TF_TUPLE = tuple(map(fn, coll))

        return coll[:TF_TUPLE.index(False)] if False in TF_TUPLE else coll


def partition_by(fn, coll):

    if __name__ == 'Clojure_fn':

        if not coll: return ()

        FST = coll[0]

        RUN = (FST,) + tuple(drop_while(lambda x: fn(FST) == fn(x), coll[1:]))

        return (RUN,) + partition_by(fn, coll[len(RUN):])


def partition_num(num: int, contain_all: bool, coll):

    if not coll: return ()

    if len(coll) < num: return (coll, ) if contain_all else ()

    return (coll[:num], ) + partition_num(num, contain_all, coll[num:])
