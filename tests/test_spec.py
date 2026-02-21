# dependencies
import pandas as pd
from typespecs import ITSELF, Spec, SpecFrame
from typespecs.spec import ItselfType, is_spec, is_specframe


def test_itself() -> None:
    assert ItselfType() == ITSELF
    assert ItselfType() is not ITSELF


def test_spec() -> None:
    spec = Spec(a=1, b=2, c=ITSELF)
    assert is_spec(spec)
    assert not is_spec({})


def test_specframe() -> None:
    specs = SpecFrame()
    assert is_specframe(specs)
    assert not is_specframe(pd.DataFrame())
