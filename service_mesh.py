from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Optional, Protocol, Type, TypeVar


ServiceType = TypeVar("ServiceType")


class ServiceTransport(Protocol):
    def get_service(self, service_cls: Type[ServiceType], mesh: "ServiceMesh") -> ServiceType:
        ...


class LocalServiceTransport:
    def get_service(self, service_cls: Type[ServiceType], mesh: "ServiceMesh") -> ServiceType:
        return service_cls(mesh=mesh, db=mesh.db, user=mesh.user)


class CompositeServiceTransport:
    def __init__(self, transports: List[ServiceTransport]):
        self._transports = transports

    def get_service(self, service_cls: Type[ServiceType], mesh: "ServiceMesh") -> ServiceType:
        last_error: Optional[Exception] = None
        for transport in self._transports:
            try:
                return transport.get_service(service_cls, mesh)
            except Exception as exc:
                last_error = exc
        if last_error is not None:
            raise last_error
        raise RuntimeError("No service transports configured")


class CachedServiceTransport:
    def __init__(self, inner: ServiceTransport):
        self._inner = inner

    def get_service(self, service_cls: Type[ServiceType], mesh: "ServiceMesh") -> ServiceType:
        if service_cls in mesh._cache:
            return mesh._cache[service_cls]
        service = self._inner.get_service(service_cls, mesh)
        mesh._cache[service_cls] = service
        return service


@dataclass
class ServiceTool:
    name: str
    description: str
    callable: Callable[..., Any]


_SERVICE_REGISTRY: List[Type[Any]] = []


def service_class(name: Optional[str] = None) -> Callable[[Type[ServiceType]], Type[ServiceType]]:
    def decorator(cls: Type[ServiceType]) -> Type[ServiceType]:
        cls.service_name = name or cls.__name__
        _SERVICE_REGISTRY.append(cls)
        return cls

    return decorator


def service_tool(name: Optional[str] = None, description: Optional[str] = None) -> Callable[[Callable[..., Any]], Callable[..., Any]]:
    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        func._is_service_tool = True
        func._tool_name = name or func.__name__
        func._tool_description = description or (func.__doc__ or "").strip()
        return func

    return decorator


class ServiceMesh:
    def __init__(self, user: Any, db: Any, transport: Optional[ServiceTransport] = None) -> None:
        self.user = user
        self.db = db
        self._cache: Dict[Type[Any], Any] = {}
        base_transport: ServiceTransport = transport or CompositeServiceTransport([LocalServiceTransport()])
        self._transport = CachedServiceTransport(base_transport)

    def get_service(self, service_cls: Type[ServiceType]) -> ServiceType:
        return self._transport.get_service(service_cls, self)

    def get_tools(self) -> List[ServiceTool]:
        tools: List[ServiceTool] = []
        for service_cls in _SERVICE_REGISTRY:
            service = self.get_service(service_cls)
            for attr_name in dir(service):
                attr = getattr(service, attr_name)
                if callable(attr) and getattr(attr, "_is_service_tool", False):
                    tool_name = f"{service_cls.service_name}.{attr._tool_name}"
                    tools.append(
                        ServiceTool(
                            name=tool_name,
                            description=attr._tool_description,
                            callable=attr,
                        )
                    )
        return tools