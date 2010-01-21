"""
A suite of tools that make creating and handling plugins
in TiddlyWeb a bit more sensible.

Essentially this is a way to raise duplication to a common
core without encumbering the TiddlyWeb core.
"""

from tiddlyweb.model.bag import Bag
from tiddlyweb.model.policy import UserRequiredError
from tiddlyweb.store import NoBagError


def entitle(title):
    """
    Decorator that sets tiddlyweb.title in environ.
    """
    def entangle(f):
        def entitle(environ, start_response, *args, **kwds):
            output = f(environ, start_response)
            environ['tiddlyweb.title'] = title
            return output
        return entitle
    return entangle


def do_html():
    """
    Decorator that makes sure we are sending text/html.
    """
    def entangle(f):
        def do_html(environ, start_response, *args, **kwds):
            output = f(environ, start_response)
            start_response('200 OK', [
                ('Content-Type', 'text/html; charset=UTF-8')
                ])
            return output
        return do_html
    return entangle


def require_role(role):
    """
    Decorator that requires the current user has role <role>.
    """
    role = unicode(role)
    def entangle(f):
        def require_role(environ, start_response, *args, **kwds):
            try:
                if role in environ['tiddlyweb.usersign']['roles']:
                    return f(environ, start_response)
                else:
                    raise(UserRequiredError, 'insufficient permissions')
            except KeyError:
                raise(UserRequiredError, 'insufficient permissions')
        return require_role
    return entangle


def require_any_user():
    """
    Decorator that requires the current user be someone other than 'GUEST'.
    """
    def entangle(f):
        def require_any_user(environ, start_response, *args, **kwds):
            try:
                if environ['tiddlyweb.usersign']['name'] == 'GUEST':
                    raise(UserRequiredError, 'user must be logged in')
                else:
                    return f(environ, start_response)
            except KeyError:
                raise(UserRequiredError, 'user must be logged in')
        return require_any_user
    return entangle


def ensure_bag(bag_name, store, policy_dict={}, description='', owner=None):
    """
    Ensure that bag with name bag_name exists in store.
    If not, create it with owner, policy and description optionally
    provided. In either case return the bag object.
    """
    bag = Bag(bag_name)
    try:
        # when skinny is set we don't read the tiddlers
        bag.skinny = True
        bag = store.get(bag)
    except NoBagError:
        bag.desc = description
        if owner:
            bag.policy.owner = owner
            bag.policy.manage = [owner]
        for key in policy_dict:
            bag.policy.__setattr__(key, policy_dict[key])
        store.put(bag)
    return bag


def replace_handler(selector, path, new_handler):
    """
    Replace an existing path handler in the selector
    map with a new handler. Usually we want to add a
    new one, but sometimes we just want to replace.
    This makes replacing easy. Courtesy of arno,
    the selector author.
    """
    for index, (regex, handler) in enumerate(selector.mappings):
        if regex.match(path) is not None:
            selector.mappings[index] = (regex, new_handler)


def map_to_tiddler(selector, path, bag=None, recipe=None):
    """
    WARNING: NOT YET WELL TESTED!

    Map the route given in path to the default routing for
    getting, putting and deleting a tiddler. The provided bag
    or recipe name is used to disambiguate the mapping.

    The path must include {tiddler_name} in it somewhere. Examples:

       /{tiddler_name}
       /people/{tiddler_name}
       /a/long/path/to/something/{tiddler_name}
       /{tiddler_name}/something/here
    """
    from tiddlyweb.web.handler.tiddler import get, put, delete

    def handler(environ, start_response):
        if bag:
            environ['wsgiorg.routing_args'][1]['bag_name'] = bag
        elif recipe:
            environ['wsgiorg.routing_args'][1]['recipe_name'] = recipe
        else:
            return selector.not_found(environ, start_response)
        if environ['REQUEST_METHOD'] == 'GET':
            return get(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'PUT':
            return put(environ, start_response)
        elif environ['REQUEST_METHOD'] == 'DELETE':
            return delete(environ, start_response)
        else:
            return selector.method_not_allowed(environ, start_response)
    selector.add(path, GET=handler, PUT=handler, DELETE=handler)


def remove_handler(selector, path):
    """
    Remove an existing path handler in the selector
    map. This disables that route, and will cause a
    404 to be returned for that path.
    """
    for index, (regex, handler) in enumerate(selector.mappings):
        if regex.match(path) is not None:
            del selector.mappings[index]


def get_store(config):
    """
    Given the config, return a reference to the store.
    """
    from tiddlyweb.store import Store
    return Store(config['server_store'][0],
            config['server_store'][1],
            {'tiddlyweb.config': config})
