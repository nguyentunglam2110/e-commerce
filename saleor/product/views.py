from __future__ import unicode_literals

import datetime
import json

from django.core.urlresolvers import reverse
from django.http import HttpResponsePermanentRedirect, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.template.response import TemplateResponse

from ..cart.utils import set_cart_cookie
from ..core.utils import serialize_decimal
from .models import Category
from .utils import (products_with_details, products_for_cart,
                    handle_cart_form, get_availability,
                    get_product_images, get_variant_picker_data,
                    get_product_attributes_data, product_json_ld,
                    products_with_availability)
from ..bid.models import BidSession
from django.utils import timezone


def product_details(request, slug, product_id, form=None):
    """Product details page

    The following variables are available to the template:

    product:
        The Product instance itself.

    is_visible:
        Whether the product is visible to regular users (for cases when an
        admin is previewing a product before publishing).

    form:
        The add-to-cart form.

    price_range:
        The PriceRange for the product including all discounts.

    undiscounted_price_range:
        The PriceRange excluding all discounts.

    discount:
        Either a Price instance equal to the discount value or None if no
        discount was available.

    local_price_range:
        The same PriceRange from price_range represented in user's local
        currency. The value will be None if exchange rate is not available or
        the local currency is the same as site's default currency.
    """
    products = products_with_details(user=request.user)
    product = get_object_or_404(products, id=product_id)

    products_realated_items = product.related_products.all()

    if products_realated_items:
        products_realated = products_with_availability(products_realated_items, discounts=[], local_currency=request.currency)
    else:
        products_realated = None

    if product.get_slug() != slug:
        return HttpResponsePermanentRedirect(product.get_absolute_url())
    today = datetime.date.today()
    is_visible = (
        product.available_on is None or product.available_on <= today)
    if form is None:
        form = handle_cart_form(request, product, create_cart=False)[0]
    availability = get_availability(product, discounts=request.discounts,
                                    local_currency=request.currency)
    template_name = 'product/details_%s.html' % (
        type(product).__name__.lower(),)
    templates = [template_name, 'product/details.html']
    product_images = get_product_images(product)
    variant_picker_data = get_variant_picker_data(
        product, request.discounts, request.currency)
    product_attributes = get_product_attributes_data(product)
    show_variant_picker = all([v.attributes for v in product.variants.all()])
    json_ld_data = product_json_ld(product, availability, product_attributes)

    # check if product is on bidding:
    now =timezone.now()
    bidding_session = BidSession.objects.filter(end_bid__gte=now,
                                start_bid__lte=now).first()
    if bidding_session:
        is_bidding = (product.id in bidding_session.products.values_list('pk', flat=True).all())
    else:
        is_bidding = False

    return TemplateResponse(
        request, templates,
        {'is_visible': is_visible,
        'is_bidding' : is_bidding,
        'bidding_session' : bidding_session,
         'form': form,
         'availability': availability,
         'product': product,
         'product_attributes': product_attributes,
         'product_images': product_images,
         'show_variant_picker': show_variant_picker,
         'products_realated': products_realated,
         'variant_picker_data': json.dumps(
             variant_picker_data, default=serialize_decimal),
         'json_ld_product_data': json.dumps(
             json_ld_data, default=serialize_decimal)})


def product_add_to_cart(request, slug, product_id):
    # types: (int, str, dict) -> None

    if not request.method == 'POST':
        return redirect(reverse(
            'product:details',
            kwargs={'product_id': product_id, 'slug': slug}))

    products = products_for_cart(user=request.user)
    product = get_object_or_404(products, pk=product_id)
    form, cart = handle_cart_form(request, product, create_cart=True)
    if form.is_valid():
        form.save()
        if request.is_ajax():
            response = JsonResponse({'next': reverse('cart:index')}, status=200)
        else:
            response = redirect('cart:index')
    else:
        if request.is_ajax():
            response = JsonResponse({'error': form.errors}, status=400)
        else:
            response = product_details(request, slug, product_id, form)
    if not request.user.is_authenticated:
        set_cart_cookie(cart, response)
    return response


def category_index(request, path, category_id):
    category = get_object_or_404(Category, id=category_id)
    actual_path = category.get_full_path()
    if actual_path != path:
        return redirect('product:category', permanent=True, path=actual_path,
                        category_id=category_id)
    return TemplateResponse(request, 'category/index.html',
                            {'category': category})
