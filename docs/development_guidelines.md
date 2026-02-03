# Development guidelines

## Layering of the application components

The application follows an endpoints/services/repositories layering of components.
Objects are instantiated by factory functions which provide the neccessary dependencies
to the initialization methods. In general, each layer should use the lower-level layer
without being required to go any lower in all aspects of the code. For example, endpoints
should not be required to wire the repository dependencies of the services. Services should
instantiate the repository layer objects on their own. This is especially important since
all the repositories are per-transaction objects because they own an SQLAlchemy Session object
and repositories may need to be instantiated multiple times during the lifetime of a single
service-layer object.
