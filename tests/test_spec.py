# dependencies
from typespecs import ITSELF, Spec
from typespecs.spec import ItselfType, is_spec


def test_itself() -> None:
    assert ItselfType() == ITSELF
    assert ItselfType() is not ITSELF


def test_spec() -> None:
    spec = Spec(a=1, b=2, c=ITSELF)
    assert is_spec(spec)
    assert not is_spec({})
    assert spec.replace(1, 0) == Spec(a=0, b=2, c=ITSELF)
    assert spec.replace(ITSELF, 3) == Spec(a=1, b=2, c=3)
