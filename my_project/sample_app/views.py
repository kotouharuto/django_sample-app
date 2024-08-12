# ライブラリ等のインポート
from django.shortcuts import render
import numpy as np
import pandas as pd
import os
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from scipy.sparse import hstack
import warnings
warnings.filterwarnings('ignore')
from sample_app.admin import IkeaResource
from sample_app.admin import IkeaAdmin
from sample_app.models import Post, Ikea
from django.shortcuts import render, get_object_or_404, redirect
import requests
from django.forms import ModelForm
from django.http import HttpResponse
import requests
from bs4 import BeautifulSoup
import random
from IPython.display import Image, display
from django.db.models import Count

def recommend_form(request):
  # データベースからすべてのリンクを取得
    all_products = list(Ikea.objects.all())
    random.shuffle(all_products)  # リストをシャッフルしてランダム化

    product_images = []
    selected_links = []

    for product in all_products:
        if len(selected_links) >= 15:
            break
        
        url = product.link  # 'item_link'の代わりに'link'を使用
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tag = soup.find('img', class_='pip-image')
            if img_tag:
                image_url = img_tag.get('src')
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                product_images.append({
                  'link': url,
                  'image_url': image_url
                })
                selected_links.append(url)
        except requests.RequestException as e:
            print(f"Error fetching the URL: {e}")

    context = {'product_images': product_images}
    return render(request, 'sample_app/recommend_form.html', context)

def recommend(request):
    """必要ライブラリのインポート"""
    from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
    from scipy.sparse import hstack
    import warnings
    warnings.filterwarnings('ignore')
    from .models import Ikea

    """item_idをスクレイピングで取得"""
    link = request.GET.get('link')
    if not link:
        return render(request, 'sample_app/error.html', {'message': 'リンクが提供されていません。'})

    # デバッグ用にリンクを出力
    print(f'Provided link: {link}')

    try:
        response = requests.get(link)
        response.raise_for_status()  # HTTPエラーが発生した場合に例外を送出
    except requests.RequestException as e:
        return render(request, 'sample_app/error.html', {'message': f'リンクの取得中にエラーが発生しました: {e}'})

    soup = BeautifulSoup(response.content, 'html.parser')
    identifier = soup.find('span', class_='pip-product-identifier__value')
    if identifier:
        identifier_value = identifier.text.strip().replace('.', '')
        if identifier_value[0] == '0':
            identifier_value = identifier_value.replace('0', '')
        if len(identifier_value) < 6:
            identifier_value = f"{identifier_value}00"
        print(f'Product Identifier: {identifier_value}')
    else:
        return render(request, 'sample_app/error.html', {'message': '商品識別子が見つかりませんでした。'})

    data = Ikea.objects.all().values('item_id', 'name', 'category', 'link', 'short_description')
    df = pd.DataFrame(list(data))

    print(df.head())
    df['item_id'] = df['item_id'].astype(str)

    df.set_index('item_id', inplace=True)

    if identifier_value not in df.index:
        return render(request, 'sample_app/error.html', {'message': '指定された商品がデータベースに存在しません。'})

    product_description = df['short_description']
    product_category = df['category']
    product_names = df['name']

    tfidf_vectorizer = TfidfVectorizer(stop_words='english')
    count_vectorizer = CountVectorizer(stop_words='english')

    tfidf_matrix = tfidf_vectorizer.fit_transform(product_description)
    category_matrix = count_vectorizer.fit_transform(product_category).multiply(2)
    count_matrix_name = count_vectorizer.fit_transform(product_names)
    combined_matrix = hstack([tfidf_matrix, category_matrix, count_matrix_name])

    combined_similarity_matrix = cosine_similarity(combined_matrix)

    def get_related_products(product_id, num_products=25):
        if product_id not in df.index:
            print(f'{product_id}がリストに存在しません。')
            return None
        idx = df.index.get_loc(product_id)
        sim_scores = list(enumerate(combined_similarity_matrix[idx]))
        sim_scores = sorted(sim_scores, key=lambda x: x[1], reverse=True)
        print(sim_scores)
        print(type(sim_scores))
        sim_indices = [i[0] for i in sim_scores[1:num_products+1]]

        return df.iloc[sim_indices][['category', 'name', 'short_description', 'link']].to_dict(orient='records')

    related_products = get_related_products(identifier_value)

    if related_products is None:
        return render(request, 'sample_app/error.html', {'message': '関連商品が見つかりませんでした。'})

    related_products_images = []
    for product in related_products:
        url = product['link']
        print(url)
        try:
            response = requests.get(url)
            response.raise_for_status()
            soup = BeautifulSoup(response.content, 'html.parser')
            img_tag = soup.find('img', class_='pip-image')
            if img_tag:
                image_url = img_tag.get('src')
                if image_url.startswith('//'):
                    image_url = 'https:' + image_url
                related_products_images.append({
                    'link': url,
                    'image_url': image_url,
                    'category': product['category'],
                    'name': product['name'],
                    'short_description': product['short_description']
                })
        except requests.RequestException as e:
            print(f"Error fetching the URL: {e}")

    context = {'product_images': related_products_images}  # ここを修正
    return render(request, 'sample_app/recommend.html', context)


def home(request):
    return render(request, 'sample_app/home.html')