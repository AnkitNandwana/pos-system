import strawberry
from employees.queries import Query as EmployeeQuery
from employees.mutations import Mutation as EmployeeMutation
from baskets.queries import BasketQueries
from baskets.mutations import BasketMutations
from plugins.purchase_recommender.queries import RecommendationQueries


@strawberry.type
class Query(EmployeeQuery, BasketQueries, RecommendationQueries):
    pass


@strawberry.type
class Mutation(EmployeeMutation, BasketMutations):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
