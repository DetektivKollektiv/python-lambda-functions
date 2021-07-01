from core_layer.model.claimant_model import Claimant


def get_claimant_by_name(claimant_name, session):
    """Returns a claimant with the specified name

        Returns
        ------
        claimant: Claimant
            An url referenced in an item
        Null, if no claimant was found
        """

    claimant = session.query(Claimant).filter(
        Claimant.claimant == claimant_name).first()
    if claimant is None:
        raise Exception("No claimant found.")
    return claimant
