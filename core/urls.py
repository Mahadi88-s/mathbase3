from django.urls import path
from . import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.contrib.sitemaps.views import sitemap

urlpatterns = [
    path('', views.homepage, name='homepage'),
    path('index', views.index, name='index'),
    path('pcomp', views.pcomp, name='pcomp'),

    #api
    path('paper1/<api>', views.paper1),
    path('paper2/<api>', views.paper2),
    path('paper3/<api>', views.paper3),

    path('paper1/<int:id>/<int:pk>/<api>', views.paper1details),
    path('paper2/<int:id>/<int:pk>/<api>', views.paper2details),
    path('paper3/<int:id>/<int:pk>/<api>', views.paper3details),

    #p1
    path('paper1maths', views.paper1maths, name='paper1maths'),
    path('analysisp1', views.analysisp1, name='analysisp1'),
    path('upload_top1', views.upload_top1, name='upload_top1'),

    #p2
    path('paper2maths', views.paper2maths, name='paper2maths'),
    path('analysisp2', views.analysisp2, name='analysisp2'),
    path('upload_top2', views.upload_top2, name='upload_top2'),

    #p2
    path('paper3maths', views.paper3maths, name='paper3maths'),
    path('analysisp3', views.analysisp3, name='analysisp3'),
    path('upload_top3', views.upload_top3, name='upload_top3'),

    #ocr as
    #p1
    path('asocran1', views.asocran1, name='asocran1'),
    path('p1asocr', views.p1asocr, name='p1asocr'),
    path('upasocr1', views.upasocr1, name='upasocr1'),

    #p2
    path('asocran2', views.asocran2, name='asocran2'),
    path('p2asocr', views.p2asocr, name='p2asocr'),
    path('upasocr2', views.upasocr2, name='upasocr2'),

    path('upload_as_ocr', views.upload_as_ocr, name='upload_as_ocr'),

    path('upload', views.upload, name='upload'),
    path('search_all', views.search_all, name='search_all'),
    path('search_all_ocras', views.search_all_ocras, name='search_all_ocras'),


    path('profile', views.profile, name='profile'),
    path('signin', views.signin, name='signin'),
    path('logout', views.logout, name='logout'),
    path('signup', views.signup, name='signup'),

    path('ai', views.ai, name='ai'),
    path('ai-ex', views.ai_ex, name='ai-ex'),
    path('ai_exam_', views.ai_exam_, name='ai_exam_'),

    path('ai_site', views.ai_site, name='ai_site'),
    path('ai_exercises', views.ai_exercises, name='ai_exercises'),
    path('ai_exam', views.ai_exam, name='ai_exam'),

    path('search', views.search, name='search'),

    path('library', views.library, name='library'),
    path('delete_pdf/<int:pdf_id>/', views.delete_pdf, name='delete_pdf'),
    path('download_pdf/<int:pdf_id>/', views.download_pdf, name='download_pdf'),

    path('like', views.like, name='like'),
    path('map', views.map, name='map'),

    #path('ads.txt', views.ads, name='ads.txt'),
]

urlpatterns = format_suffix_patterns(urlpatterns)