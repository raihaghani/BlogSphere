from .services import can_author
def navigation(request):
    return {'is_author': can_author(request.user)}
