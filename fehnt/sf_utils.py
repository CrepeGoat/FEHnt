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

    def match_index_to(self, target, fill_value=None):
        # Designed to replace calls like `s1.add(s2, fill_value=0)`
        if isinstance(target, sf.Series):
            target_index = target.index
        else:
            target_index = target

        return self.__class__((
            self[i] if i in self else fill_value
            for i in target_index
        ), index=target_index)

    def broadcast_index_to(self, target, level_in_target):
        # Designed to replace calls like `s1.add(s2, level=0)`
        if isinstance(target, sf.Series):
            target_index = target.index
        else:
            target_index = target

        return self.__class__((
            self[i[level_in_target]] for i in target_index
        ), index=target_index)



def pd_ify(ntuple):
    return ntuple._replace(**{k: v.to_pandas()
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, sf.Series)})


def sf_ify(ntuple):
    return ntuple._replace(**{k: HashableSeries.from_pandas(v, own_data=True)
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, pd.Series)})
