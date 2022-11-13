from honeybee_ph_rhino.gh_compo_io import ghio_validators

def test_validated():
    class Test:
        test_attr = ghio_validators.NotNone("test_attr")

    t = Test()
    t.test_attr = "a"
