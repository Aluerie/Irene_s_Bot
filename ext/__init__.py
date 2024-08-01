from pkgutil import iter_modules

# EXTENSIONS
EXTENSIONS = tuple(module.name for module in iter_modules(__path__, f'{__package__}.'))
