from dwhpulse.pipeline import STEPS


def test_step_names_are_unique():
    names = [step.name for step in STEPS]
    assert len(names) == len(set(names))


def test_dependencies_come_before_their_step():
    seen = set()
    for step in STEPS:
        assert set(step.depends_on) <= seen, step.name
        seen.add(step.name)
