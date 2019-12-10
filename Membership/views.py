from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import render, redirect
from django.views.generic import ListView
from django.urls import reverse

from .models import Membership, UserMembership, Subscription

import stripe

def get_user_membership(request):
    user_membership_qs = UserMembership.objects.filter(user=request.user)
    if user_membership_qs.exists():
        return user_membership_qs.first()
    return None    


def get_user_subscription(request):
    user_subscription_qs = Subscription.objects.filter(user_membership=get_user_membership(request))
    if user_subscription_qs.exists():
        user_subscription = user_subscription_qs.first()
        return user_subscription
    return None


def get_selected_membership(request):
    # This is how we get something from reqeust.session
    membership_type = request.session['selected_membership_type'] 
    selected_membership_qs = Membership.objects.filter(membership_type=membership_type)
    if selected_membership_qs.exists():
        return selected_membership_qs.first()
    return None

@login_required
def ProfileView (request):
    user_membership = get_user_membership(request)
    user_subscription = get_user_subscription(request)
    context = {
        'user_membership': user_membership,
        'user_subscription': user_subscription
    }
    return render(request, "membership/profile.html", context)


class MembershipSelectView(ListView):
    model = Membership

    # method is used to populate a dictionary with the new key called current membership 
    # to use as the template context

    def get_context_data(self, *args, **kwargs):
        context = super().get_context_data(**kwargs)
        print(context)
        current_membership = get_user_membership(self.request)
        # adding new key current_membership and assigning user current membership to it
        # which can be futher used by template
        context['current_membership'] = str(current_membership.membership) 
        print(context)
        return context



    # Select membership and move to payment page
    # if selected membership is already subscribe then don't 
    # if selected membership is not susbcribe then assign it to the session 
#-------------------------------------------------------------------------------------

      # To select the Membership and Move to next view
    def post(self, request, **kwargs):
        user_membership = get_user_membership(request)
        user_subscription = get_user_subscription(request)

        # select the membership type and get the next view 
        # 'membership_type' may be coming from template
        # Example :
        # request.POST.get('name',default=None).- Gets the value of the name parameter -
        # in a POST request or gets None if the parameter is not present. Note default can -
        # be overridden with a custom value. 
        selected_membership_type = request.POST.get('membership_type') # string type
        # string type is converted into object type  
        selected_membership = Membership.objects.get(membership_type=selected_membership_type)

        if user_membership.membership == selected_membership:
            if user_subscription is not None:
                messages.info(request, """You already have this membership. Your
                              next payment is due {}""".format('get this value from stripe'))
                return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

        # assign to the session
        request.session['selected_membership_type'] = selected_membership.membership_type

        return HttpResponseRedirect(reverse('memberships:payment'))


def test(request):
    return render(request, 'membership/test.html')


# one things to take care of :
# if user didn't select any memberrship 
# then request.session is None


@login_required
def PaymentView(request):
    # we user membership and user which selected the membership 
    # we have assign the selected membership to request.session 
    # so, we can used to get the selected  


    # user 
    user_membership = get_user_membership(request)

    try:
        # user with selected membership
        selected_membership = get_selected_membership(request)
    except:
        # if user didn't select any membership then redirect back select page
        return redirect(reverse("memberships:select"))



    # Now, Payment configurations :
    publishKey = settings.STRIPE_PUBLISHABLE_KEY

    if request.method == "POST":
        try:
            token = request.POST['stripeToken']

            # UPDATE FOR STRIPE API CHANGE 2018-05-21

            '''
            First we need to add the source for the customer
            '''

            customer = stripe.Customer.retrieve(user_membership.stripe_customer_id)
            customer.source = token # 4242424242424242
            customer.save()

            '''
            Now we can create the subscription using only the customer as we don't need to pass their
            credit card source anymore
            ''' 

            subscription = stripe.Subscription.create(
                customer=user_membership.stripe_customer_id,
                items=[
                    { "plan": selected_membership.stripe_plan_id },
                ]
            )

            return redirect(reverse('memberships:update-transactions',
                                    kwargs={
                                        'subscription_id': subscription.id
                                    }))

        except:
            messages.info(request, "An error has occurred, investigate it in the console")

    context = {
        'publishKey': publishKey,
        'selected_membership': selected_membership
    }

    return render(request, "membership/membership_payment.html", context)




@login_required
def updateTransactions(request, subscription_id):
    user_membership = get_user_membership(request)
    selected_membership = get_selected_membership(request)
    user_membership.membership = selected_membership
    user_membership.save()

    sub, created = Subscription.objects.get_or_create(
        user_membership=user_membership)
    sub.stripe_subscription_id = subscription_id
    sub.active = True
    sub.save()

    try:
        del request.session['selected_membership_type']
    except:
        pass
    print('Success')
    messages.info(request, 'Successfully created {} membership'.format(
        selected_membership))

    return redirect(reverse('memberships:select'))

# @login_required
# def cancelSubscription(request):
#     user_sub = get_user_subscription(request)

#     if user_sub.active is False:
#         messages.info(request, "You dont have an active membership")
#         return HttpResponseRedirect(request.META.get('HTTP_REFERER'))

#     sub = stripe.Subscription.retrieve(user_sub.stripe_subscription_id)
#     sub.delete()

#     user_sub.active = False
#     user_sub.save()

#     free_membership = Membership.objects.get(membership_type='Free')
#     user_membership = get_user_membership(request)
#     user_membership.membership = free_membership
#     user_membership.save()

#     messages.info(
#         request, "Successfully cancelled membership. We have sent an email")
#     # sending an email here

#     return redirect(reverse('memberships:select'))
