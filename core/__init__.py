from pkgutil import iter_modules

# EXTENSIONS
CORE_EXTENSIONS = tuple(module.name for module in iter_modules(__path__, f'{__package__}.'))
