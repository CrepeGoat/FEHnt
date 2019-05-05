import pandas as pd
import static_frame as sf


class HashableSeries(sf.Series):
    def __hash__(self):
        items = self.iter_element_items()
        if isinstance(self.index, sf.IndexHierarchy):
            items = ((tuple(k), v) for k, v in items)

        return hash(tuple(items))


    def __eq__(self, other):
        return (
            len(self) == len(other)
            and (self.values == other.values).all()
            and (self.index.values == other.index.values).all()
        )

def pd_ify(ntuple):
    return ntuple._replace(**{k: v.to_pandas()
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, sf.Series)})


def sf_ify(ntuple):
    return ntuple._replace(**{k: HashableSeries.from_pandas(v, own_data=True)
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, pd.Series)})
