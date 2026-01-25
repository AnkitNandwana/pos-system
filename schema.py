import strawberry
from employees.queries import Query as EmployeeQuery
from employees.mutations import Mutation as EmployeeMutation
from baskets.queries import BasketQueries
from baskets.mutations import BasketMutations
from baskets.subscriptions import Subscription as BasketSubscription
from products.queries import ProductQueries
from plugins.purchase_recommender.queries import RecommendationQueries
from plugins.purchase_recommender.mutations import RecommendationMutations
from plugins.purchase_recommender.subscriptions import RecommendationSubscriptions
from plugins.queries import PluginQueries
from plugins.mutations import PluginMutations
from customers.queries import CustomerQueries
from customers.mutations import CustomerMutations


@strawberry.type
class Query(EmployeeQuery, BasketQueries, ProductQueries, RecommendationQueries, CustomerQueries, PluginQueries):
    pass


@strawberry.type
class Mutation(EmployeeMutation, BasketMutations, RecommendationMutations, CustomerMutations, PluginMutations):
    pass


@strawberry.type
class Subscription(BasketSubscription, RecommendationSubscriptions):
    pass


schema = strawberry.Schema(query=Query, mutation=Mutation, subscription=Subscription)
