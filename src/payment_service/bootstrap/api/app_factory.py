from bootstrap.api.dependencies import get_api_key
from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI
from structlog import get_logger

from bootstrap.api.hanlers.exceptions.domain.payment import register_exception_handlers
from presentation.http.v1.payments.router import router


def create_app() -> FastAPI:
    app = FastAPI(
        title='Async payment processing service',
        description="""Test task for async processing service,
                        with gateway processing emulation
                        and message delivery guarantee""",
        version='0.0.1',
        lifespan=lifespan,
        dependencies=[Depends(get_api_key)],
    )

    register_exception_handlers(app)
    app.include_router(router)

    return app


@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- startup ---
    # init_logging()
    logger = get_logger()
    logger.info('app startup')
    # --- startup ---

    yield
