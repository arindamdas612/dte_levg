import re

from random import choice, shuffle
from string import ascii_uppercase, ascii_lowercase, digits


from django.shortcuts import render, redirect

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.admin.views.decorators import staff_member_required


from django.contrib.auth.models import User

# Create your views here.


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_superuser)
def members(request):
    has_error = False
    if request.method == 'POST':
        regex_email = '^\w+([\.-]?\w+)*@\w+([\.-]?\w+)*(\.\w{2,3})+$'
        username = request.POST.get('username')
        firstname = request.POST.get('firstname')
        lastname = request.POST.get('lastname')
        email = request.POST.get('email')
        staff = request.POST.get('staff')
        staff = True if staff == 'on' else False
        superuser = request.POST.get('superuser')
        superuser = True if superuser == 'on' else False
        email_domain = email.split("@")[1]

        if email_domain.lower() != 'deloitte.com':
            messages.error(
                request, f"Deloitte email required")
            has_error = True
        else:
            user = User.objects.filter(email=email).first()
            if user:
                messages.error(
                    request, f"The Email already taken.")
                has_error = True
            else:
                user = User.objects.filter(username=username).first()
                if user:
                    messages.error(
                        request, f"The Username already taken.")
                    has_error = True
        if not has_error:
            pwd = [choice(ascii_lowercase), choice(ascii_uppercase), choice(digits)] \
                + [choice(ascii_lowercase + ascii_uppercase + digits)
                   for _ in range(5)]
            shuffle(pwd)
            pwd = ''.join(pwd)
            user = User.objects.create_user(
                username=username,
                password=pwd,
                email=email,
                first_name=firstname,
                last_name=lastname,
                is_active=False,
                is_superuser=superuser,
                is_staff=staff,
            )
            messages.success(
                request, f"Member created succesfully. System genrated password is {pwd}. Please make note of the password and share it with the Member.")

    users = User.objects.exclude(id=request.user.id).order_by('id')
    context = {
        'page_title': 'Members',
        'members': users,
    }
    return render(request, 'members.html', context=context)


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_superuser)
def switch_role(request, id, role):
    user = User.objects.get(pk=id)
    if role == 1:
        user.is_superuser = True
        user.is_staff = True
    elif role == 2:
        user.is_superuser = False
        user.is_staff = True
    else:
        user.is_superuser = False
        user.is_staff = False
    user.save()
    messages.success(
        request, f"{user.username}'s role switched successfully")
    return redirect('members')


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_superuser)
def activate_user(request, user_id):
    user = User.objects.get(pk=user_id)
    user.is_active = not user.is_active
    action = 'Activated' if user.is_active else 'Deactivated'
    user.save()
    messages.success(
        request, f"{user.username} {action}")
    return redirect('members')


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_superuser)
def del_user(request, user_id):
    user = User.objects.get(pk=user_id)
    username = user.username
    user.delete()
    messages.success(request, f"{username} deleted.")
    return redirect('members')


@login_required(login_url='/login/')
@user_passes_test(lambda u: u.is_superuser)
def reset_password(request, user_id):
    user = User.objects.get(pk=user_id)
    pwd = [choice(ascii_lowercase), choice(ascii_uppercase), choice(digits)] \
        + [choice(ascii_lowercase + ascii_uppercase + digits)
           for _ in range(5)]
    shuffle(pwd)
    pwd = ''.join(pwd)
    user.set_password(pwd)
    user.save()
    messages.success(
        request, f"{user.username}'s password is reset. New Password is {pwd}.")
    return redirect('members')
