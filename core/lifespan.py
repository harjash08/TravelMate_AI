from contextlib import asynccontextmanager
from fastapi import FastAPI
from langgraph.store.postgres import PostgresStore
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool

from core.settings import settings
from agents.agent_factory import (
    create_hotel_agent,
    create_transport_agent,
    create_sightseeing_agent
)
from graph.workflow import create_travel_graph


@asynccontextmanager
async def lifespan(app: FastAPI):

    print("Initializing TravelMate agents...")

    hotel_agent= await create_hotel_agent()
    transport_agent = await create_transport_agent()
    sightseeing_agent = await create_sightseeing_agent()

    travel_agents = {
        "hotel": hotel_agent["hotel_search"],
        "hotel_booking":hotel_agent["hotel_booking"],
        "transport": transport_agent,
        "sightseeing": sightseeing_agent,
    }

    try:
        with PostgresStore.from_conn_string(
            settings.LANGGRAPH_DATABASE_URL
        ) as store:

            store.setup()

            async with AsyncConnectionPool(
                conninfo=settings.LANGGRAPH_DATABASE_URL,
                min_size=1,
                max_size=10,
                kwargs={
                    "autocommit": True,
                    "prepare_threshold": 0,
                },
                open=False,
            ) as pool:

                app.state.store = store
                app.state.checkpointer_pool = pool

                checkpointer = AsyncPostgresSaver(pool)

                await checkpointer.setup()

                app.state.checkpointer = checkpointer

                app.state.travel_graph = create_travel_graph(
                    travel_agents,
                    store,
                    checkpointer,
                )

                print("TravelMate graph initialized successfully.")

                yield

    finally:
        print("TravelMate application shutting down.")

        for attribute in (
            "travel_graph",
            "store",
            "checkpointer",
            "checkpointer_pool",
        ):
            if hasattr(app.state, attribute):
                delattr(app.state, attribute)