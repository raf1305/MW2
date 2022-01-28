from django.shortcuts import redirect
from django.views import generic
from django.core.paginator import Paginator
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt

import ast
from http.client import HTTPResponse
from telnetlib import STATUS
from turtle import title
from urllib import response
from datetime import datetime,timezone

from product.models import Variant,Product,ProductVariant,ProductVariantPrice

@method_decorator(csrf_exempt, name='dispatch')
class CreateProductView(generic.TemplateView):
    template_name = 'products/create.html'

    def get_context_data(self, **kwargs):
        context = super(CreateProductView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        context['product'] = True
        context['variants'] = list(variants.all())
        return context
    def post(self,request):
        response_ = request.body
        r = ast.literal_eval(response_.decode('utf-8'))
        product_title = r.get('title')
        product_sku = r.get('sku')
        product_description = r.get('description')
        product_image = r.get('product_image')
        product_variant = r.get('product_variant')
        product_variant_prices = r.get('product_variant_prices')
        
        product_object = Product(title = product_title,sku=product_sku,description = product_description)
        product_object.save()
        product_variants = []
        product_variants_obj = {}
        for i in product_variant:
            variant_id = i['option']
            variant_tags = i['tags']
            for j in variant_tags:
                temp = ProductVariant(variant_title = j,variant_id = variant_id,product_id = product_object.id)
                temp.save()
                # product_variants.append(temp)
                product_variants_obj[j] = temp
        # ProductVariant.objects.bulk_create(product_variants,batch_size=50)
        product_variant_prices_obj = []
        for i in product_variant_prices:
            title = i['title'].split('/')[:-1]
            temp = ProductVariantPrice(price = i['price'],stock = i['stock'],product_id = product_object.id)
            try:
                temp.product_variant_one = product_variants_obj[title[0]]
            except:
                pass
            try:
                temp.product_variant_two = product_variants_obj[title[1]]
            except:
                pass
            try:
                temp.product_variant_three = product_variants_obj[title[2]]
            except:
                pass
            temp.save()

            # product_variant_prices_obj.append(temp)
        # ProductVariantPrice.objects.bulk_create(product_variant_prices_obj,batch_size=50)
        return redirect('product:list.product')


@method_decorator(csrf_exempt, name='dispatch')
class ProductListView(generic.TemplateView):
    template_name = 'products/list.html'
    paginate_by = 2

    def get_context_data(self, **kwargs):
        context = super(ProductListView, self).get_context_data(**kwargs)

        product_filter_title = self.request.GET.get('title')
        product_filter_variant = self.request.GET.get('variant')
        product_filter_price_from = self.request.GET.get('price_from')
        product_filter_price_to = self.request.GET.get('price_to')
        product_filter_date = self.request.GET.get('date')

        product_list = []
        all_products = Product.objects.all()

        if product_filter_title:
            all_products = all_products.filter(title__icontains = product_filter_title)
        if product_filter_price_from and product_filter_price_to:
            product_ids =list(set(ProductVariantPrice.objects.filter(price__range = [product_filter_price_from,product_filter_price_to]).only('product_id').values_list('product_id',flat=True)))
            all_products = all_products.filter(id__in = product_ids)
        if product_filter_variant:
            product_ids = ProductVariant.objects.filter(variant_title__iexact = product_filter_variant).only('product_id').values_list('product_id',flat=True).distinct()
            all_products = all_products.filter(id__in = product_ids)
        if product_filter_date:
            product_filter_start_date = datetime.strptime(product_filter_date,"%Y-%m-%d").date()
            product_filter_end_date = datetime.strptime(product_filter_date+" 23:59:59","%Y-%m-%d %H:%M:%S")
            all_products = all_products.filter(created_at__range = [product_filter_start_date,product_filter_end_date])
        paginator = Paginator(all_products, self.paginate_by)
        page = self.request.GET.get('page')
        pag_item = paginator.get_page(page)
        for i in pag_item:
            temp = {}
            temp['id'] = i.id
            creattion_difference = datetime.now(timezone.utc)-i.created_at
            temp['created_at'] = (str(creattion_difference.days) + ' days ago') if creattion_difference.days != 0  else str(int(float(str(creattion_difference.total_seconds()/(60*60))))) + ' hours ago'
            temp['title'] = i.title
            temp['description'] = i.description
            temp['variants'] = []
            product_variants = ProductVariantPrice.objects.select_related('product_variant_one','product_variant_two','product_variant_three').filter(product_id = i.id)
            for j in product_variants:
                variant_temp = {}
                variant_temp['variant'] = ''
                if j.product_variant_one:
                    variant_temp['variant'] += j.product_variant_one.variant_title + '/'
                else:
                    variant_temp['variant'] += '/'
                if j.product_variant_two:
                    variant_temp['variant'] += j.product_variant_two.variant_title + '/'
                else:
                    variant_temp['variant'] += '/'
                if j.product_variant_three:
                    variant_temp['variant'] += j.product_variant_three.variant_title
                variant_temp['price'] = j.price
                variant_temp['stock'] = j.stock
                temp['variants'].append(variant_temp)
            product_list.append(temp)
        variants = Variant.objects.filter(active = True)
        all_variants = []
        for i in variants:
            temp = {}
            temp['title'] = i.title
            temp['values'] = ProductVariant.objects.filter(variant_id = i.id).only('variant_title').values_list('variant_title',flat=True).distinct()
            all_variants.append(temp)
        context['product'] = True
        context['is_paginated'] = True
        context['products'] = pag_item
        context['all_products'] = product_list
        context['all_variants'] = all_variants
        return context

@method_decorator(csrf_exempt, name='dispatch')
class ProductEditView(generic.TemplateView):
    template_name = 'products/edit.html'

    def get_context_data(self,id, **kwargs):
        context = super(ProductEditView, self).get_context_data(**kwargs)
        variants = Variant.objects.filter(active=True).values('id', 'title')
        print(variants)
        product_object = Product.objects.get(id=id)
        context['product'] = True
        context['variants'] = list(variants.all())
        context['product_id'] = product_object.id
        context['product_obj_name'] = product_object.title
        context['product_obj_sku'] = product_object.sku
        context['product_obj_description'] = product_object.description
        # variants_temp = ProductVariant.objects.select_related('variant').filter(product_id=id).values('variant_id','variant_title')
        # for i in variants_temp:
        context['current_variants'] = [{'option':1,'tags':['a','b']}]

        return context

    def put(self,request,id):
        response_ = request.body
        r = ast.literal_eval(response_.decode('utf-8'))
        product_title = r.get('title')
        product_sku = r.get('sku')
        product_description = r.get('description')

        product_object = Product.objects.get(id=id)
        product_object.title = product_title
        product_object.sku = product_sku
        product_object.description = product_description
        product_object.save()
        return redirect('product:list.product')

