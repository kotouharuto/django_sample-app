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
from sample_app.models import Post
from django.shortcuts import render, get_object_or_404, redirect
import requests
from django.forms import ModelForm
from django.http import HttpResponse


def recommend_form(request):
  """
  新たなデータを作成する
  """
  if request.method == 'POST':
    return HttpResponse('POSTリクエストが処理されました。')
  elif request.method == 'GET':
    return render(request, 'sample_app/recommend_form.html')

def recommend(request):
 ikea_admin = IkeaAdmin()
 from sklearn.feature_extraction.text import TfidfVectorizer, CountVectorizer
 from sklearn.metrics.pairwise import cosine_similarity
 from scipy.sparse import hstack
 import warnings
 warnings.filterwarnings('ignore')

 import pandas as pd
 import numpy as np
 data = ikea_admin.list_display

 # Unnamed: 0は不要なので削除する
 data.drop(['Unnamed: 0'], axis=1, inplace=True)

 df = data.copy()
 df = df.dropna()

 """データ加工"""
 df = df.rename(columns={'item_id': 'product_id', 'name': 'product_name', 'category': 'product_category', 'link': 'product_link', 'short_description': 'product_description'})

 if '30180504' in df['product_id'].astype(str).values:
   print('Value found in DataFrame.')
 else:
   print('Value not found in DataFrame.')

 df = df.set_index('product_id')

 """レコメンド実装"""

 product_description = df['product_description']
 product_category = df['product_category']
 product_names = df['product_name']
 product_link = df['product_link']

 tfidf_vectorizer = TfidfVectorizer(stop_words='english')
 count_vectorizer = CountVectorizer(stop_words='english')

 tfidf_matrix = tfidf_vectorizer.fit_transform(product_description)
 category_matrix_weight = 2

 count_matrix_category = count_vectorizer.fit_transform(category_matrix_weight * product_category)
 count_matrix_name = count_vectorizer.fit_transform(product_names)
 count_matrix = hstack([count_matrix_category, count_matrix_name])

 # 2つのmatrixを結合
 combined_similarity_matrix = cosine_similarity(hstack([tfidf_matrix, count_matrix]))

 def get_related_products(product_id, num_products=25):
   if product_id not in df.index:
     print(f'{product_id}がリストに存在しません。')
     return None
   idx = df.index.get_loc(product_id)
   # コサイン類似度のスコアを取得
   sim_scores = list(enumerate(combined_similarity_matrix[idx]))
   sim_indices = [i[0] for i in sim_scores[1:num_products+1]]

   return df.iloc[sim_indices][['product_category', 'product_name', 'product_description', 'product_link']]

 related_products = get_related_products(70404875)
 return related_products