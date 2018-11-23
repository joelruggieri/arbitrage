from rofex.client.RofexClient import RofexClient
from rofex.facade.RofexFacade import RofexFacade
from model.Portfolio import Portfolio
import configparser
import dependency_injector.containers as containers
import dependency_injector.providers as providers

class Module(containers.DeclarativeContainer):
    """IoC container of engine providers."""

    config = configparser.ConfigParser()
    config.read('config.ini')
    configuration = providers.Object(config)
    rofex_client = providers.Singleton(RofexClient, config=config)
    rofex_facade = providers.Singleton(RofexFacade, config=config, client=rofex_client())
    portfolio = providers.Singleton(Portfolio, account_id=config["PORTFOLIO"]["AccountId"], initial_amount=float(config["PORTFOLIO"]["InitialAmount"]))
