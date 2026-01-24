import strawberry
from employees.queries import Query
from employees.mutations import Mutation


schema = strawberry.Schema(query=Query, mutation=Mutation)
