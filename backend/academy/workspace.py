from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Lesson,LessonNote,Enrollment,LessonBookmark,ProjectSubmission

@api_view(['GET'])
def search(request):
    query=request.query_params.get('q','').strip()
    if not 2<=len(query)<=100:return Response({'detail':'Search with 2–100 characters.'},status=400)
    enrolled=Enrollment.objects.filter(user=request.user).values('program_id')
    notes=LessonNote.objects.filter(user=request.user,text__icontains=query,lesson__program_id__in=enrolled).exclude(lesson__program__category='Archive')
    note_map={row.lesson_id:row.text for row in notes}
    rows=Lesson.objects.filter(program_id__in=enrolled).exclude(program__category='Archive').filter(Q(title__icontains=query)|Q(module__icontains=query)|Q(content__icontains=query)|Q(id__in=note_map)).select_related('program')[:30]
    results=[]
    for row in rows:
        source=note_map.get(row.pk,row.content)
        position=source.casefold().find(query.casefold())
        start=max(0,position-70)
        results.append({'lesson':row.pk,'program':row.program.slug,'program_title':row.program.title,'title':row.title,'module':row.module,'snippet':source[start:start+230].replace('#','').replace('`',''),'match':'Private note' if row.pk in note_map else 'Lesson'})
    return Response(results)

@api_view(['GET','POST','DELETE'])
def bookmarks(request,pk=None):
    if pk is not None:
        lesson=get_object_or_404(Lesson,pk=pk)
        if not Enrollment.objects.filter(user=request.user,program=lesson.program).exists():return Response({'detail':'Enroll in this program first.'},status=403)
        if request.method=='POST':LessonBookmark.objects.get_or_create(user=request.user,lesson=lesson)
        elif request.method=='DELETE':LessonBookmark.objects.filter(user=request.user,lesson=lesson).delete()
        else:return Response({'detail':'Use the bookmark list endpoint.'},status=405)
    return Response([{'lesson':row.lesson_id,'program':row.lesson.program.slug,'program_title':row.lesson.program.title,'title':row.lesson.title} for row in LessonBookmark.objects.filter(user=request.user).exclude(lesson__program__category='Archive').select_related('lesson__program').order_by('-created_at')])

@api_view(['GET'])
def portfolio(request):
    rows=ProjectSubmission.objects.filter(user=request.user).select_related('lesson__program','reviewer')[:100]
    return Response([{'id':row.pk,'program':row.lesson.program.title,'title':row.lesson.title,'artifact_url':row.artifact_url,'commit':row.commit,'evidence':row.evidence,'measurements':row.measurements,'status':row.review_status,'feedback':row.review_feedback,'reviewer':row.reviewer.username if row.reviewer else None,'created_at':row.created_at} for row in rows])
