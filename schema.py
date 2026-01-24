import strawberry
from employees.queries import Query as EmployeeQuery
from employees.mutations import Mutation as EmployeeMutation
from baskets.queries import BasketQueries
from baskets.mutations import BasketMutations
from plugins.purchase_recommender.queries import RecommendationQueries
from customers.queries import CustomerQueries
from customers.mutations import CustomerMutations


@strawberry.type
class Query(EmployeeQuery, BasketQueries, RecommendationQueries, CustomerQueries):
    pass


@strawberry.type
class Mutation(EmployeeMutation, BasketMutations, CustomerMutations):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation)
