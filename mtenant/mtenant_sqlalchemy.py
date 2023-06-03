from __future__ import annotations

from flask import g
from flask_sqlalchemy import SQLAlchemy
import typing as t
import sqlalchemy as sa
from flask_sqlalchemy.session import Session


class MTUtil:

    @staticmethod
    def get_tenant_key():
        if "tenant" in g and "tkey" in g.tenant:
            return g.tenant["tkey"]
        return None


class MTenantSession(Session):
    def get_bind(
            self,
            mapper: t.Any | None = None,
            clause: t.Any | None = None,
            bind: sa.engine.Engine | sa.engine.Connection | None = None,
            **kwargs: t.Any,
    ) -> sa.engine.Engine | sa.engine.Connection:
        if bind is not None:
            return bind

        engines = self._db.engines

        if mapper is not None:
            try:
                mapper = sa.inspect(mapper)
            except sa.exc.NoInspectionAvailable as e:
                if isinstance(mapper, type):
                    raise sa.orm.exc.UnmappedClassError(mapper) from e
                raise

        bind_key = MTUtil.get_tenant_key()
        if bind_key in engines:
            return engines[bind_key]

        return super().get_bind(mapper=mapper, clause=clause, bind=bind, kwargs=kwargs)


class MTenantSQLAlchemy(SQLAlchemy):

    def _make_session_factory(
            self, options: dict[str, t.Any]
    ) -> sa.orm.sessionmaker[Session]:
        options.setdefault("class_", MTenantSession)
        options.setdefault("query_cls", self.Query)
        return sa.orm.sessionmaker(db=self, **options)

    def get_tenant_list(self):
        tenants = self.engines
        tenant_list = []
        if tenants:
            for key, details in tenants.items():
                if key:
                    tenant_list.append(key)
        return tenant_list

    def register_tenant(self, app, key: str, db_url: str):
        if not key or not db_url or key in self.engines:
            return False

        echo: bool = app.config.setdefault("SQLALCHEMY_ECHO", False)

        options: dict = {"url": db_url}
        options.setdefault("echo", echo)
        options.setdefault("echo_pool", echo)

        self._make_metadata(key)
        self._apply_driver_defaults(options, app)
        engine = self._make_engine(key, options, app)
        if self._app_engines and app in self._app_engines and key not in self._app_engines[app]:
            self._app_engines[app][key] = engine
            return True
        return False
