def drop_while(F, COLL):

    if __name__ == 'Clojure_fn':

        TF_TUPLE = tuple(map(F, COLL))

        return COLL[:TF_TUPLE.index(False)] if False in TF_TUPLE else COLL


def partition_by(F, COLL):

    if __name__ == 'Clojure_fn':

        if not COLL: return ()

        FST = COLL[0]

        RUN = (FST,) + tuple(drop_while(lambda x: F(FST) == F(x), COLL[1:]))

        return (RUN,) + partition_by(F, COLL[len(RUN):])
