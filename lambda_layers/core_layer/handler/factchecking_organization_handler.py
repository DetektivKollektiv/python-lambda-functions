from core_layer.connection_handler import get_db_session
from core_layer.model.factchecking_organization_model import FactChecking_Organization


def get_organization_by_name(content, is_test, session):
    """Returns the organization publishing fact checks

        Returns
        ------
        org: FactChecking_Organization
        Null, if no org was found
        """
    session = get_db_session(is_test, session)
    org = session.query(FactChecking_Organization).filter(
        FactChecking_Organization.name == content).first()
    if org is None:
        raise Exception("No Organization found.")
    return org
