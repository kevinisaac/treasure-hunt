from functools import wraps
from flask import redirect, url_for
from flask.ext.login import current_user

def logout_required(target):
    """Redirects to target if logged in"""
    def decorated_wrapper(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if current_user.is_authenticated:
                print 'Core - authenticated'
                return redirect(url_for(target))
            else:
                print 'Core - nah authenticated'
                return f(*args, **kwargs)
        return decorated_function
    return decorated_wrapper

def to_lower(*o_args):
    def decorated_wrapper(f):
        @wraps(f)
        def decorated_function(*f_args, **f_kwargs):
            for o_arg in o_args:
                if o_arg in f_kwargs:
                    f_kwargs[o_arg] = f_kwargs[o_arg].lower()
            return f(*f_args, **f_kwargs)
        return decorated_function
    return decorated_wrapper

