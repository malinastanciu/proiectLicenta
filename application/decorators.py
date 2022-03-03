from django.shortcuts import redirect


def allowed_users(allowed_roles=[]):
    """
        Function that redirects to the group specific page
        :param allowed_roles: groups checked in the user's group list
        :param view_func: the View Function to be decorated
        :return a HttpResponse based on the belonging to allowed_roles group
    """

    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            user_groups = list()
            for group in request.user.groups.all():
                user_groups.append(group.name)
            if allowed_roles[0] in user_groups:

                return view_func(request, *args, **kwargs)
            else:
                return redirect('dashboard')

        return wrapper_func

    return decorator