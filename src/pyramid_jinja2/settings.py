from jinja2 import (
    BytecodeCache,
    DebugUndefined,
    FileSystemBytecodeCache,
    StrictUndefined,
    Undefined,
)
from pyramid.path import AssetResolver
from pyramid.settings import asbool

from .i18n import GetTextWrapper

_JINJA2_ENVIRONMENT_DEFAULTS = {
    "autoescape": True,
}


def splitlines(s):
    return filter(None, [x.strip() for x in s.splitlines()])


def parse_named_assetspecs(input, maybe_dotted):
    """
    Parse a dictionary of asset specs.
    Parses config values from .ini file and returns a dictionary with
    imported objects
    """
    # input must be a string or dict
    result = {}
    if isinstance(input, str):
        for f in splitlines(input):
            name, impl = f.split("=", 1)
            result[name.strip()] = maybe_dotted(impl.strip())
    else:
        for name, impl in input.items():
            result[name] = maybe_dotted(impl)
    return result


def parse_multiline(extensions):
    if isinstance(extensions, str):
        extensions = list(splitlines(extensions))
    return extensions


def parse_undefined(undefined):
    if undefined == "strict":
        return StrictUndefined
    if undefined == "debug":
        return DebugUndefined
    return Undefined


def parse_loader_options_from_settings(settings, prefix, maybe_dotted, package):
    """Parse options for use with the SmartAssetSpecLoader."""
    package = package or "__main__"

    def sget(name, default=None):
        return settings.get(prefix + name, default)

    debug = sget("debug_templates", None)
    if debug is None:
        # bw-compat prior to checking debug_templates for specific prefix
        debug = settings.get("debug_templates", None)
    debug = asbool(debug)

    input_encoding = sget("input_encoding", "utf-8")

    # get jinja2 directories
    resolve = AssetResolver(package).resolve
    directories = parse_multiline(sget("directories") or "")
    directories = [resolve(d).abspath() for d in directories]

    return dict(
        debug=debug,
        encoding=input_encoding,
        searchpath=directories,
    )


def parse_env_options_from_settings(
    settings,
    prefix,
    maybe_dotted,
    package,
    defaults=None,
):
    """Parse options for use with the Jinja2 Environment."""

    def sget(name, default=None):
        return settings.get(prefix + name, default)

    if defaults is None:
        defaults = _JINJA2_ENVIRONMENT_DEFAULTS

    opts = {}

    reload_templates = sget("reload_templates")
    if reload_templates is None:
        reload_templates = settings.get("pyramid.reload_templates")
    opts["auto_reload"] = asbool(reload_templates)

    # set string settings
    for key_name in (
        "block_start_string",
        "block_end_string",
        "variable_start_string",
        "variable_end_string",
        "comment_start_string",
        "comment_end_string",
        "line_statement_prefix",
        "line_comment_prefix",
        "newline_sequence",
    ):
        value = sget(key_name, defaults.get(key_name))
        if value is not None:
            opts[key_name] = value

    # boolean settings
    for key_name in ("autoescape", "trim_blocks", "optimized", "lstrip_blocks"):
        value = sget(key_name, defaults.get(key_name))
        if value is not None:
            opts[key_name] = asbool(value)

    # integer settings
    for key_name in ("cache_size",):
        value = sget(key_name, defaults.get(key_name))
        if value is not None:
            opts[key_name] = int(value)

    opts["undefined"] = parse_undefined(sget("undefined", ""))

    # get supplementary jinja2 settings
    domain = sget("i18n.domain", package and package.__name__ or "messages")
    gettext_wrapper = maybe_dotted(sget("i18n.gettext", GetTextWrapper))
    opts["gettext"] = gettext_wrapper(domain=domain)

    # get jinja2 extensions
    extensions = parse_multiline(sget("extensions", ""))
    i18n_extension = sget("i18n_extension", "jinja2.ext.i18n")
    if i18n_extension not in extensions:
        extensions.append(i18n_extension)
    opts["extensions"] = extensions

    # get jinja2 bytecode caching settings and set up bytecaching
    bytecode_caching = sget("bytecode_caching", False)
    if isinstance(bytecode_caching, BytecodeCache):
        opts["bytecode_cache"] = bytecode_caching
    elif asbool(bytecode_caching):
        bytecode_caching_directory = sget("bytecode_caching_directory", None)
        opts["bytecode_cache"] = FileSystemBytecodeCache(bytecode_caching_directory)

    # should newstyle gettext calls be enabled?
    opts["newstyle"] = asbool(sget("newstyle", False))

    # Do we have a finalize function?
    finalize = sget("finalize")
    if finalize is not None:
        opts["finalize"] = maybe_dotted(finalize)

    # add custom jinja2 filters
    opts["filters"] = parse_named_assetspecs(sget("filters", ""), maybe_dotted)

    # add custom jinja2 tests
    opts["tests"] = parse_named_assetspecs(sget("tests", ""), maybe_dotted)

    # add custom jinja2 functions
    opts["globals"] = parse_named_assetspecs(sget("globals", ""), maybe_dotted)

    return opts
