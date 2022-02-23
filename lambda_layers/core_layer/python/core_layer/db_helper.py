from sqlalchemy import func


def substring(column, delimeter, session):
    if session.bind.dialect.name == 'sqlite':
        return func.iif(func.instr(column, delimeter) > 0, func.substr(
            column, 1, func.instr(column, delimeter)-1), column)
    elif session.bind.dialect.name == 'mysql':
        return func.substring_index(column, delimeter, 1)
