from . import models
from . import wizards


def post_init_hook(env):
    """I partner che esistono gia' prendono il nome come cognome."""
    env.cr.execute(
        "UPDATE res_partner SET cognome = name WHERE cognome IS NULL AND name IS NOT NULL")
