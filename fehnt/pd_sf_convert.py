import pandas as pd
import static_frame as sf


class Series(sf.Series):
    def __hash__(self):
        return hash(
            (tuple(self.index), tuple(self.values))
        )


def pd_ify(ntuple):
    return ntuple._replace(**{k: v.to_pandas()
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, sf.Series)})


def sf_ify(ntuple):
    return ntuple._replace(**{k: Series.from_pandas(v, own_data=True)
                              for k, v in ntuple._asdict().items()
                              if isinstance(v, pd.Series)})
